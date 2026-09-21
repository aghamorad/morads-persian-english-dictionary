#!/usr/bin/env python3
"""Merge open Persian lexicons into Kindle dictionary source files."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from extract_apple import extract_body


ZWNJ = "\u200c"
ZWJ = "\u200d"
TATWEEL = "\u0640"
PERSIAN_RUN = re.compile(r"[\u0600-\u06ff\u200c\u200d]+(?:[ -][\u0600-\u06ff\u200c\u200d]+)*")
HMT_ENTRY = re.compile(r'<d:entry\b[^>]*?d:title="(.*?)"[^>]*>(.*?)</d:entry>', re.S)
SOURCE_PRIORITY = {"Wiktionary": 0, "Dehkhoda-Lexicon": 1, "HMT": 2}
DISPLAY_TRANSLATION = str.maketrans({
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
    "ۀ": "ه",
    "ة": "ه",
    "إ": "ا",
    "أ": "ا",
    "ٱ": "ا",
})
PERSIAN_TO_ARABIC = str.maketrans({"ی": "ي", "ک": "ك"})
NAVIGATION_TEXT = (
    "درباره این فرهنگ لغت",
    "مشاهده کلمات مرتبط",
)


@dataclass
class LexiconEntry:
    key: str
    headword: str
    headword_score: tuple[int, int, int, str]
    definitions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    parts_of_speech: set[str] = field(default_factory=set)
    spellings: set[str] = field(default_factory=set)
    forms: set[str] = field(default_factory=set)


def raw_word(text: str) -> str:
    text = html.unescape(unicodedata.normalize("NFKC", text))
    text = text.replace(TATWEEL, "").replace(ZWJ, "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_word(text: str) -> str:
    return raw_word(text).translate(DISPLAY_TRANSLATION)


def strip_zero_weight(text: str) -> str:
    text = raw_word(text).replace(ZWNJ, "")
    return "".join(character for character in text if unicodedata.category(character) != "Mn")


def merge_key(text: str) -> str:
    text = normalize_word(text).replace(ZWNJ, "")
    return "".join(character for character in text if unicodedata.category(character) != "Mn")


def index_key(text: str) -> str:
    return strip_zero_weight(text)


def valid_word(text: str) -> bool:
    if not text or len(text) > 80:
        return False
    has_letter = False
    for character in text:
        if character in {" ", "-", ZWNJ} or unicodedata.category(character) == "Mn":
            continue
        if "\u0600" <= character <= "\u06ff" and unicodedata.category(character).startswith(("L", "N")):
            has_letter = has_letter or unicodedata.category(character).startswith("L")
            continue
        return False
    return has_letter


def index_label(text: str) -> str:
    return raw_word(text).replace(ZWNJ, "")


def clean_definition(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n,;/")
    return text


def get_entry(entries: dict[str, LexiconEntry], word: str, source: str) -> LexiconEntry | None:
    source_spelling = raw_word(word)
    normalized = normalize_word(source_spelling)
    if not valid_word(normalized):
        return None
    key = merge_key(normalized)
    score = (
        SOURCE_PRIORITY[source],
        sum(unicodedata.category(character) == "Mn" for character in normalized),
        len(normalized),
        normalized,
    )
    entry = entries.get(key)
    if entry is None:
        entry = LexiconEntry(key=key, headword=normalized, headword_score=score)
        entries[key] = entry
    elif score < entry.headword_score:
        entry.headword = normalized
        entry.headword_score = score
    entry.spellings.add(source_spelling)
    entry.spellings.add(normalized)
    return entry


def add_definition(entry: LexiconEntry, source: str, definition: str) -> None:
    definition = clean_definition(definition)
    if not definition:
        return
    existing = {item.casefold() for item in entry.definitions[source]}
    if definition.casefold() not in existing:
        entry.definitions[source].append(definition)


def load_kaikki(path: Path, entries: dict[str, LexiconEntry]) -> None:
    with path.open(encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            entry = get_entry(entries, record.get("word", ""), "Wiktionary")
            if entry is None:
                continue
            part_of_speech = record.get("pos")
            if part_of_speech:
                entry.parts_of_speech.add(part_of_speech)
            for sense in record.get("senses", []):
                for gloss in sense.get("glosses", []):
                    add_definition(entry, "Wiktionary", gloss)
            for form_record in record.get("forms", []):
                tags = set(form_record.get("tags", []))
                if tags & {"romanization", "table-tags", "inflection-template"}:
                    continue
                for form in PERSIAN_RUN.findall(form_record.get("form", "")):
                    if valid_word(normalize_word(form)):
                        entry.forms.add(raw_word(form))


def load_dehkhoda(path: Path, entries: dict[str, LexiconEntry]) -> None:
    for record in json.loads(path.read_text(encoding="utf-8")):
        for line in record.get("output", "").splitlines():
            if ":" not in line:
                continue
            word, definition = line.split(":", 1)
            entry = get_entry(entries, word, "Dehkhoda-Lexicon")
            if entry is not None:
                add_definition(entry, "Dehkhoda-Lexicon", definition)


def hmt_plain_text(body: str, headword: str) -> str:
    body = re.sub(r"<(?:script|style)\b.*?</(?:script|style)>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<(?:br|/p|/div|/li|/dd|/dt)\s*/?>", "; ", body, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    text = clean_definition(body)
    for phrase in NAVIGATION_TEXT:
        text = text.replace(phrase, " ")
    text = clean_definition(text)
    if text.startswith(headword):
        text = clean_definition(text[len(headword):])
    if not re.search(r"[A-Za-z]", text):
        return ""
    return text[:1600].rstrip(" ,;/")


def load_hmt(path: Path, entries: dict[str, LexiconEntry]) -> None:
    for chunk in extract_body(path):
        match = HMT_ENTRY.search(chunk)
        if match is None:
            continue
        source_title = html.unescape(match.group(1)).strip()
        if source_title.startswith("@"):
            continue
        entry = get_entry(entries, source_title, "HMT")
        if entry is None:
            continue
        definition = hmt_plain_text(match.group(2), entry.headword)
        if definition:
            add_definition(entry, "HMT", definition)


def generated_aliases(entry: LexiconEntry) -> set[str]:
    word = entry.headword
    aliases = set(entry.spellings) | set(entry.forms)
    aliases.add(word.translate(PERSIAN_TO_ARABIC))
    if ZWNJ in word:
        aliases.add(word.replace(ZWNJ, " "))
    if word.endswith("ه"):
        aliases.add(word[:-1] + "ۀ")
        aliases.add(word + "ٔ")
    if word.endswith("ی"):
        aliases.add(word[:-1] + "ى")
    if " " not in word and "-" not in word and len(word.replace(ZWNJ, "")) >= 2:
        stem = word.replace(ZWNJ, "")
        for suffix in ("ی", "ها", "های", "م", "ت", "ش", "مان", "تان", "شان"):
            aliases.add(stem + suffix)
        if stem.endswith(("ه", "ا", "و", "ی")):
            for suffix in ("ام", "ات", "اش"):
                aliases.add(stem + suffix)
        if not stem.endswith(("ا", "و")):
            # The plural carries its own indefinite: کتابهایی. Not added for vowel-final stems.
            aliases.add(stem + "هایی")
            for possessive in ("م", "ت", "ش"):
                # Only the singular possessives. کتابهایمان and its siblings are six more
                # labels per entry for forms a reader almost never types; they cost far
                # more index than they return.
                aliases.add(stem + "های" + possessive)
        if stem.endswith("ه"):
            # The space-separated indefinite is its own on-device label: the device folds
            # ZWNJ away before searching, so خانهای and خانهای collapse, but خانه ای does not.
            aliases.add(stem + " ای")
            aliases.add(stem + " ی")
        if "adj" in entry.parts_of_speech:
            aliases.add(stem + "تر")
            aliases.add(stem + "ترین")
    return {index_label(alias) for alias in aliases if valid_word(index_label(alias))}


def assign_aliases(entries: dict[str, LexiconEntry]) -> tuple[dict[str, list[str]], int]:
    canonical_owners = {index_key(index_label(entry.headword)): entry.key for entry in entries.values()}
    alias_owners: dict[str, str] = {}
    assigned: dict[str, list[str]] = {}
    conflicts = 0
    for entry in sorted(entries.values(), key=lambda item: item.headword):
        aliases = []
        for alias in sorted(generated_aliases(entry)):
            primary_label = index_label(entry.headword)
            if alias == primary_label:
                continue
            # Conflicts are judged by on-device index identity, not by the display-folded
            # merge key: مسأله folds to مساله for display, but the device matches them as
            # distinct strings, so a recorded form like مسأله belongs on its own entry.
            alias_index_key = index_key(alias)
            canonical_owner = canonical_owners.get(alias_index_key)
            if canonical_owner is not None and canonical_owner != entry.key:
                conflicts += 1
                continue
            alias_owner = alias_owners.get(alias_index_key)
            if alias_owner is not None and alias_owner != entry.key:
                conflicts += 1
                continue
            if alias_index_key == index_key(primary_label) and not alias.endswith("ٔ"):
                continue
            alias_owners[alias_index_key] = entry.key
            aliases.append(alias)
        assigned[entry.key] = aliases
    return assigned, conflicts


def source_block(source: str, definitions: list[str]) -> str:
    items = "".join(f"<li>{html.escape(definition)}</li>" for definition in definitions[:16])
    return (
        f'<section class="source"><h2>{html.escape(source)}</h2>'
        f'<ol dir="ltr" lang="en">{items}</ol></section>'
    )


def kindle_entry(number: int, entry: LexiconEntry, aliases: list[str]) -> str:
    headword = html.escape(index_label(entry.headword), quote=True)
    orth = [f'<idx:orth value="{headword}"><b>{html.escape(entry.headword)}</b>']
    if aliases:
        orth.append("<idx:infl>")
        orth.extend(
            f'<idx:iform value="{html.escape(alias, quote=True)}" exact="yes"/>'
            for alias in aliases
        )
        orth.append("</idx:infl>")
    orth.append("</idx:orth>")
    sources = "".join(
        source_block(source, entry.definitions[source])
        for source in ("Wiktionary", "HMT", "Dehkhoda-Lexicon")
        if entry.definitions.get(source)
    )
    parts = ""
    if entry.parts_of_speech:
        parts = f'<p class="pos" dir="ltr">{html.escape(", ".join(sorted(entry.parts_of_speech)))}</p>'
    return (
        f'<idx:entry name="default" scriptable="yes" spell="yes"><a id="e{number}"></a>'
        + "".join(orth)
        + f'<article><h1>{html.escape(entry.headword)}</h1>{parts}{sources}</article></idx:entry>\n'
    )


def write_opf(root: Path) -> None:
    (root / "content.opf").write_text('''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Morad's Persian–English Dictionary</dc:title>
    <dc:language>fa</dc:language>
    <dc:creator opf:role="aut">Morad Moazami</dc:creator>
    <dc:identifier id="bookid">morads-persian-english-dictionary-2026</dc:identifier>
    <dc:description>Persian to English dictionary merged from HMT, Wiktionary, and Dehkhoda-Lexicon with Kindle-aware spelling lookup.</dc:description>
    <meta name="cover" content="cover-image"/>
    <x-metadata>
      <DictionaryInLanguage>fa</DictionaryInLanguage>
      <DictionaryOutLanguage>en</DictionaryOutLanguage>
    </x-metadata>
  </metadata>
  <manifest>
    <item id="main" href="dictionary.html" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="cover-image" href="cover.png" media-type="image/png"/>
    <item id="css" href="style.css" media-type="text/css"/>
  </manifest>
  <spine toc="ncx"><itemref idref="main"/></spine>
  <guide><reference type="index" title="Dictionary" href="dictionary.html"/></guide>
</package>
''', encoding="utf-8")
    (root / "toc.ncx").write_text('''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="morads-persian-english-dictionary-2026"/></head>
  <docTitle><text>Morad's Persian–English Dictionary</text></docTitle>
  <navMap><navPoint id="dictionary" playOrder="1"><navLabel><text>Dictionary</text></navLabel><content src="dictionary.html"/></navPoint></navMap>
</ncx>
''', encoding="utf-8")


def write_source(root: Path, cover: Path, entries: dict[str, LexiconEntry]) -> dict[str, int]:
    root.mkdir(parents=True, exist_ok=True)
    aliases, conflicts = assign_aliases(entries)
    usable_entries = [entry for entry in entries.values() if any(entry.definitions.values())]
    usable_entries.sort(key=lambda entry: entry.headword)
    rendered = [kindle_entry(number, entry, aliases[entry.key]) for number, entry in enumerate(usable_entries, 1)]
    document = '''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:idx="http://www.mobipocket.com/iBook/index-2.0" xmlns:mbp="http://www.mobipocket.com">
<head><title>Morad's Persian–English Dictionary</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body dir="rtl"><mbp:frameset>''' + "".join(rendered) + "</mbp:frameset></body></html>\n"
    (root / "dictionary.html").write_text(document, encoding="utf-8")
    (root / "style.css").write_text(
        "body{font-family:serif;line-height:1.35}article{margin:.2em 0 .9em}h1{font-size:1.25em;margin:.1em 0}h2{font-size:.8em;margin:.5em 0 .1em;color:#666}.pos{font-size:.8em;color:#666;margin:.1em 0}ol{margin:.15em 0 .35em;padding-left:1.4em}li{margin:.08em 0}idx\\:orth{font-weight:bold}",
        encoding="utf-8",
    )
    shutil.copy2(cover, root / "cover.png")
    write_opf(root)
    stats = {
        "entries": len(usable_entries),
        "aliases": sum(len(aliases[entry.key]) for entry in usable_entries),
        "alias_conflicts_skipped": conflicts,
        "wiktionary_entries": sum(bool(entry.definitions.get("Wiktionary")) for entry in usable_entries),
        "hmt_entries": sum(bool(entry.definitions.get("HMT")) for entry in usable_entries),
        "dehkhoda_entries": sum(bool(entry.definitions.get("Dehkhoda-Lexicon")) for entry in usable_entries),
    }
    (root.parent / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hmt-body", type=Path, required=True)
    parser.add_argument("--dehkhoda", type=Path, required=True)
    parser.add_argument("--kaikki", type=Path, required=True)
    parser.add_argument("--cover", type=Path, default=Path("build/cover.png"))
    parser.add_argument("--out", type=Path, default=Path("build/source"))
    args = parser.parse_args()
    entries: dict[str, LexiconEntry] = {}
    load_kaikki(args.kaikki, entries)
    load_dehkhoda(args.dehkhoda, entries)
    load_hmt(args.hmt_body, entries)
    stats = write_source(args.out, args.cover, entries)
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

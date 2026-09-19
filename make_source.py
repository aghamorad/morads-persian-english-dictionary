#!/usr/bin/env python3
"""Turn extracted Apple Dictionary XML into Kindle dictionary source files."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ARABIC_TO_PERSIAN = str.maketrans({
    "ي": "ی", "ى": "ی", "ك": "ک", "ۀ": "هٔ", "ة": "ه",
    "ؤ": "ؤ", "إ": "ا", "أ": "ا", "ٱ": "ا",
})
PERSIAN_TO_ARABIC = str.maketrans({
    "ی": "ي", "ک": "ك", "گ": "گ", "پ": "پ", "چ": "چ", "ژ": "ژ",
})
ZWNJ = "\u200c"
ZWJ = "\u200d"
TATWEEL = "\u0640"
FA_LETTER = re.compile(r"[\u0600-\u06ff]")
WORD = re.compile(r"^[\u0600-\u06ff][\u0600-\u06ff\u200c\u200d\u064b-\u065f\u0670-\u06ef]*$")


def clean_title(title: str) -> str:
    title = html.unescape(title)
    return re.sub(r"\s+", " ", title.replace(TATWEEL, "")).strip()


def variants(word: str) -> set[str]:
    """Return conservative lookup aliases, keeping the original as primary."""
    out = {word}
    plain = word.replace(ZWNJ, "").replace(ZWJ, "")
    out.add(plain)
    out.add(word.replace(ZWNJ, " "))
    out.add(word.replace(ZWNJ, ""))
    out.add(word.translate(ARABIC_TO_PERSIAN))
    out.add(plain.translate(ARABIC_TO_PERSIAN))
    out.add(word.translate(PERSIAN_TO_ARABIC))
    out.add(plain.translate(PERSIAN_TO_ARABIC))
    out.add(word.replace("هٔ", "ة").translate(PERSIAN_TO_ARABIC))
    out.add(plain.replace("هٔ", "ة").translate(PERSIAN_TO_ARABIC))
    if WORD.match(word) and len(plain) >= 2:
        # Common attached Persian morphology and clitics. These are aliases,
        # not separate fabricated definitions.
        stems = {word, plain, word.translate(PERSIAN_TO_ARABIC), plain.translate(PERSIAN_TO_ARABIC)}
        for suffix in ("ها", "های", "تر", "ترین", "ی", "ام", "ات", "اش", "مان", "تان", "شان"):
            for stem in stems:
                out.add(stem + suffix)
                out.add(stem + ZWNJ + suffix)
        for prefix in ("می", "نمی"):
            for stem in stems:
                out.add(prefix + stem)
                out.add(prefix + ZWNJ + stem)
    # Ezafeh is often typed with a kasra, a hyphen, or a space before e.
    if WORD.match(word):
        out.add(word + "ِ")
        out.add(word + " ـِ")
        out.add(word + "-e")
    return {v.strip() for v in out if v.strip() and v != word}


def entries(xml: str):
    pattern = re.compile(r'<d:entry\b[^>]*?d:title="(.*?)"[^>]*>(.*?)</d:entry>', re.S)
    for match in pattern.finditer(xml):
        title = clean_title(match.group(1))
        body = match.group(2)
        if title:
            yield title, body


def kindle_entry(number: int, title: str, body: str) -> str:
    aliases = sorted(variants(title), key=lambda x: (len(x), x))
    orth = [f'<idx:orth value="{html.escape(title, quote=True)}"><b>{html.escape(title)}</b>']
    if aliases:
        orth.append("<idx:infl>")
        for alias in aliases:
            orth.append(f'<idx:iform value="{html.escape(alias, quote=True)}" exact="yes"/>')
        orth.append("</idx:infl>")
    orth.append("</idx:orth>")
    # Remove Apple-only wrapper elements while retaining readable inner HTML.
    body = re.sub(r"\s+d:(?:def|ex)=[^>]*", "", body)
    body = body.replace("<d:def></d:def>", "")
    return f'<idx:entry name="default" scriptable="yes" spell="yes"><a id="e{number}"/>' + "".join(orth) + body + "</idx:entry>\n"


def write_opf(root: Path, count: int) -> None:
    (root / "content.opf").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Morad's Persian–English Dictionary</dc:title>
    <dc:language>fa</dc:language>
    <dc:creator opf:role="aut">Morad Moazami</dc:creator>
    <dc:identifier id="bookid">persian-english-wiktionary-2026</dc:identifier>
    <dc:description>Persian to English dictionary with robust Persian spelling and attachment lookup.</dc:description>
    <meta name="DictionaryInLanguage" content="fa"/>
    <meta name="DictionaryOutLanguage" content="en"/>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="main" href="dictionary.html" media-type="application/xhtml+xml"/>
    <item id="cover-image" href="cover.png" media-type="image/png"/>
    <item id="css" href="style.css" media-type="text/css"/>
  </manifest>
  <spine toc="ncx"><itemref idref="main"/></spine>
</package>
''', encoding="utf-8")
    (root / "style.css").write_text("body{font-family:serif;} h1{font-size:1.35em;} .subentry{margin:.35em 0 .8em;} idx\\:orth{font-weight:bold;}", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    parts = []
    count = 0
    for count, (title, body) in enumerate(entries(args.xml.read_text(encoding="utf-8")), 1):
        parts.append(kindle_entry(count, title, body))
    document = '''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:idx="http://www.mobipocket.com/iBook/index-2.0">
<head><title>Morad's Persian–English Dictionary</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body dir="rtl">''' + "".join(parts) + "</body></html>\n"
    (args.out / "dictionary.html").write_text(document, encoding="utf-8")
    write_opf(args.out, count)
    print(f"wrote {count:,} dictionary entries to {args.out}")


if __name__ == "__main__":
    main()

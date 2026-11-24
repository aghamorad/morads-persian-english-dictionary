#!/usr/bin/env python3
"""Export Morad's Persian-English Dictionary to a native Apple Dictionary bundle.

Reads the same published web data shards (entries + lookup index) that
export_web.py produces, and emits Apple Dictionary Development Kit XML plus the
plist and CSS needed to compile a .dictionary bundle with build_dict.sh.

Only canonical headwords are indexed as titles; every searchable lookup alias in
the index (spelling variants, attached suffixes, ezafeh, plurals, possessives) is
added as a d:index so Dictionary.app and system-wide Look Up can find each form.
"""
from __future__ import annotations

import argparse
import html
import json
import plistlib
from collections import defaultdict
from pathlib import Path
import sys

XML_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" '
    'xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">\n'
)
XML_FOOTER = "</d:dictionary>\n"

CSS = """
body {
    font-family: -apple-system, "Noto Naskh Arabic", Tahoma, sans-serif;
    direction: rtl;
    text-align: right;
}
h1 {
    font-size: 1.5em;
    font-weight: 700;
    margin: 0 0 0.25em;
    direction: rtl;
    unicode-bidi: embed;
}
p.pos {
    color: #6b7b70;
    font-size: 0.78em;
    margin: 0 0 0.8em;
    direction: rtl;
}
div.source {
    margin: 0.6em 0 0;
    border-top: 1px solid #e3e4de;
    padding-top: 0.45em;
}
div.source h3 {
    margin: 0 0 0.35em;
    color: #6b7b70;
    font-size: 0.72em;
    font-weight: 600;
    letter-spacing: 0.04em;
}
ol {
    margin: 0;
    padding: 0 1.4em 0 0;
    line-height: 1.7;
    direction: rtl;
}
li { padding: 0 0 0.35em; }
"""


def load_shards(shard_dir: Path) -> dict[str, dict]:
    """Merge every *.json shard in a directory into one dict."""
    merged: dict[str, dict] = {}
    for path in sorted(shard_dir.glob("*.json")):
        merged.update(json.loads(path.read_text(encoding="utf-8")))
    return merged


def build(entries_dir: Path, index_dir: Path, out: Path, version: str = "1.3.0") -> dict:
    entries = load_shards(entries_dir)
    index = load_shards(index_dir)

    # Reverse index: target merge-key -> list of searchable lookup strings
    aliases_for: dict[str, set[str]] = defaultdict(set)
    for term, target in index.items():
        aliases_for[target].add(term)

    out.mkdir(parents=True, exist_ok=True)
    xml_path = out / "Morads-Dictionary.xml"
    with xml_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(XML_HEADER)
        for n, (key, entry) in enumerate(sorted(entries.items()), 1):
            word = entry["word"]
            pos = entry.get("pos", [])
            sources = entry.get("sources", {})
            eword = html.escape(word, quote=True)
            f.write(f'<d:entry id="pde_{n:06d}" d:title="{eword}">')
            # index the canonical headword and every searchable alias
            f.write(f'<d:index d:value="{eword}"/>')
            for alias in sorted(aliases_for.get(key, set())):
                if alias == word:
                    continue
                ealias = html.escape(alias, quote=True)
                f.write(f'<d:index d:value="{ealias}"/>')
            f.write(f"<h1>{eword}</h1>")
            if pos:
                f.write(f'<p class="pos">{html.escape(", ".join(sorted(pos)), quote=True)}</p>')
            for source in ("Wiktionary", "Editorial", "HMT", "Dehkhoda-Lexicon"):
                defs = sources.get(source)
                if not defs:
                    continue
                f.write(f'<div class="source"><h3>{html.escape(source, quote=True)}</h3><ol>')
                for d in defs:
                    f.write(f"<li>{html.escape(d, quote=True)}</li>")
                f.write("</ol></div>")
            f.write("</d:entry>\n")
        f.write(XML_FOOTER)

    meta = {
        "CFBundleDevelopmentRegion": "fa",
        "CFBundleIdentifier": "org.morads.dictionary.persian-english",
        "CFBundleName": "Morad's Persian-English Dictionary",
        "CFBundleShortVersionString": version,
        "DCSDictionaryCopyright": (
            "Data: HMT (MIT), Wiktionary/Kaikki (CC BY-SA 4.0 / GFDL), "
            "Dehkhoda-Lexicon by Maani (CC BY-SA 4.0). Compiled by Morad."
        ),
        "DCSDictionaryManufacturerName": "Morad",
        "DCSDictionaryUseSystemAppearance": True,
    }
    with (out / "Morads.plist").open("wb") as f:
        plistlib.dump(meta, f, fmt=plistlib.FMT_XML)
    (out / "Morads.css").write_text(CSS.lstrip(), encoding="utf-8")

    stats = {
        "entries": len(entries),
        "lookup_terms": len(index),
        "indexed_aliases": sum(len(v) for v in aliases_for.values()),
        "version": version,
    }
    (out / "statistics.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entries", type=Path, required=True, help="dir of entries/*.json shards")
    parser.add_argument("--index", type=Path, required=True, help="dir of index/*.json shards")
    parser.add_argument("--out", type=Path, default=Path("build/ddk"))
    parser.add_argument("--version", default="1.3.0")
    args = parser.parse_args()
    stats = build(args.entries, args.index, args.out, args.version)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
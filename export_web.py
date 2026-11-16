#!/usr/bin/env python3
"""Export the same sourced lexicon to small, static browser lookup shards."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

from make_source import (
    LexiconEntry, assign_aliases, load_dehkhoda, load_editorial,
    load_hmt, load_kaikki, merge_key,
)


def shard_name(key: str) -> str:
    """Use ASCII file names even for Persian, Arabic and punctuation."""
    return f"{ord(key[0]):04x}"


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def export_site(entries: dict[str, LexiconEntry], out: Path, web: Path, cover: Path) -> dict:
    usable = {entry.key: entry for entry in entries.values() if any(entry.definitions.values())}
    aliases, conflicts = assign_aliases(usable)
    index: dict[str, str] = {}
    entry_shards: dict[str, dict] = defaultdict(dict)
    index_shards: dict[str, dict] = defaultdict(dict)

    # Canonical headwords have priority over generated inflections.
    for key, entry in sorted(usable.items()):
        index[merge_key(entry.headword)] = key
        entry_shards[shard_name(key)][key] = {
            "word": entry.headword,
            "pos": sorted(entry.parts_of_speech),
            "sources": {
                name: entry.definitions[name]
                for name in ("Wiktionary", "Editorial", "HMT", "Dehkhoda-Lexicon")
                if entry.definitions.get(name)
            },
        }

    for key, entry in sorted(usable.items()):
        for alias in sorted(aliases[key]):
            normal = merge_key(alias)
            # Never replace a canonical word with another entry's alias.
            index.setdefault(normal, key)

    for search_term, target in sorted(index.items()):
        index_shards[shard_name(search_term)][search_term] = target

    out.mkdir(parents=True, exist_ok=True)
    for path in web.iterdir():
        if path.is_file():
            shutil.copy2(path, out / path.name)
    shutil.copy2(cover, out / "cover.png")

    for shard, items in entry_shards.items():
        write_json(out / "data" / "entries" / f"{shard}.json", items)
    for shard, items in index_shards.items():
        write_json(out / "data" / "index" / f"{shard}.json", items)

    manifest = {
        "entries": len(usable),
        "lookup_terms": len(index),
        "alias_conflicts_skipped": conflicts,
        "index_shards": sorted(index_shards),
        "entry_shards": sorted(entry_shards),
    }
    write_json(out / "data" / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hmt-body", type=Path, required=True)
    parser.add_argument("--dehkhoda", type=Path, required=True)
    parser.add_argument("--kaikki", type=Path, required=True)
    parser.add_argument(
        "--editorial", type=Path,
        default=Path(__file__).resolve().parent / "lexicon/idioms.json",
    )
    parser.add_argument("--web", type=Path, default=Path("web"))
    parser.add_argument("--cover", type=Path, default=Path("build/cover.png"))
    parser.add_argument("--out", type=Path, default=Path("site"))
    args = parser.parse_args()

    entries: dict[str, LexiconEntry] = {}
    load_kaikki(args.kaikki, entries)
    load_dehkhoda(args.dehkhoda, entries)
    load_hmt(args.hmt_body, entries)
    load_editorial(args.editorial, entries)
    print(json.dumps(export_site(entries, args.out, args.web, args.cover), ensure_ascii=False))


if __name__ == "__main__":
    main()

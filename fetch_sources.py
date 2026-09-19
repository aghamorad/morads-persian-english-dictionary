#!/usr/bin/env python3
"""Download and verify the source snapshots listed in sources.lock.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--lock", type=Path, default=Path("sources.lock.json"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    for name, source in lock["sources"].items():
        target = args.out / source["filename"]
        if target.exists() and sha256(target) == source["sha256"]:
            print(f"verified {name}: {target}")
            continue
        temporary = target.with_suffix(target.suffix + ".part")
        request = urllib.request.Request(source["url"], headers={"User-Agent": "morads-persian-english-dictionary/1.0"})
        with urllib.request.urlopen(request) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        actual = sha256(temporary)
        if actual != source["sha256"]:
            temporary.unlink(missing_ok=True)
            raise SystemExit(f"checksum mismatch for {name}: expected {source['sha256']}, got {actual}")
        temporary.replace(target)
        print(f"downloaded {name}: {target}")


if __name__ == "__main__":
    main()

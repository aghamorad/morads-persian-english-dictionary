#!/usr/bin/env python3
"""Verify the built MOBI with kindling's on-device lookup simulator."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


REQUIRED_LOOKUPS = (
    "هنگفت",
    "هنگفتی",
    "ممتحن",
    "گفت",
    "رفت",
    "خورد",
    "اقتدار",
    "کتاب",
    "كتاب",
    "خانۀ",
    "خانهٔ",
    "کتابی",
    "کتاب‌ها",
    "فارسى",
    # Inflected forms the alias generator now covers: plural indefinite, the spaced
    # indefinite after a silent heh, and plural with a singular possessive.
    "کتاب‌هایی",
    "روزهایی",
    "خانه‌هایی",
    "مشکل‌هایی",
    "خانه ای",
    "جلسه ای",
    "کتاب‌هایم",
    "کتاب‌هایت",
    "کتاب‌هایش",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mobi", type=Path)
    parser.add_argument("--kindling", type=Path, default=Path("tools/kindling-cli"))
    parser.add_argument("--stats", type=Path, default=Path("build/stats.json"))
    args = parser.parse_args()
    failures = []
    for word in REQUIRED_LOOKUPS:
        result = subprocess.run(
            [str(args.kindling), "lookup", str(args.mobi), word],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        resolved = " resolves " in output or output.startswith(f'"{word}" resolves')
        print(f"{word}: {'RESOLVES' if resolved else 'FAIL'}")
        if not resolved:
            failures.append(word)
    digest = hashlib.sha256(args.mobi.read_bytes()).hexdigest()
    print(f"mobi_bytes={args.mobi.stat().st_size}")
    print(f"mobi_sha256={digest}")
    if args.stats.exists():
        print(json.dumps(json.loads(args.stats.read_text(encoding="utf-8")), ensure_ascii=False, sort_keys=True))
    if failures:
        raise SystemExit("unresolved lookups: " + ", ".join(failures))


if __name__ == "__main__":
    main()

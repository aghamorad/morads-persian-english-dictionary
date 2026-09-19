#!/usr/bin/env python3
"""Extract the XML entries from an Apple Dictionary Body.data file."""

from __future__ import annotations

import argparse
import re
import struct
import zlib
from pathlib import Path


SEP = b"\xff\xff\xff\xff"


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def split_entries(data: bytes) -> list[str]:
    entries: list[str] = []
    pos = 0
    while pos + 4 <= len(data):
        length = u32(data, pos)
        pos += 4
        entries.append(data[pos:pos + length].decode("utf-8"))
        pos += length
    return entries


def process_chunk(chunk: bytes) -> list[str]:
    expected = u32(chunk, 0)
    decoded = zlib.decompress(chunk[4:])
    if len(decoded) != expected:
        raise ValueError("Apple Dictionary compressed chunk size mismatch")
    return split_entries(decoded)


def extract_body(path: Path) -> list[str]:
    raw = path.read_bytes()
    header = raw[:96]
    content = raw[96:]
    values = [
        u32(header, i)
        for i in range(0, len(header), 4)
        if header[i:i + 4] != SEP
    ]
    # The final header field is the number of chunks; this is how Apple's
    # current Body.data layout is organized.
    num_chunks = values[-1]
    entries: list[str] = []
    for _ in range(num_chunks):
        _size_1 = u32(content, 0)
        size_2 = u32(content, 4)
        chunk = content[8:8 + size_2]
        entries.extend(process_chunk(chunk))
        content = content[8 + size_2:]
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("body", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    entries = extract_body(args.body)
    args.output.write_text(
        '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">'
        + "".join(entries)
        + "</d:dictionary>",
        encoding="utf-8",
    )
    print(f"extracted {len(entries):,} entries to {args.output}")


if __name__ == "__main__":
    main()

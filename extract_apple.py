#!/usr/bin/env python3
"""Extract the XML entries from an Apple Dictionary Body.data file."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def process_chunk(chunk: bytes) -> bytes:
    """Decompress a single chunk and return the raw decompressed bytes."""
    expected = u32(chunk, 0)
    decoded = zlib.decompress(chunk[4:])
    if len(decoded) != expected:
        raise ValueError("Apple Dictionary compressed chunk size mismatch")
    return decoded


def extract_body(path: Path) -> list[str]:
    raw = path.read_bytes()
    header = raw[:96]
    # Field [16] is the byte length of the chunk stream (at header byte 64).
    # Walk until that many bytes are consumed.
    stream_length = u32(header, 64)
    content = raw[96:96 + stream_length]
    entries: list[str] = []
    consumed = 0
    while consumed + 8 <= len(content):
        _size_1 = u32(content, consumed)
        size_2 = u32(content, consumed + 4)
        if size_2 == 0:
            break
        block_end = consumed + 8 + size_2
        if block_end > len(content):
            break
        chunk = content[consumed + 8:block_end]
        decoded = process_chunk(chunk)
        entries.append(decoded.decode("utf-8"))
        consumed += 8 + size_2
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

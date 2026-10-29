"""The game's LZ codec (decompressor 80:935E / loop 80:93A8).

Stream of ops, ends at a 00 byte:
  01-7F n      literal: copy the next n bytes
  80-FF d      copy (op & 7F) + 3 bytes from d + 1 bytes back in the output (overlap allowed)
Blocks are reached through 16-bit pointer tables at the start of a bank ($3E points at the table entry).

    python -X utf8 tools/lz.py OFFSET [--rom ROM]      decompress one stream, print its sizes
"""
import argparse
from pathlib import Path


def decompress(data, pos, limit=0x10000):
    """Return (output bytes, compressed length) of the stream at pos."""
    out, start = bytearray(), pos
    while True:
        b = data[pos]
        if b == 0:
            return bytes(out), pos + 1 - start
        if b < 0x80:
            out += data[pos + 1:pos + 1 + b]
            pos += 1 + b
        else:
            n, d = (b & 0x7F) + 3, data[pos + 1] + 1
            if d > len(out):
                raise ValueError(f"copy before start at {pos:#x}")
            for _ in range(n):
                out.append(out[-d])
            pos += 2
        if len(out) > limit:
            raise ValueError("output too large")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("offset", type=lambda s: int(s, 16))
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    a = ap.parse_args()
    out, used = decompress(Path(a.rom).read_bytes(), a.offset)
    print(f"{a.offset:06X}: {used} bytes -> {len(out)} bytes")


if __name__ == "__main__":
    main()

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


def compress(data):
    """Greedy encoder for the format above: longest match (3-130 bytes, 1-256 back), else literals (runs of <=127)."""
    out, lit, i, seen = bytearray(), bytearray(), 0, {}  # seen: 3-byte key -> earlier positions
    while i < len(data):
        best, dist = 0, 0
        for j in reversed(seen.get(data[i:i + 3], ())):
            d = i - j
            if d > 256:
                break
            n = 0
            while n < 130 and i + n < len(data) and data[i + n] == data[i + n - d]:
                n += 1
            if n > best:
                best, dist = n, d
                if n == 130 or i + n == len(data):
                    break
        step = best if best >= 3 else 1
        for p in range(i, i + step):
            seen.setdefault(data[p:p + 3], []).append(p)
        if best >= 3:
            if lit:
                out += bytes([len(lit)]) + lit
                lit = bytearray()
            out += bytes([0x80 | (best - 3), dist - 1])
            i += best
        else:
            lit.append(data[i])
            i += 1
            if len(lit) == 0x7F:
                out += bytes([len(lit)]) + lit
                lit = bytearray()
    if lit:
        out += bytes([len(lit)]) + lit
    return bytes(out + b"\x00")


def blocks(rom):
    """Yield (name, file offset) for every LZ block behind a bank-start pointer table (as gfx_sweep.py finds them)."""
    for b in range(len(rom) // 0x8000):
        s = b * 0x8000
        w = rom[s] | rom[s + 1] << 8
        if not 0x8002 <= w < 0x8400 or w & 1:
            continue
        for i in range((w - 0x8000) // 2):
            p = rom[s + 2 * i] | rom[s + 2 * i + 1] << 8
            if p >= 0x8000:
                yield f"{b | 0x80:02X}_{i:02X}", s + (p & 0x7FFF)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("offset", type=lambda s: int(s, 16))
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    a = ap.parse_args()
    out, used = decompress(Path(a.rom).read_bytes(), a.offset)
    print(f"{a.offset:06X}: {used} bytes -> {len(out)} bytes")


if __name__ == "__main__":
    main()

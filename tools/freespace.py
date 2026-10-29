"""List free-space candidates: runs of one filler byte (00/FF) at the end of each 32 KiB LoROM bank.

    python tools/freespace.py [--rom ROM] [--min 256]

A candidate is not proven free: trap-fill it and tour the game, and search code for pointers into it, before use.
"""
import argparse
from pathlib import Path


def tails(rom, minimum=256):
    """Yield (bank, start offset, length, filler) for each bank whose tail is a run of 00 or FF."""
    for b in range(len(rom) // 0x8000):
        end = (b + 1) * 0x8000
        f = rom[end - 1]
        if f not in (0x00, 0xFF):
            continue
        p = end
        while p > b * 0x8000 and rom[p - 1] == f:
            p -= 1
        if end - p >= minimum:
            yield b, p, end - p, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    ap.add_argument("--min", type=int, default=256)
    a = ap.parse_args()
    total = 0
    for b, p, n, f in tails(Path(a.rom).read_bytes(), a.min):
        total += n
        print(f"bank ${b | 0x80:02X}  {p:06X}-{p + n - 1:06X}  {n:6d} bytes of {f:02X}")
    print(f"total {total} bytes")


if __name__ == "__main__":
    main()

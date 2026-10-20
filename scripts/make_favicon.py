"""Build the atlas M favicon using only the standard library."""
from pathlib import Path
import struct
import zlib


def chunk(kind, data):
    return (struct.pack('>I', len(data)) + kind + data
            + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))


def main():
    size = 32
    # Existing site palette: --drape and --ink; original geometric monogram.
    rows = []
    for y in range(size):
        row = bytearray([0])  # PNG filter: none
        for x in range(size):
            stem = 7 <= y <= 24 and (7 <= x <= 10 or 21 <= x <= 24)
            diagonal = 7 <= y <= 16 and (abs(x - y) <= 2 or abs(x - (31 - y)) <= 2)
            row.extend((18, 34, 32, 255) if stem or diagonal else (221, 231, 228, 255))
        rows.append(row)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))
    ico = struct.pack('<HHH', 0, 1, 1) + struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(png), 22) + png
    target = Path(__file__).resolve().parents[1] / 'site' / 'favicon.ico'
    target.write_bytes(ico)
    print(f'{target.name}: {len(ico)} bytes')


if __name__ == '__main__':
    main()

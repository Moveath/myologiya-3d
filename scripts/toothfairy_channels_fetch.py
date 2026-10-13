"""Read selected inert members of a public ToothFairy2 training-data mirror.

The author licenses ToothFairy2 (not ToothFairy3) CC BY-SA 4.0. Archive member
CRC32 is checked by zipfile; this does not verify the entire 26 GB archive.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/toothfairy-channels'
URL = 'https://huggingface.co/datasets/XXCHENZm/ToothFairy2/resolve/main/ToothFairy2.zip'
SIZE = 26124590907


class RemoteZip(io.RawIOBase):
    def __init__(self):
        self.position = 0

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else SIZE + offset
        return self.position

    def tell(self):
        return self.position

    def read(self, count=-1):
        end = SIZE if count < 0 else min(SIZE, self.position + count)
        if end <= self.position:
            return b''
        start = self.position
        request = urllib.request.Request(URL + f'?range_start={start}&range_end={end}', headers={'Range': f'bytes={start}-{end-1}'})
        with urllib.request.urlopen(request, timeout=120) as response:
            assert response.status == 206
            assert response.headers['Content-Range'] == f'bytes {start}-{end-1}/{SIZE}'
            result = response.read()
        assert len(result) == end - start
        self.position = end
        return result


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(RemoteZip()) as archive:
        records = [dict(name=f.filename, size=f.file_size, compressed=f.compress_size, crc32=f'{f.CRC:08x}') for f in archive.infolist()]
        (CACHE / 'archive-index.json').write_text(json.dumps(records, indent=2), encoding='utf8')
        needles = sys.argv[1:] or ['dataset.json']
        selected = [f for f in archive.infolist() if any(n in f.filename for n in needles) and not f.is_dir()]
        print([(f.filename, f.file_size, f.compress_size) for f in selected], flush=True)
        for member in selected:
            target = CACHE / Path(member.filename).name
            if not target.exists():
                data = archive.read(member)  # zipfile verifies the original member CRC32
                target.write_bytes(data)
            else:
                data = target.read_bytes()
            assert len(data) == member.file_size
            import zlib
            assert zlib.crc32(data) == member.CRC
            print(target.name, 'CRC32 verified', hashlib.sha256(data).hexdigest(), flush=True)


if __name__ == '__main__':
    main()

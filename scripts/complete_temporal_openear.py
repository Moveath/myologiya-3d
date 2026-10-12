"""Fetch the original OpenEar mesh members by bounded HTTP Range requests.

Source: Sieber et al., Zenodo 1473724, CC BY 4.0. This does not extract a
restricted viewer: the original publication explicitly distributes these ZIPs.
ZIP member CRC32 is checked by zipfile; full archive MD5 is not claimed when
only selected members were downloaded. Source meshes remain a local cache.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/complete-temporal'
RECORD = CACHE / 'record.json'


class RemoteZip(io.RawIOBase):
    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0
        self.blocks = {}

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        self.pos = (0, self.pos, self.size)[whence] + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        size = min(self.size - self.pos, size if size >= 0 else self.size)
        if size <= 0:
            return b''
        output = []
        while size:
            block_size = 1024 * 1024
            start = self.pos // block_size * block_size
            end = min(start + block_size, self.size) - 1
            length = end - start + 1
            if start in self.blocks:
                data = self.blocks[start]
            else:
                data = self.fetch(start, end)
                self.blocks[start] = data
            offset = self.pos - start
            take = min(size, length - offset)
            output.append(data[offset:offset + take])
            self.pos += take
            size -= take
        return b''.join(output)

    def fetch(self, start, end):
        length = end - start + 1
        for attempt in range(4):
            try:
                req = urllib.request.Request(self.url, headers={
                    'User-Agent': 'myologiya3d educational atlas',
                    'Range': f'bytes={start}-{end}'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    expected = f'bytes {start}-{end}/{self.size}'
                    assert response.status == 206, response.status
                    assert response.headers.get('Content-Range') == expected
                    data = response.read(length + 1)
                assert len(data) == length
                print('Range', start, end, 'OK', flush=True)
                break
            except Exception as exc:
                print('Range retry', start, end, type(exc).__name__, flush=True)
                if attempt == 3:
                    raise
                time.sleep(2)
        return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--specimen', default='ZETA')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--bone-voxel', action='store_true', help='Use author bone mask instead of the much larger PLY')
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if not RECORD.exists():
        previous_record = ROOT / 'research/cache/temporal/openear.json'
        if previous_record.exists():
            RECORD.write_bytes(previous_record.read_bytes())
        else:
            request = urllib.request.Request('https://zenodo.org/api/records/1473724',
                                             headers={'User-Agent': 'myologiya3d educational atlas'})
            with urllib.request.urlopen(request, timeout=45) as response:
                RECORD.write_bytes(response.read())
    record = json.loads(RECORD.read_text(encoding='utf-8'))
    assert record['metadata']['license']['id'] == 'cc-by-4.0'
    entry = next(f for f in record['files'] if f['key'] == args.specimen + '.zip')
    url = f"https://zenodo.org/records/1473724/files/{entry['key']}"
    out = CACHE / args.specimen.lower()
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(RemoteZip(url, entry['size'])) as archive:
        members = archive.infolist()
        inventory = [{'name': f.filename, 'bytes': f.file_size,
                      'compressed_bytes': f.compress_size, 'crc32': f'{f.CRC:08x}'}
                     for f in members]
        (out / 'zip-inventory.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')
        selected = [f for f in members if f.filename.lower().endswith(('.ply', '.mrml', '.txt'))]
        if args.bone_voxel:
            selected = [f for f in selected if Path(f.filename).name != 'Bone.ply']
            selected.extend(f for f in members if Path(f.filename).name == 'Bone.nrrd')
        for member in selected:
            print(member.filename, member.file_size, member.compress_size, flush=True)
        if not args.download:
            return
        acquired = []
        for member in selected:
            filename = Path(member.filename).name
            assert filename not in ('', '.', '..')
            destination = out / filename
            if destination.exists() and destination.stat().st_size == member.file_size:
                data = destination.read_bytes()
                import binascii
                assert binascii.crc32(data) & 0xffffffff == member.CRC
            else:
                data = archive.read(member)  # zipfile validates the member CRC.
                destination.write_bytes(data)
            acquired.append({'archive_path': member.filename, 'file': filename,
                             'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                             'zip_crc32': f'{member.CRC:08x}'})
            print('Downloaded and CRC-checked', filename, len(data), flush=True)
    manifest = {'source': url, 'record': 'https://zenodo.org/records/1473724',
                'paper': 'https://doi.org/10.1038/sdata.2018.297',
                'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
                'authors': [c['name'] for c in record['metadata']['creators']],
                'specimen': args.specimen, 'original_archive_bytes': entry['size'],
                'original_archive_md5_unverified': entry['checksum'],
                'method': 'HTTP byte ranges; selected ZIP members; each member CRC32 checked',
                'files': acquired}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

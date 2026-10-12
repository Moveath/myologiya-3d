"""Fetch the registered high-resolution OpenEar ZETA CBCT for native review.

Only public archive bytes are fetched. zipfile verifies the selected member CRC.
The registered CBCT has its own header, which must be read before spatial use.
"""
from pathlib import Path
import concurrent.futures
import argparse
import binascii
import hashlib
import json
import zipfile
from complete_temporal_openear import RemoteZip

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/temporal_features'
OUT.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    filename = 'CBCT_Unembedded.nrrd' if args.full else 'CBCT_Embedded.nrrd'
    cached = OUT / filename
    if cached.exists():
        inventory=json.loads((ROOT/'research/cache/complete-temporal/zeta/zip-inventory.json').read_text())
        expected=next(r for r in inventory if r['name']=='05_Registred_Slicer_Volumes/'+filename)
        raw=cached.read_bytes()
        assert len(raw)==expected['bytes']
        assert f'{binascii.crc32(raw)&0xffffffff:08x}'==expected['crc32']
        print('Existing source member CRC32 verified:',filename,flush=True)
        return
    record = json.loads((ROOT / 'research/cache/temporal/openear.json').read_text(encoding='utf-8'))
    entry = next(f for f in record['files'] if f['key'] == 'ZETA.zip')
    remote = RemoteZip('https://zenodo.org/records/1473724/files/ZETA.zip', entry['size'])
    with zipfile.ZipFile(remote) as z:
        member = z.getinfo('05_Registred_Slicer_Volumes/' + filename)
        start = member.header_offset // (1024*1024) * (1024*1024)
        end = member.header_offset + member.compress_size + 2048
        blocks = list(range(start, end, 8*1024*1024))
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for begin, raw in pool.map(lambda i: (i, remote.fetch(i, min(i + 8*1024*1024, remote.size)-1)), blocks):
                for offset in range(0,len(raw),1024*1024):
                    remote.blocks[begin+offset] = raw[offset:offset+1024*1024]
        raw = z.read(member)
        out = OUT / filename
        out.write_bytes(raw)
        metadata = {'source': remote.url, 'member': member.filename, 'bytes': len(raw),
                    'crc32': f'{member.CRC:08x}', 'crc32_verified': True,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'license': 'CC BY 4.0',
                    'note': 'Selected member verification; full archive MD5 not verified.'}
        (OUT / ('cbct-full-download.json' if args.full else 'cbct-download.json')).write_text(json.dumps(metadata, indent=2) + '\n')
        print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()

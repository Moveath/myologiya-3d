"""Acquire and inspect additional open skull candidates without publishing them.

Only author-authorized downloads are used. This audit does not relabel atlas
markers or infer anatomical completeness from triangle counts. Source files and
review GLBs stay in research/cache/new-skull (excluded from publication).
"""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/new-skull'
HF = 'https://huggingface.co/datasets/BoneHub/visible-human-3d-models'


def fetch(url, destination, sha256=None, md5=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with urllib.request.urlopen(url, timeout=60) as response, destination.open('wb') as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
    data = destination.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha256 and sha != sha256:
        raise ValueError(f'SHA256 mismatch: {destination.name}')
    if md5 and hashlib.md5(data).hexdigest() != md5:
        raise ValueError(f'MD5 mismatch: {destination.name}')
    return {'file': str(destination.relative_to(ROOT)).replace('\\', '/'),
            'bytes': len(data), 'sha256': sha, 'url': url}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--mug500-masks', action='store_true', help='Download only first archive author NRRD masks by HTTP ranges')
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest = []
    if args.mug500_masks:
        import zipfile
        from complete_temporal_openear import RemoteZip
        record = CACHE / 'mug500-record.json'
        fetch('https://api.figshare.com/v2/articles/9616319', record)
        metadata = json.loads(record.read_text(encoding='utf-8'))
        assert metadata['license']['name'] == 'CC BY 4.0'
        item = next(f for f in metadata['files'] if f['name'] == 'A0001-A0020.zip')
        masks = []
        with zipfile.ZipFile(RemoteZip(item['download_url'], item['size'])) as archive:
            for member in archive.infolist():
                if not member.filename.endswith('.nrrd'):
                    continue
                target = CACHE / 'mug500' / Path(member.filename).name
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    import binascii
                    data = target.read_bytes()
                    assert (binascii.crc32(data) & 0xffffffff) == member.CRC
                else:
                    data = archive.read(member)
                    target.write_bytes(data)
                header = data.split(b'\n\n', 1)[0].decode('ascii', errors='replace')
                masks.append({'file': str(target.relative_to(ROOT)).replace('\\', '/'),
                              'member': member.filename, 'bytes': len(data), 'zip_crc32': f'{member.CRC:08x}',
                              'sha256': hashlib.sha256(data).hexdigest(), 'header': header})
        (CACHE / 'mug500-masks.json').write_text(json.dumps({'archive': item['download_url'],
            'archive_md5_verified': False, 'members_crc32_verified': True, 'masks': masks}, indent=2), encoding='utf-8')
        print('MUG500 masks checked:', len(masks), flush=True)
    inventory = CACHE / 'bonehub-files.json'
    if args.download:
        fetch('https://huggingface.co/api/datasets/BoneHub/visible-human-3d-models/tree/main?recursive=true&limit=1000', inventory)
        fetch(HF + '/raw/main/README.md', CACHE / 'bonehub-readme.md')
    if inventory.exists():
        files = json.loads(inventory.read_text(encoding='utf-8'))
        for item in files:
            if '/SKULL/' not in item['path'] or '/Mesh/' not in item['path']:
                continue
            dst = CACHE / ('bonehub-' + item['path'].split('/')[3] + '-' + Path(item['path']).name)
            if args.download or dst.exists():
                entry = fetch(HF + '/resolve/main/' + item['path'], dst, sha256=item['lfs']['oid'])
                entry.update(source='bonehub', license='CC BY 4.0', hash_checked_against='Hugging Face Git LFS SHA256')
                manifest.append(entry)
    dst = CACHE / 'nih-002448.stl'
    if args.download or dst.exists():
        entry = fetch('https://3d.nih.gov/api/submissions/31677/runs/f5bf57f4-c5ad-4d0c-bf09-62033800b3d7/output-files/862730', dst,
                      md5='0416f322fc725f57b964ab3e15212fa6')
        entry.update(source='nih_002448', license='CC BY 4.0', hash_checked_against='NIH workflow output ETag (single MD5)')
        manifest.append(entry)
    if args.inspect:
        import numpy as np
        import trimesh
        scene = trimesh.Scene()
        for entry in manifest:
            filename = ROOT / entry['file']
            mesh = trimesh.load_mesh(filename, process=True)
            entry['geometry'] = {
                'vertices': len(mesh.vertices), 'triangles': len(mesh.faces),
                'bounds_native': mesh.bounds.tolist(), 'watertight': bool(mesh.is_watertight),
                'units': 'STL has no unit metadata; author export expected millimetres, not independently confirmed',
            }
            # Proper rotation only for local display: native +Z becomes +Y.
            matrix = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)
            mesh.apply_transform(matrix)
            mesh.apply_scale(0.001)
            key = filename.stem.replace('bonehub-', '').replace('SKULL_', '').lower()
            scene.add_geometry(mesh, node_name='b|' + key, geom_name='b|' + key)
            entry['review_node'] = key
        scene.export(CACHE / 'review.glb')
    previous_file = CACHE / 'acquired.json'
    if not args.inspect and previous_file.exists():
        previous = {x['sha256']: x for x in json.loads(previous_file.read_text(encoding='utf-8'))}
        manifest = [{**previous.get(x['sha256'], {}), **x} for x in manifest]
    previous_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

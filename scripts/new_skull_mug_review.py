"""Build one original-resolution MUG500 author-mask surface for local review.

No interpolation beyond marching cubes, no anatomical editing, no simplification,
and no publication. A surface reconstructed from a binary author mask cannot
recover structures absent from that mask.
"""
from pathlib import Path
import argparse
import gzip
import json
import re

import numpy as np
import trimesh
from skimage.measure import marching_cubes

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/new-skull'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('specimen', default='A0014', nargs='?')
    args = parser.parse_args()
    filename = CACHE / 'mug500' / (args.specimen + '.nrrd')
    header, payload = filename.read_bytes().split(b'\n\n', 1)
    fields = dict(line.split(': ', 1) for line in header.decode('ascii').splitlines() if ': ' in line and not line.startswith('#'))
    assert fields['type'] == 'short' and fields['endian'] == 'little' and fields['encoding'] == 'gzip'
    assert fields['space'] == 'left-posterior-superior'
    sizes = list(map(int, fields['sizes'].split()))
    directions = np.array([list(map(float, x.split(','))) for x in re.findall(r'\(([^)]+)\)', fields['space directions'])])
    origin = np.fromstring(fields['space origin'].strip('()'), sep=',')
    raw = gzip.decompress(payload)
    volume = np.frombuffer(raw, dtype='<i2').reshape(sizes, order='F')
    values, counts = np.unique(volume, return_counts=True)
    vertices, faces, _, _ = marching_cubes(volume.astype(np.float32), level=0.5, allow_degenerate=False)
    native = vertices @ directions + origin
    # Proper rotation of LPS coordinates: X remains left, Y becomes superior, Z anterior.
    world = native[:, [0, 2, 1]] * np.array([1, 1, -1]) * 0.001
    mesh = trimesh.Trimesh(vertices=world, faces=faces, process=False)
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name='b|' + args.specimen, geom_name='b|' + args.specimen)
    scene.export(CACHE / 'mug500-review.glb')
    report = {'specimen': args.specimen, 'source': str(filename.relative_to(ROOT)).replace('\\', '/'),
              'header': fields, 'voxel_values': dict(zip(values.tolist(), counts.tolist())),
              'triangles': len(faces), 'vertices': len(vertices), 'bounds_m': mesh.bounds.tolist(),
              'changes': ['Marching cubes level 0.5 at all original samples',
                          'LPS -> [L,S,-P], mm -> m', 'No smoothing, decimation or anatomical remodeling'],
              'independent_anatomical_landmarks_verified': 0,
              'registration_to_bodyparts3d': False}
    (CACHE / 'mug500-review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

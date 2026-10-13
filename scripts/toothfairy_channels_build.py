"""Inspect original ToothFairy2 label volumes; output remains research-only.

No invented canal, smoothing, gap filling, or mirrored side is generated.
The canal meshes bound the author's labelled volume, not cortical bone walls.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from skimage.measure import marching_cubes
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/toothfairy-channels'
BUILD = ROOT / 'build_head/toothfairy_channels'


def read_mha(path):
    header = {}
    with path.open('rb') as stream:
        while True:
            line = stream.readline().decode('ascii').strip()
            key, value = line.split(' = ', 1)
            header[key] = value
            if key == 'ElementDataFile':
                break
        offset = stream.tell()
    assert header['CompressedData'] == 'False' and header['ElementDataFile'] == 'LOCAL'
    dtype = {'MET_UCHAR': np.uint8, 'MET_DOUBLE': np.dtype('<f8')}[header['ElementType']]
    shape = tuple(map(int, header['DimSize'].split()))[::-1]
    return np.memmap(path, mode='r', dtype=dtype, offset=offset, shape=shape), header


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    volume, header = read_mha(CACHE / 'ToothFairy2F_026.mha')
    scene = trimesh.Scene()
    rows = []
    for label, name, color in [(1, 'mandible_context', [227, 217, 193, 255]), (3, 'mandibular_canal_left', [83, 174, 209, 255]), (4, 'mandibular_canal_right', [229, 140, 101, 255])]:
        mask = volume == label
        locations = np.argwhere(mask)
        low, high = locations.min(0), locations.max(0) + 1
        components, count = ndimage.label(mask)
        counts = np.bincount(components.ravel())[1:]
        roi = mask[tuple(slice(a, b) for a, b in zip(low, high))]
        vertices, faces, _, _ = marching_cubes(np.pad(roi, 1), .5, allow_degenerate=False)
        vertices += low - 1
        # Display orientation is checked visually; the dataset FAQ warns that
        # direction metadata does not establish physical patient orientation.
        vertices = -vertices[:, [2, 0, 1]] * .0003
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces[:, ::-1], process=False)
        mesh.visual.vertex_colors = color
        scene.add_geometry(mesh, node_name='toothfairy|' + name, geom_name=name)
        rows.append({'id': name, 'source_label': label, 'voxels': len(locations),
                     'components_6_connected': count, 'component_voxels': sorted(map(int, counts), reverse=True),
                     'triangles': len(faces), 'bounds_m': mesh.bounds.tolist(),
                     'label_interpretation': 'author-labelled canal volume' if label != 1 else 'author-labelled mandibular bone',
                     'label_touches_volume_boundary': bool(np.any(low == 0) or np.any(high == volume.shape)),
                     'added_smoothing': False, 'added_gap_filling': False, 'full_bone_wall_claim': False})
        print(name, len(faces), count, flush=True)
    target = BUILD / 'toothfairy-f026-hi.glb'
    target.write_bytes(scene.export(file_type='glb'))
    report = {'specimen': 'ToothFairy2 F026', 'source': 'https://ditto.ing.unimore.it/toothfairy2/',
              'mirror': 'https://huggingface.co/datasets/XXCHENZm/ToothFairy2',
              'declared_license': 'CC BY-SA 4.0', 'publication_approved': False,
              'publication_note': 'Review current author licence against research-only wording in the 2024 ethics proposal before publishing.',
              'source_header': header, 'voxel_mm': .3, 'structures': rows,
              'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (BUILD / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()

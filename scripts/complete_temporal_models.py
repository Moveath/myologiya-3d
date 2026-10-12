"""Build a co-registered OpenEar specimen from the author's bone mask and PLYs.

This rotates the common specimen frame into renderer axes. It does not register the specimen
to BodyParts3D, reflect a right ear into a left ear, or reconstruct guessed tubes.
"""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

import numpy as np
import trimesh
from skimage.measure import marching_cubes

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/complete-temporal/zeta'
OUT = ROOT / 'build_head/complete_temporal'
OUT.mkdir(parents=True, exist_ok=True)
RAS_TO_VIEWER = np.array([[-1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
assert np.linalg.det(RAS_TO_VIEWER) == 1

PARTS = [
    ('scala_tympani', '01_Scala Tympani.ply', '#63c6e8'),
    ('vestibular_space', '02_Scala Vestibuli.ply', '#5c92de'),
    ('malleus', '03_Malleus.ply', '#e8ac54'),
    ('incus', '04_Incus.ply', '#83b977'),
    ('stapes', '05_Stapes.ply', '#c67ca8'),
    ('facial_nerve', '06_Facial Nerve.ply', '#e9d258'),
    ('chorda_tympani', '07_Chorda Tympani.ply', '#ddbd55'),
    ('vestibulocochlear_nerve', '08_Cochleovestibular Nerve.ply', '#bfad5d'),
    ('tympanic_membrane', '09_Tympanic Membrane.ply', '#acb5cd'),
    ('external_acoustic_meatus', '10_External Auditory Canal.ply', '#72c6bb'),
    ('sinus_dura', '11_Sinus Dura.ply', '#9a7fae'),
    ('internal_carotid_artery', '12_Carotis Interna.ply', '#d56e6f'),
]


def color_mesh(mesh, color):
    mesh.visual = trimesh.visual.ColorVisuals(mesh=mesh, vertex_colors=trimesh.visual.color.hex_to_rgba(color))
    return mesh


def bone_mask():
    raw = (CACHE / 'Bone.nrrd').read_bytes()
    stop = raw.index(b'\n\n') + 2
    header = raw[:stop].decode('ascii')
    assert 'space: left-posterior-superior' in header
    assert 'sizes: 668 587 625' in header
    assert '(-0.125,0,0) (0,-0.125,0) (0,0,0.125)' in header
    origin = np.array([19.806900024414063, 7.7452301979064941, -1.7357300519943237])
    volume = np.frombuffer(gzip.decompress(raw[stop:]), dtype='<i2').reshape((625, 587, 668))
    vertices, faces = [], []
    offset = 0
    # One shared slice prevents omissions along slab seams. Vertices at seams
    # are merged later, not closed with artificial caps.
    for first in range(0, volume.shape[0] - 1, 40):
        last = min(first + 41, volume.shape[0])
        slab = volume[first:last]
        if slab.min() == slab.max():
            continue
        v, f, _, _ = marching_cubes(slab, level=.5, allow_degenerate=False)
        v[:, 0] += first
        # Slicer PLY meshes use RAS. NRRD is LPS, with negative i/j steps.
        # Native RAS = [-origin_L + .125*i, -origin_P + .125*j, origin_S + .125*k].
        v = v[:, [2, 1, 0]].copy() * .125
        v += origin * np.array([-1, -1, 1])
        v = (v @ RAS_TO_VIEWER.T) * .001  # Proper rotation; no reflection or registration.
        vertices.append(v)
        faces.append(f[:, [0, 2, 1]] + offset)  # axis permutation changes handedness.
        offset += len(v)
        print('Bone slab', first, last, len(v), len(f), flush=True)
    mesh = trimesh.Trimesh(vertices=np.vstack(vertices), faces=np.vstack(faces), process=False)
    mesh.merge_vertices(digits_vertex=8)
    return mesh, header


def main():
    scene = trimesh.Scene()
    report = []
    for part, filename, color in PARTS:
        mesh = trimesh.load(CACHE / filename, process=False)
        mesh.vertices = (mesh.vertices @ RAS_TO_VIEWER.T) * .001
        color_mesh(mesh, color)
        scene.add_geometry(mesh, node_name='openear|' + part, geom_name=part)
        report.append({'id': part, 'node': 'openear|' + part, 'source': filename,
                       'vertices': len(mesh.vertices), 'triangles': len(mesh.faces),
                       'bounds_m': mesh.bounds.tolist(), 'watertight': bool(mesh.is_watertight),
                       'color': color})
    bone, header = bone_mask()
    color_mesh(bone, '#d8cab0')
    scene.add_geometry(bone, node_name='openear|temporal_bone', geom_name='temporal_bone')
    report.append({'id': 'temporal_bone', 'node': 'openear|temporal_bone', 'source': 'Bone.nrrd',
                   'vertices': len(bone.vertices), 'triangles': len(bone.faces),
                   'bounds_m': bone.bounds.tolist(), 'color': '#d8cab0'})
    high = OUT / 'skull-openear-hi.glb'
    high.write_bytes(scene.export(file_type='glb'))
    output = OUT / 'skull-openear.glb'
    cli = ROOT / 'tools/node_modules/gltfpack/cli.js'
    completed = subprocess.run(['node', str(cli), '-i', str(high), '-o', str(output),
                                '-cc', '-kn', '-ke', '-vp', '16'],
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=True)
    print(completed.stdout.decode(errors='replace'), completed.stderr.decode(errors='replace'), flush=True)
    payload = {'source': json.loads((CACHE / 'manifest.json').read_text(encoding='utf-8')),
               'file': output.name, 'bytes': output.stat().st_size,
               'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
               'bone_header': header,
               'coordinate_frame': 'Author PLY in RAS; NRRD LPS converted to matching RAS, then all vertices [RASx,RASy,RASz] → [-RASx,RASz,RASy] and mm → m. Renderer X left, Y superior, Z anterior according to source axes. No registration to BodyParts3D.',
               'ras_to_viewer_matrix': RAS_TO_VIEWER.tolist(),
               'changes': ['12 author PLY meshes retained without anatomical remodeling.',
                           'Bone surface generated from author binary mask at level 0.5 and original 0.125 mm sampling.',
                           'LPS bone coordinates converted to RAS to match author PLY; common proper rotation [-RASx,RASz,RASy] and mm to metres.',
                           'Meshopt compression with 16-bit position quantization; no decimation in this build.'],
               'structures': report}
    (OUT / 'geometry-report.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote', output, output.stat().st_size, 'bytes', flush=True)


if __name__ == '__main__':
    main()

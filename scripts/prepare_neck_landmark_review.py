"""Build an unchanged-bone-only inspection GLB; never used as a published model."""
from pathlib import Path
import json
import numpy as np
import trimesh
from manifest_neck import BONES

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build_neck/landmark_review'
out.mkdir(parents=True, exist_ok=True)
scene = trimesh.Scene()
for bone, ids in BONES.items():
    for fid in ids:
        m = trimesh.load(ROOT / f'stl_neck/{fid}.stl', process=True)
        m.vertices = m.vertices[:, [0, 2, 1]] * np.array([1, 1, -1]) / 1000
        scene.add_geometry(m, node_name=f'b|{bone}', geom_name=f'b|{bone}')
scene.export(out / 'bones.glb')
print(out / 'bones.glb')

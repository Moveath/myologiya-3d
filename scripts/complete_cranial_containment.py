"""Measure cavity/simplified-bone envelope mismatch (requires rtree).

Sampling detects incompatible surfaces; containment is not an anatomical test.
"""
from pathlib import Path
import json
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/complete_cranial'
scene=trimesh.load(OUT/'comparison.glb',force='scene')
def mesh(key):
    matrix,name=scene.graph[key]
    result=scene.geometry[name].copy()
    result.apply_transform(matrix)
    return result
rows=[]
names=[('frontal','frontal_sinus'),('sphenoid','sphenoidal_sinus')]
names += [('ethmoid',f'ethmoid_cells_{group}_{side}')
    for group in ['anterior','middle','posterior'] for side in ['left','right']]
for bone,cavity in names:
    envelope=mesh('b|bp_'+bone)
    assert envelope.is_watertight, bone
    source=mesh('o|'+cavity)
    points=trimesh.sample.sample_surface(source,3000,seed=0)[0]
    inside=envelope.contains(points)
    _,distance,_=trimesh.proximity.closest_point(envelope,points)
    rows.append({'bone':bone,'cavity':cavity,'inside_fraction':float(inside.mean()),
        'outside_distance_quantiles_mm':np.quantile(distance[~inside]*1000,[.5,.9,.95,1]).tolist() if (~inside).any() else []})
(OUT/'cavity-containment.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))

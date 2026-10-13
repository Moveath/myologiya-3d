"""Export unchanged source bone surfaces for local visual inspection.

Sternal source parts are concatenated in their original coordinate frame, not
registered, deformed or fused. This inspection asset is not published.
"""
from pathlib import Path
import json
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
names=dict(line.rstrip('\n').split('\t')[::-1] for line in (ROOT/'bp/all_named.tsv').open(encoding='utf8'))
WORDS='first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth'.split()
BONES={f'thoracic_{i}':[names[f'{w} thoracic vertebra']] for i,w in enumerate(WORDS,1)}
BONES.update({f'rib_{i}_{side}':[names[f'{side} {w} rib']] for side in ('right','left') for i,w in enumerate(WORDS,1)})
BONES['sternum']=[names[n] for n in ('manubrium','body of sternum','xiphoid process')]

def source_path(fid):
    for folder in ('stl_thorax','stl_neck','stl_head','stl_body'):
        p=ROOT/folder/(fid+'.stl')
        if p.exists(): return p
    raise FileNotFoundError(fid)

if __name__=='__main__':
    out=ROOT/'build_thorax/landmark_review'
    out.mkdir(parents=True,exist_ok=True)
    scene=trimesh.Scene()
    missing=[]
    for bone,fids in BONES.items():
        parts=[]
        try:
            for fid in fids:
                m=trimesh.load(source_path(fid),process=True)
                m.vertices=m.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
                parts.append(m)
        except FileNotFoundError:
            missing.append(bone)
            continue
        mesh=trimesh.util.concatenate(parts)
        scene.add_geometry(mesh,node_name='b|'+bone,geom_name='b|'+bone)
    scene.export(out/'bones.glb')
    (out/'inventory.json').write_text(json.dumps(dict(loaded=list(scene.geometry),missing=missing),indent=2),encoding='utf8')
    print('Inspection bones:',len(scene.geometry),'missing:',missing)

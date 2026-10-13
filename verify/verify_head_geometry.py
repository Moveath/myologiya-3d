"""Bound source-to-distribution vertex drift for every head bone, both assets.

This checks axis conversion, identity and compression; it does not identify
anatomical features or prove the accuracy of the BodyParts3D source anatomy.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from manifest_head import BONES

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
rotation=np.array([[1,0,0],[0,0,1],[0,-1,0]])
records=[]
for filename in ['head-glb.txt','head-q-glb.txt']:
    decoded=json.loads((ROOT/'build_head/geometry_check'/filename.replace('.txt','.json')).read_text())
    assert set(decoded)==set(BONES), 'The distributed bone inventory differs from the source manifest'
    for bone,fids in BONES.items():
        source=trimesh.util.concatenate([trimesh.load(ROOT/'stl_head'/f'{fid}.stl',process=True) for fid in fids])
        original=source.vertices@rotation.T/1000
        actual=np.asarray(decoded[bone]['vertices']).reshape(-1,3)
        output_faces=np.asarray(decoded[bone]['faces']).reshape(-1,3)
        forward=cKDTree(actual).query(original)[0]*1000
        reverse=cKDTree(original).query(actual)[0]*1000
        # Nearest-vertex distances are conservative upper bounds on point-to-surface distances.
        maximum=max(float(forward.max()),float(reverse.max()))
        assert maximum<.03,(filename,bone,maximum,'Source geometry drift exceeds 0.03 mm')
        assert len(output_faces)==len(source.faces),(filename,bone,'Bone triangle count changed')
        records.append(dict(file=filename,bone=bone,source_files=[dict(file=f'stl_head/{fid}.stl',sha256=sha(ROOT/'stl_head'/f'{fid}.stl')) for fid in fids],source_triangles=len(source.faces),distributed_triangles=len(output_faces),maximum_bidirectional_vertex_distance_mm=maximum,source_to_distributed_maximum_mm=float(forward.max()),distributed_to_source_maximum_mm=float(reverse.max())))
report=dict(status='passed',scope='All 22 source bones in both distributed GLBs; compression and identity only, not anatomical completeness',metric='Maximum bidirectional nearest-vertex distance; a conservative vertex-to-surface bound, not continuous surface Hausdorff distance',tolerance_mm=.03,assets={f:sha(ROOT/'site'/f) for f in ['head-glb.txt','head-q-glb.txt']},checked=len(records),maximum_distance_mm=max(r['maximum_bidirectional_vertex_distance_mm'] for r in records),records=records)
(ROOT/'verify/head-source-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Verified bone assets:',len(records),'maximum vertex drift:',report['maximum_distance_mm'],'mm')

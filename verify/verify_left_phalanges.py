"""Addressed source/export/registration diagnostics; no mesh or pin repair."""
import base64
import hashlib
import io
import json
import pathlib
import sys
import time
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = pathlib.Path(__file__).resolve().parents[1]
run = pathlib.Path(sys.argv[1])
cache = root / "research/cache/stage6-sources"
out = root / "build_stage6/left_phalanges_v1"
mapping = {'phalanx_prox_1_left': 'FMA65470', 'phalanx_prox_2_left': 'FMA71915', 'phalanx_prox_3_left': 'FMA71908', 'phalanx_prox_4_left': 'FMA71916', 'phalanx_prox_5_left': 'FMA66791', 'phalanx_mid_2_left': 'FMA23938', 'phalanx_mid_3_left': 'FMA23940', 'phalanx_mid_4_left': 'FMA23942', 'phalanx_mid_5_left': 'FMA23944', 'phalanx_dist_1_left': 'FMA23951', 'phalanx_dist_2_left': 'FMA23953', 'phalanx_dist_3_left': 'FMA23955', 'phalanx_dist_4_left': 'FMA23957', 'phalanx_dist_5_left': 'FMA23959', 'metacarpal_1_left': 'FMA24465', 'metacarpal_2_left': 'FMA24467', 'metacarpal_3_left': 'FMA24469', 'metacarpal_4_left': 'FMA24471', 'metacarpal_5_left': 'FMA24473'}
TARGETS=list(mapping)[:14]


def world_meshes(scene):
    result = {}
    for node in scene.graph.nodes_geometry:
        owner = node
        while owner and not owner.startswith(("b|", "reference|")):
            owner = scene.graph.transforms.parents.get(owner)
        matrix, key = scene.graph[node]
        mesh = scene.geometry[key].copy()
        mesh.apply_transform(matrix)
        result[owner or node] = mesh
    return result

def compare(a, b):
    da = cKDTree(b.vertices).query(a.vertices)[0]
    db = cKDTree(a.vertices).query(b.vertices)[0]
    # Compare ordered face corners, allowing only floating-point serialization.
    direct = a.triangles.shape == b.triangles.shape and np.allclose(a.triangles, b.triangles, atol=2e-7, rtol=0)
    return dict(maxNearestVertexMM=float(max(da.max(), db.max())*1000),
                orderedTriangleCornersWithin0002MM=bool(direct),
                sourceTriangles=len(a.faces), targetTriangles=len(b.faces))

sources={};rows=[]
for bone,fma in mapping.items():
 mesh=trimesh.load(cache/(fma+'.obj'),force='mesh',process=False)
 mesh.vertices=mesh.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
 sources[bone]=mesh
 if bone not in TARGETS:continue
 target=world_meshes(trimesh.load(out/(bone+'.glb'),force='scene',process=False))['b|'+bone]
 result=compare(mesh,target)
 assert result['sourceTriangles']==result['targetTriangles'] and result['maxNearestVertexMM']<.001 and result['orderedTriangleCornersWithin0002MM']
 weld=target.copy();weld.merge_vertices()
 row=dict(id=bone,**result,extentsMM=(target.extents*1000).tolist(),bounds=target.bounds.tolist(),centroid=target.centroid.tolist(),degenerateFaces=int((target.area_faces<1e-15).sum()),duplicateFaces=int(len(weld.faces)-len(np.unique(np.sort(weld.faces,axis=1),axis=0))),watertight=bool(weld.is_watertight),windingConsistent=bool(weld.is_winding_consistent),positiveVolume=bool(weld.volume>0),components=len(weld.split(only_watertight=False)),positiveX=bool(target.bounds[0,0]>0))
 assert not row['degenerateFaces'] and not row['duplicateFaces'] and row['windingConsistent'] and row['positiveVolume'] and row['positiveX']
 rows.append(row)
pairs=[] # Prior target/proximal diagnostics reused after exact source/export checks.
controls=[]
for a,b in pairs:
 mesh=sources[a]; pts=mesh.vertices[np.linspace(0,len(mesh.vertices)-1,min(150,len(mesh.vertices)),dtype=int)]
 distances=[]
 for chunk in np.array_split(pts,10):distances.extend(trimesh.proximity.closest_point_naive(sources[b],chunk)[1].tolist())
 controls.append(dict(a=a,b=b,samples=len(pts),minSampleDistanceMM=min(distances)*1000,medianSampleDistanceMM=float(np.median(distances)*1000),jointSpaceAccepted=False))
with (run/'trimesh-check.json').open('x',encoding='utf8') as f:json.dump(dict(status='passed',rows=rows,adjacency=controls,acceptedScope='technical and gross source-frame consistency, not exact cartilage or joint contours'),f,indent=2)
with (run/'mesh-arrays.json').open('x',encoding='utf8') as f:json.dump({b:dict(vertices=m.vertices.flatten().tolist(),faces=m.faces.flatten().tolist()) for b,m in sources.items()},f)
print(json.dumps(dict(status='passed',models=len(rows),triangles=sum(r['targetTriangles'] for r in rows),rows=rows)))

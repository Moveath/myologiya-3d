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
out = root / "build_stage6/left_carpals2_v1"
mapping = {"trapezium_left":"FMA24444", "trapezoid_left":"FMA24445", "capitate_left":"FMA24447", "hamate_left":"FMA24449", "radius_left":"FMA23465", "ulna_left":"FMA23468", "scaphoid_left":"FMA24436", "lunate_left":"FMA24438", "triquetrum_left":"FMA24440", "pisiform_left":"FMA24442"}
TARGETS=list(mapping)[:4]


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
# Reconfirm the two live neighbours without repeating their expensive mesh audits.
for bone in ['radius_left','ulna_left','scaphoid_left','lunate_left','triquetrum_left','pisiform_left']:
 actual=world_meshes(trimesh.load(root/'site/models/bodyparts3d-3.0'/('left-forearm' if bone in ['radius_left','ulna_left'] else 'left-carpals1')/(bone+'.glb'),force='scene',process=False))['b|'+bone]
 assert compare(sources[bone],actual)['maxNearestVertexMM']<.001
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

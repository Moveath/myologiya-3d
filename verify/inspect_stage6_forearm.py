"""Read-only comparison of recovered source meshes and current GLB transforms."""
import base64
import io
import json
import pathlib
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = pathlib.Path(__file__).resolve().parents[1]
run = pathlib.Path(sys.argv[1])
cache = root / "research/cache/stage6-sources"
scene = trimesh.load(io.BytesIO(base64.b64decode((root/"site/arm-q-glb.txt").read_bytes())),
                     file_type="glb",force="scene",process=False)
current = {}
for node in scene.graph.nodes_geometry:
    label = node
    while label and not label.startswith("b|"):
        label = scene.graph.transforms.parents.get(label)
    if label not in ("b|radius","b|ulna"):
        continue
    transform,geometry = scene.graph[node]
    mesh = scene.geometry[geometry].copy()
    mesh.apply_transform(transform)
    current[label[2:]]=mesh
assert set(current)=={"radius","ulna"}
rows=[]
for fma,bone,side in [("FMA23464","radius","right"),("FMA23465","radius","left"),
                       ("FMA23467","ulna","right"),("FMA23468","ulna","left")]:
    mesh=trimesh.load(cache/(fma+".obj"),force="mesh",process=False)
    welded=mesh.copy()
    welded.merge_vertices()  # audit copy only, never saved as a replacement.
    stl=trimesh.load(cache/(fma+".stl"),force="mesh",process=False)
    v=mesh.vertices
    world=np.column_stack([v[:,0],v[:,2],-v[:,1]])/1000
    row=dict(id=fma,bone=bone,side=side,vertices=len(v),triangles=len(mesh.faces),
             nativeBounds=mesh.bounds.tolist(),threeBounds=np.array([world.min(0),world.max(0)]).tolist(),
             extentsMM=mesh.extents.tolist(),degenerateTriangles=int((mesh.area_faces<1e-12).sum()),
             duplicateTriangles=int(len(mesh.faces)-len(np.unique(np.sort(mesh.faces,axis=1),axis=0))),
             finite=bool(np.isfinite(v).all()),watertight=bool(welded.is_watertight),
             windingConsistent=bool(welded.is_winding_consistent),volumeMM3=float(welded.volume),
             components=len(welded.split(only_watertight=False)),
             stlMaxNearestVertexDistanceMM=float(cKDTree(v).query(stl.vertices)[0].max()),
             anatomicalAcceptance=False,selfIntersections="not tested; no claim of absence")
    if side=="right":
        existing=current[bone]
        distances=cKDTree(existing.vertices).query(world)[0]
        reverse=cKDTree(world).query(existing.vertices)[0]
        row["currentRightComparison"]=dict(triangles=len(existing.faces),bounds=existing.bounds.tolist(),
            maxVertexDistanceMM=float(max(distances.max(),reverse.max())*1000),
            medianSourceVertexDistanceMM=float(np.median(distances)*1000),
            sameFaceCount=len(mesh.faces)==len(existing.faces))
    rows.append(row)
with (run/"forearm-trimesh.json").open("x",encoding="utf8") as out:
    json.dump(dict(status="passed",rows=rows,limitations="Proximity/vertex agreement is not anatomical acceptance. No pin coordinates transferred."),out,indent=2)
print(json.dumps(rows))

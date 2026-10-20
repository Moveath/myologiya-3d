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
out = root / "build_stage6/left_forearm_v1"
mapping = {"radius_left": "FMA23465", "ulna_left": "FMA23468",
           "humerus_left": "FMA23131", "scaphoid_left": "FMA24436", "lunate_left": "FMA24438"}

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

sources = {}
rows = []
for bone, fma in mapping.items():
    mesh = trimesh.load(cache / (fma + ".obj"), force="mesh", process=False)
    mesh.vertices = mesh.vertices[:, [0, 2, 1]] * np.array([1, 1, -1]) / 1000
    sources[bone] = mesh
    if bone not in ("radius_left", "ulna_left"):
        continue
    target = world_meshes(trimesh.load(out / (bone + ".glb"), force="scene", process=False))["b|" + bone]
    result = compare(mesh, target)
    assert result["sourceTriangles"] == result["targetTriangles"]
    assert result["maxNearestVertexMM"] < 0.001
    assert result["orderedTriangleCornersWithin0002MM"]
    normals = target.vertex_normals
    weld = target.copy()
    weld.merge_vertices()
    rows.append(dict(id=bone, **result, bounds=target.bounds.tolist(),
                     vertices=len(target.vertices), finite=bool(np.isfinite(target.vertices).all()),
                     normalsFinite=bool(np.isfinite(normals).all()),
                     minNormalLength=float(np.linalg.norm(normals, axis=1).min()),
                     degenerateFaces=int((target.area_faces < 1e-15).sum()),
                     duplicateFaces=int(len(weld.faces)-len(np.unique(np.sort(weld.faces,axis=1),axis=0))),
                     watertight=bool(weld.is_watertight), windingConsistent=bool(weld.is_winding_consistent),
                     positiveVolume=bool(weld.volume>0), positiveX=bool(target.bounds[0,0]>0)))

existing = world_meshes(trimesh.load(io.BytesIO(base64.b64decode((root/"site/arm-extra-q-glb.txt").read_bytes())),
                                   file_type="glb",force="scene",process=False))["b|humerus_left"]
alignment = compare(sources["humerus_left"], existing)
assert alignment["maxNearestVertexMM"] < 0.1
controls = {}
deadline = time.monotonic() + 120
for a, b in [("radius_left","ulna_left"),("radius_left","humerus_left"),
             ("ulna_left","humerus_left"),("radius_left","scaphoid_left"),("radius_left","lunate_left")]:
    # Nearest-triangle distances at all source vertices; not accepted joint contours.
    chunks = []
    for v in np.array_split(sources[a].vertices, max(1, len(sources[a].vertices)//24)):
        if time.monotonic() > deadline:
            with (run/"trimesh-partial.json").open("x",encoding="utf8") as f:
                json.dump(dict(status="incomplete",rows=rows,completedAdjacency=controls,
                               reason="120 second adjacency budget exceeded"),f,indent=2)
            raise TimeoutError("120 second adjacency budget exceeded; partial evidence saved")
        chunks.append(trimesh.proximity.closest_point_naive(sources[b], v))
    closest, distances = np.concatenate([c[0] for c in chunks]), np.concatenate([c[1] for c in chunks])
    k = int(distances.argmin())
    controls[a+"__"+b] = dict(minVertexToTriangleMM=float(distances.min()*1000),
        vertexIndex=k, diagnosticPointM=sources[a].vertices[k].tolist(),
        closestSurfaceM=closest[k].tolist(), scope="distance only, no pin or anatomical surface acceptance")

# Reuse exhaustive bounded BVH code on this small set only.
arrays = {bone:dict(vertices=m.vertices.reshape(-1).tolist(), faces=m.faces.reshape(-1).tolist())
          for bone,m in sources.items()}
arrays["existing_humerus_left"] = dict(vertices=existing.vertices.reshape(-1).tolist(),faces=existing.faces.reshape(-1).tolist())
for name,value in [("mesh-arrays.json",arrays),("trimesh-roundtrip.json",
    dict(status="passed",rows=rows,existingHumerusSourceAgreement=alignment,
         adjacencyDiagnostics=controls,registrationTransform="native shared BP3D frame, [x,z,-y]/1000; no fit/translation/reflection",
         limitation="No cartilage, full joint surface, pin localisation or clinical geometry acceptance"))]:
    with (run/name).open("x",encoding="utf8") as f:
        json.dump(value,f,indent=2)
print(json.dumps(dict(status="passed",rows=rows,humerus=alignment,distances=controls)))

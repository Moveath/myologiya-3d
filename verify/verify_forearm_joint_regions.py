"""Diagnostic end-region sampling on the existing pilot; never labels facets or pins."""
import base64
import hashlib
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(sys.argv[1]).resolve()
PILOT = ROOT / "build_stage6/left_forearm_v1"
OLD = ROOT / "research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def meshes(scene):
    result = {}
    for node in scene.graph.nodes_geometry:
        owner = node
        while owner and not owner.startswith("b|"):
            owner = scene.graph.transforms.parents.get(owner)
        matrix, key = scene.graph[node]
        mesh = scene.geometry[key].copy()
        mesh.apply_transform(matrix)
        result[owner or node] = mesh
    return result


def save(name, data):
    with (RUN / name).open("x", encoding="utf8") as stream:
        json.dump(data, stream, indent=2)


bone_meshes = {
    name: meshes(trimesh.load(PILOT / f"{name}.glb", process=False))[f"b|{name}"]
    for name in ("radius_left", "ulna_left")
}
original = ROOT / "site/arm-extra-q-glb.txt"
bone_meshes["humerus_left"] = meshes(trimesh.load(
    io.BytesIO(base64.b64decode(original.read_text().strip())),
    file_type="glb", process=False))["b|humerus_left"]

old_arrays = json.loads((OLD / "mesh-arrays.json").read_text())
checks, inventory = [], {}
for name, mesh in bone_meshes.items():
    baseline = old_arrays["existing_humerus_left" if name == "humerus_left" else name]
    old_vertices = np.asarray(baseline["vertices"]).reshape(-1, 3)
    old_faces = np.asarray(baseline["faces"]).reshape(-1, 3)
    unchanged = bool(np.array_equal(mesh.faces, old_faces) and
                     np.allclose(mesh.vertices, old_vertices, atol=2e-7, rtol=0))
    assert unchanged, f"{name}: source changed; prior intersection results not reusable"
    checks.append(dict(bone=name, previousIntersectionGeometryEquivalent=True))
    inventory[name] = dict(boundsMM=(mesh.bounds * 1000).tolist(),
                           extentMM=(mesh.extents * 1000).tolist(),
                           triangles=len(mesh.faces), vertices=len(mesh.vertices))
save("geometry-inputs.json", dict(
    files={str(p.relative_to(ROOT)): digest(p) for p in
           [original, PILOT / "radius_left.glb", PILOT / "ulna_left.glb"]},
    checks=checks, inventory=inventory,
    limitation="Y extent is not an anatomical bone length; source pose is unchanged."))
save("current-mesh-arrays.json", {
    name: dict(vertices=m.vertices.tolist(), faces=m.faces.tolist())
    for name, m in bone_meshes.items()
})

# A deterministic 15% axial window isolates diagnostic ends, NOT articular facets.
def end_faces(mesh, end):
    lo, hi = mesh.bounds[:, 1]
    y = mesh.triangles_center[:, 1]
    mask = y >= hi - .15 * (hi - lo) if end == "proximal" else y <= lo + .15 * (hi - lo)
    return np.flatnonzero(mask)


def sample_pair(label, source_name, target_name, end):
    source, target = bone_meshes[source_name], bone_meshes[target_name]
    ids = end_faces(source, end)
    # Max 80 reproducible triangle-centroid samples; no dense or exact distance claim.
    ids = ids[np.linspace(0, len(ids)-1, min(80, len(ids)), dtype=int)]
    queries = source.triangles_center[ids]
    locations, distances, faces = [], [], []
    start = time.monotonic()
    for chunk in np.array_split(queries, max(1, (len(queries)+7)//8)):
        if time.monotonic() - start > 30:
            raise TimeoutError(f"{label}: 30-second budget exceeded")
        q, d, f = trimesh.proximity.closest_point_naive(target, chunk)
        locations.extend(q.tolist())
        distances.extend(d.tolist())
        faces.extend(f.tolist())
    distances = np.asarray(distances)
    dots = np.einsum("ij,ij->i", source.face_normals[ids], target.face_normals[faces])
    return dict(
        diagnosticPair=label, source=source_name, target=target_name,
        axialWindow=end, fraction=.15, samples=len(ids),
        sourceFaceIds=ids.tolist(), targetFaceIds=faces,
        distanceQuantilesMM=dict(zip(["min", "p25", "median", "p75", "max"],
                                    (np.quantile(distances, [0, .25, .5, .75, 1])*1000).tolist())),
        sampledCentroids=queries.tolist(), nearestTargetPoints=locations,
        normalDotProducts=dots.tolist(), elapsedSeconds=time.monotonic()-start,
        anatomicalFacetSegmentation=False, jointSpaceMeasurement=False,
        limitation="Nearest bone surface may be non-articular. No clinical threshold or pin created.")


for label, source, target, end in [
    ("radiocapitellar-region", "radius_left", "humerus_left", "proximal"),
    ("humeroulnar-region", "ulna_left", "humerus_left", "proximal"),
    ("proximal-radioulnar-region", "radius_left", "ulna_left", "proximal"),
    ("distal-radioulnar-region", "ulna_left", "radius_left", "distal"),
]:
    result = sample_pair(label, source, target, end)
    save(label + ".json", result)
    print(json.dumps({k: result[k] for k in
                      ("diagnosticPair", "samples", "distanceQuantilesMM", "elapsedSeconds")}))

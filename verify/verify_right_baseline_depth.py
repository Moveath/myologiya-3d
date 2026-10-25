"""Contralateral baseline: the remaining20 depth diagnostic on the accepted right hand/foot.

The penetration algorithm is copied unchanged from verify_remaining20_depth.py (winding of
vertices and face centres, nearest-triangle sampled depth). Inputs are the saved read-only
arrays of the live r170 assets; their hashes must still match site/*.txt. No mesh is changed.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import trimesh

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
read = lambda p: json.loads(Path(p).read_text(encoding="utf8"))
source_run = root/"research/evidence-runs/stage6-mirror-screen-2026-10-20T12-05-47-925Z-TQbeVF"
for asset in read(source_run/"right-source-assets.json"):
    assert hashlib.sha256((root/asset["file"]).read_bytes()).hexdigest() == asset["sha256"], asset["file"]
arrays = read(source_run/"right-source-arrays.json")
FOOT = [("talus", "calcaneus"), ("talus", "navicular"), ("talus", "tibia"), ("talus", "fibula"),
        ("calcaneus", "cuboid"), ("cuboid", "navicular"), ("cuboid", "cuneiform_lat"),
        ("navicular", "cuneiform_med"), ("navicular", "cuneiform_int"), ("navicular", "cuneiform_lat"),
        ("cuneiform_med", "cuneiform_int"), ("cuneiform_int", "cuneiform_lat"),
        ("cuneiform_med", "metatarsal_1"), ("cuneiform_med", "metatarsal_2"), ("cuneiform_int", "metatarsal_2"),
        ("cuneiform_lat", "metatarsal_2"), ("cuneiform_lat", "metatarsal_3"), ("cuneiform_lat", "metatarsal_4"),
        ("cuboid", "metatarsal_4"), ("cuboid", "metatarsal_5"),
        ("metatarsal_1", "metatarsal_2"), ("metatarsal_2", "metatarsal_3"), ("metatarsal_3", "metatarsal_4"),
        ("metatarsal_4", "metatarsal_5"), ("metatarsal_1", "sesamoid_pedis"),
        ("metatarsal_1", "toe_prox_1"), ("toe_prox_1", "toe_dist_1"), ("metatarsal_2", "toe_prox_2"),
        ("metatarsal_3", "toe_prox_3"), ("metatarsal_4", "toe_prox_4"), ("metatarsal_5", "toe_prox_5"),
        ("toe_prox_5", "toe_mid_5"), ("toe_mid_5", "toe_dist_5")]
HAND = [("metacarpal_1", "trapezium"), ("metacarpal_1", "trapezoid"), ("metacarpal_1", "metacarpal_2"),
        ("metacarpal_1", "phalanx_prox_1"), ("metacarpal_3", "capitate"), ("metacarpal_3", "trapezoid"),
        ("metacarpal_2", "metacarpal_3"), ("metacarpal_3", "metacarpal_4"), ("metacarpal_3", "phalanx_prox_3")]
pairs = [("leg-glb.txt:"+a, "leg-glb.txt:"+b) for a, b in FOOT]+[("arm-glb.txt:"+a, "arm-glb.txt:"+b) for a, b in HAND]
meshes = {k: trimesh.Trimesh(np.array(arrays[k]["vertices"]).reshape(-1, 3),
                             np.array(arrays[k]["faces"]).reshape(-1, 3), process=False)
          for k in dict.fromkeys(x for p in pairs for x in p)}


def depth(x, y, limit=600):
    start = time.monotonic()
    points = np.concatenate([meshes[x].vertices, meshes[x].triangles_center])
    bounds, triangles = meshes[y].bounds, meshes[y].triangles
    candidate = np.where(np.all((points >= bounds[0]) & (points <= bounds[1]), axis=1))[0]
    inside, complete = [], True
    for i in range(0, len(candidate), 16):
        if time.monotonic()-start > limit:
            complete = False
            break
        indices = candidate[i:i+16]
        v = triangles[None]-points[indices, None, None, :]
        u, w, z = v[:, :, 0], v[:, :, 1], v[:, :, 2]
        lu, lw, lz = [np.linalg.norm(s, axis=2) for s in (u, w, z)]
        dot = lambda a, b: np.einsum("ijk,ijk->ij", a, b)
        n = dot(u, np.cross(w, z))
        den = lu*lw*lz+dot(u, w)*lz+dot(w, z)*lu+dot(z, u)*lw
        winding = np.sum(2*np.arctan2(n, den), axis=1)/(4*np.pi)
        inside.extend(indices[np.abs(winding) > .5].tolist())
    distances = []
    for i in range(0, len(inside), 16):
        distances.extend(trimesh.proximity.closest_point_naive(meshes[y], points[inside[i:i+16]])[1])
    faces = [i-len(meshes[x].vertices) for i in inside if i >= len(meshes[x].vertices)]
    row = dict(a=x, b=y, complete=complete, candidateSamples=len(candidate),
               allVerticesAndFaceCentres=len(points), insideSamples=len(inside),
               maxSamplePenetrationMM=float(max(distances, default=0)*1000),
               affectedSourceFaces=len(faces), durationSeconds=time.monotonic()-start)
    if faces:
        row["diagnosticPatchAreaMM2"] = float(meshes[x].area_faces[faces].sum()*1e6)
    return row


rows = []
for a, b in pairs:
    for x, y in [(a, b), (b, a)]:
        rows.append(depth(x, y))
    print(json.dumps(dict(pair=[a, b], depthMM=[round(r["maxSamplePenetrationMM"], 3) for r in rows[-2:]])), flush=True)
summary = dict(rows=rows, sourceArrays=(source_run/"right-source-arrays.json").relative_to(root).as_posix(),
               method="Identical to verify_remaining20_depth.py on accepted right live r170 assets. "
                      "Not a continuous maximum, medical tolerance, cartilage mask or acceptance.")
with (run/"right-baseline-depth.json").open("x", encoding="utf8") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(dict(status="passed" if all(r["complete"] for r in rows) else "incomplete", directions=len(rows))))

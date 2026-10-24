"""Local penetration diagnostics with exact-input reuse and bounded checkpoints."""
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
arrays = read(run/"comparison-arrays.json")
signature = lambda a: hashlib.sha256(np.asarray(a["vertices"], dtype="<f8").tobytes()
                                    +np.asarray(a["faces"], dtype="<u4").tobytes()).hexdigest()
hashes = {k: signature(v) for k, v in arrays.items()}
prior_names = [
    "stage6-mirror-upper-v2-2026-10-20T12-11-27-299Z-T0jfz0",
    "stage6-mirror-lower-v2-2026-10-20T12-11-27-305Z-5rXqo2",
    "stage6-mirror-toe5-repair-2026-10-20T12-20-59-021Z-ZBXbnc",
    "stage6-left-metatarsals-2026-10-20T11-37-52-033Z-JqSVPJ",
    "stage6-left-tarsals-2026-10-20T11-22-52-873Z-6rEIlo"]
cached = {}
for name in prior_names:
    d = root/"research/evidence-runs"/name
    old = read(d/"mesh-arrays.json")
    if not (d/"bounded-penetration.json").exists():
        continue
    for row in read(d/"bounded-penetration.json")["rows"]:
        if row["complete"]:
            cached[(signature(old[row["a"]]), signature(old[row["b"]]))] = (
                row, (d/f'penetration-{row["a"]}-{row["b"]}.json').relative_to(root).as_posix())
meshes = {k: trimesh.Trimesh(np.array(a["vertices"]).reshape(-1, 3),
                            np.array(a["faces"]).reshape(-1, 3), process=False) for k, a in arrays.items()}
results = []
new, reused = 0, 0
for pair in read(run/"comparison-pairs.json")["cross"]:
    if not (pair["counts"].get("crossing") or pair["counts"].get("coplanarOverlap")):
        continue
    for x, y in [(pair["a"], pair["b"]), (pair["b"], pair["a"])]:
        out = run/f"depth-{x}-{y}.json"
        if out.exists():
            results.append(read(out))
            continue
        start = time.monotonic()
        points = np.concatenate([meshes[x].vertices, meshes[x].triangles_center])
        key = hashes[x], hashes[y]
        if key in cached:
            old, evidence = cached[key]
            row = {**old, "a": x, "b": y, "reusedFrom": evidence}
            reused += 1
        else:
            bounds, triangles = meshes[y].bounds, meshes[y].triangles
            candidate = np.where(np.all((points >= bounds[0]) & (points <= bounds[1]), axis=1))[0]
            inside, complete = [], True
            for i in range(0, len(candidate), 16):
                if time.monotonic()-start > 35:
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
                if time.monotonic()-start > 45:
                    complete = False
                    break
                distances.extend(trimesh.proximity.closest_point_naive(meshes[y], points[inside[i:i+16]])[1])
            faces = [i-len(meshes[x].vertices) for i in inside if i >= len(meshes[x].vertices)]
            row = dict(a=x, b=y, complete=complete, candidateSamples=len(candidate),
                       allVerticesAndFaceCentres=len(points), insideSamples=len(inside),
                       maxSamplePenetrationMM=float(max(distances, default=0)*1000),
                       affectedSourceFaces=faces, durationSeconds=time.monotonic()-start)
            new += 1
        faces = row["affectedSourceFaces"]
        if faces:
            q = meshes[x].triangles_center[faces]
            row["diagnosticPatchBounds"] = [q.min(axis=0).tolist(), q.max(axis=0).tolist()]
            row["diagnosticPatchAreaMM2"] = float(meshes[x].area_faces[faces].sum()*1e6)
        row["patchIsNotAnatomicalSurfaceMask"] = True
        with out.open("x", encoding="utf8") as f:
            json.dump(row, f, indent=2)
        results.append(row)
        if new and new % 10 == 0:
            print(json.dumps(dict(new=new, reused=reused, saved=len(results))), flush=True)
summary = dict(rows=results, newDirections=new, reusedDirections=reused,
               method="Solid-angle winding of vertices and face centres; nearest-triangle sampled depth. "
                      "Not a continuous maximum, medical tolerance, cartilage mask or acceptance.")
with (run/"comparison-depth.json").open("x", encoding="utf8") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(dict(status="passed" if all(r["complete"] for r in results) else "incomplete",
                      new=new, reused=reused, directions=len(results))))

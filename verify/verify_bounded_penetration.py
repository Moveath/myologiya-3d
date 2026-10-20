"""Bounded winding diagnostics. AABB filtering excludes only impossible inside points."""
import json
import pathlib
import sys
import time
import numpy as np
import trimesh

run = pathlib.Path(sys.argv[1])
arrays = json.loads((run / "mesh-arrays.json").read_text())
meshes = {
    key: trimesh.Trimesh(np.array(a["vertices"]).reshape(-1, 3),
                        np.array(a["faces"]).reshape(-1, 3), process=False)
    for key, a in arrays.items()
}
pairs = [p for p in json.loads((run / "joint-intersections.json").read_text())["cross"]
         if p["counts"].get("crossing") or p["counts"].get("coplanarOverlap")]
results = []
for pair in pairs:
    for x, y in [(pair["a"], pair["b"]), (pair["b"], pair["a"])]:
        output = run / f"penetration-{x}-{y}.json"
        if output.exists():
            results.append(json.loads(output.read_text()))
            continue
        start = time.monotonic()
        points = np.concatenate([meshes[x].vertices, meshes[x].triangles_center])
        bounds = meshes[y].bounds
        candidate = np.where(np.all((points >= bounds[0]) & (points <= bounds[1]), axis=1))[0]
        triangles = meshes[y].triangles
        inside = []
        complete = True
        for i in range(0, len(candidate), 16):
            if time.monotonic() - start > 60:
                complete = False
                break
            indices = candidate[i:i + 16]
            v = triangles[None] - points[indices, None, None, :]
            u, w, z = v[:, :, 0], v[:, :, 1], v[:, :, 2]
            lu, lw, lz = [np.linalg.norm(s, axis=2) for s in (u, w, z)]
            dot = lambda a, b: np.einsum("ijk,ijk->ij", a, b)
            n = dot(u, np.cross(w, z))
            d = lu * lw * lz + dot(u, w) * lz + dot(w, z) * lu + dot(z, u) * lw
            winding = np.sum(2 * np.arctan2(n, d), axis=1) / (4 * np.pi)
            inside.extend(indices[np.abs(winding) > .5].tolist())
        distances = []
        for i in range(0, len(inside), 16):
            if time.monotonic() - start > 75:
                complete = False
                break
            distances.extend(trimesh.proximity.closest_point_naive(
                meshes[y], points[inside[i:i + 16]])[1].tolist())
        row = dict(a=x, b=y, complete=complete, candidateSamples=len(candidate),
                   allVerticesAndFaceCentres=len(points), insideSamples=len(inside),
                   maxSamplePenetrationMM=max(distances, default=0) * 1000,
                   affectedSourceFaces=[i - len(meshes[x].vertices) for i in inside
                                        if i >= len(meshes[x].vertices)],
                   durationSeconds=time.monotonic() - start)
        with output.open("x") as f:
            json.dump(row, f, indent=2)
        results.append(row)
        print(json.dumps({k: v for k, v in row.items() if k != "affectedSourceFaces"}), flush=True)
with (run / "bounded-penetration.json").open("x") as f:
    json.dump(dict(rows=results, method="AABB-filtered solid-angle winding; all vertices and face centres. "
                   "Sampled depth only, not exact continuous maximum or physiological threshold."), f, indent=2)

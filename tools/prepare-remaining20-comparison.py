"""Compare authored-left and reflected candidates in the unchanged atlas frame."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import trimesh

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
read = lambda p: json.loads(Path(p).read_text(encoding="utf8"))
config = read(run / "batch.json")
atlas = read(run / "atlas-before.json")
prior = root / "research/evidence-runs"
upper = prior / "stage6-mirror-upper-v2-2026-10-20T12-11-27-299Z-T0jfz0"
lower = prior / "stage6-mirror-lower-v2-2026-10-20T12-11-27-305Z-5rXqo2"
repair = prior / "stage6-mirror-toe5-repair-2026-10-20T12-20-59-021Z-ZBXbnc"
mirror = {**read(upper / "mesh-arrays.json"), **read(lower / "mesh-arrays.json")}
mirror["toe_dist_5_left"] = read(repair / "mesh-arrays.json")["toe_dist_5_left"]
arrays, metadata, quality = {}, {}, []

def add(key, bone, variant, mesh, source):
    arrays[key] = dict(vertices=mesh.vertices.flatten().tolist(), faces=mesh.faces.flatten().tolist())
    metadata[key] = dict(owner=bone, variant=variant, source=source,
                         region="arm" if bone.startswith("metacarpal") else "leg",
                         bounds=mesh.bounds.tolist())

for bone, fma in config["targets"].items():
    file = root / "research/cache/stage6-sources" / (fma + ".obj")
    m = trimesh.load(file, force="mesh", process=False)
    m.vertices = m.vertices[:, [0, 2, 1]] * [1, 1, -1] / 1000
    add("native__" + bone, bone, "authored_left", m, dict(
        file=file.relative_to(root).as_posix(), sha256=hashlib.sha256(file.read_bytes()).hexdigest(), fma=fma))
    w = m.copy()
    w.merge_vertices()
    quality.append(dict(id=bone, faces=len(m.faces), bounds=m.bounds.tolist(),
                        extentsMM=(m.extents*1000).tolist(),
                        degenerate=int((m.area_faces < 1e-15).sum()),
                        duplicate=int(len(w.faces)-len(np.unique(np.sort(w.faces, axis=1), axis=0))),
                        watertight=bool(w.is_watertight), winding=bool(w.is_winding_consistent),
                        positiveVolume=bool(w.volume > 0),
                        components=len(w.split(only_watertight=False, repair=False))))
    a = mirror[bone]
    m = trimesh.Trimesh(np.array(a["vertices"]).reshape(-1, 3),
                        np.array(a["faces"]).reshape(-1, 3), process=False)
    source = repair if bone == "toe_dist_5_left" else upper if bone.startswith("metacarpal") else lower
    add("mirror__" + bone, bone, "mirrored_right", m, str(source.relative_to(root)))

for bone, b in atlas["bones"].items():
    if not bone.endswith("_left") or b.get("noModel") or not b.get("modelFile"):
        continue
    region = b.get("modelFile", "")
    if any(x in region for x in ["forearm", "carpal", "phalang"]) and not bone.startswith("toe_"):
        group = "arm"
    elif any(x in region for x in ["tarsal", "mirrored-left-foot"]) or bone in ["tibia_left", "fibula_left"]:
        group = "leg"
    else:
        continue
    file = root / "site" / b["modelFile"]
    scene = trimesh.load(file, force="scene", process=False)
    meshes = []
    for node in scene.graph.nodes_geometry:
        transform, name = scene.graph[node]
        m = scene.geometry[name].copy()
        m.apply_transform(transform)
        meshes.append(m)
    m = trimesh.util.concatenate(meshes)
    key = "live__" + bone
    add(key, bone, "working_model", m, dict(
        file=file.relative_to(root).as_posix(), sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    metadata[key]["region"] = group

for file, value in [("comparison-arrays.json", arrays), ("comparison-metadata.json", metadata),
                    ("authored-left-quality.json", quality)]:
    with (run/file).open("x", encoding="utf8") as f:
        json.dump(value, f, ensure_ascii=False)
print(json.dumps(dict(candidates=len(config["targets"])*2, controls=len(metadata)-len(config["targets"])*2,
                      nativeIssues=[x for x in quality if x["degenerate"] or x["duplicate"] or not x["winding"]])))

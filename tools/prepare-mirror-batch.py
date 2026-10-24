"""Prepare bounded paired-bone candidates from decoded, immutable atlas assets."""
import hashlib
import json
import pathlib
import sys
import numpy as np
import trimesh

root = pathlib.Path(__file__).resolve().parents[1]
screen, run, region = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
assert region in ("upper", "lower")
atlas = json.loads((screen/"atlas-before.json").read_text())
source = json.loads((screen/"right-source-arrays.json").read_text())
filename = "arm-glb.txt" if region == "upper" else "leg-glb.txt"
right = {r["id"]: r for r in source.values() if r["file"] == filename}
targets = {b: b.removesuffix("_left") for b, d in atlas["bones"].items()
           if d.get("noModel") and b.endswith("_left") and b.removesuffix("_left") in right}
assert len(targets) == (2 if region == "upper" else 24), targets
arrays = {}
for left, original in targets.items():
    row = right[original]
    v = np.array(row["vertices"]).reshape(-1, 3)
    f = np.array(row["faces"]).reshape(-1, 3)
    assert v[:, 0].max() < 0, left
    # Bake reflection and reversed winding, not a negative object scale.
    arrays[left] = dict(vertices=(v*[-1, 1, 1]).flatten().tolist(),
                        faces=f[:, [0, 2, 1]].flatten().tolist())
controls = {}
for b, d in atlas["bones"].items():
    if not b.endswith("_left") or d.get("noModel") or not d.get("modelFile"):
        continue
    counterpart = b.removesuffix("_left")
    if counterpart not in right or counterpart in ("humerus", "femur", "patella"):
        continue
    file = root/"site"/d["modelFile"]
    scene = trimesh.load(file, force="scene", process=False)
    vs, fs = [], []
    for node in scene.graph.nodes_geometry:
        matrix, key = scene.graph[node]
        m = scene.geometry[key].copy()
        m.apply_transform(matrix)
        fs.extend((m.faces+len(vs)).tolist())
        vs.extend(m.vertices.tolist())
    arrays[b] = dict(vertices=np.array(vs).flatten().tolist(), faces=np.array(fs).flatten().tolist())
    controls[b] = dict(file=d["modelFile"], sha256=hashlib.sha256(file.read_bytes()).hexdigest())
output = "build_stage6/mirror_"+region+"_"+(sys.argv[4] if len(sys.argv)>4 else "v1")
config = dict(region=region, output=output, targets=targets, controls=controls,
    sourceAsset="site/"+filename, sourceAssetSha256=hashlib.sha256((root/"site"/filename).read_bytes()).hexdigest(),
    plane=dict(normal=[1,0,0],offset=0,space="atlas Y-up metres",
        scope="Educational skeleton frame, independently screened against bilateral and central bones; not exact patient plane"),
    sourceScreen=str(screen.relative_to(root)).replace("\\","/"),
    transform="World-space x -> -x, face (a,b,c) -> (a,c,b); no scaling, fitting, deformation or pin transform",
    license="CC BY-SA 2.1 Japan", source="BodyParts3D 3.0; existing atlas derivative, not an independent left specimen")
for name,value in [("batch.json",config),("mesh-arrays.json",arrays)]:
    with (run/name).open("x",encoding="utf8") as f:json.dump(value,f,ensure_ascii=False)
print(json.dumps(dict(targets=list(targets),controls=list(controls)),ensure_ascii=False))

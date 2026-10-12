"""Convert BodyParts3D STL (mm, Z up, -Y anterior) into one GLB for three.js.

three.js frame: x = bp.x (body right is -x), y = bp.z (up), z = -bp.y (anterior), meters.
Every mesh gets a node name:  m:<muscle>:<part> | b:<bone> | o:<other> | c:<id>
"""
import sys, json
import numpy as np
import trimesh
import fast_simplification

sys.path.insert(0, sys.argv[1])  # scripts dir
_mod = __import__(sys.argv[5] if len(sys.argv) > 5 else 'manifest')
MUSCLES, BONES, OTHER, CONTEXT = _mod.MUSCLES, _mod.BONES, _mod.OTHER, _mod.CONTEXT

stl_dir, out_glb, out_meta = sys.argv[2], sys.argv[3], sys.argv[4]

R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)


def load(fid, ratio, lo, hi):
    m = trimesh.load(f"{stl_dir}/{fid}.stl", process=True)
    m.merge_vertices()
    v = (m.vertices @ R.T) / 1000.0
    f = m.faces
    n = len(f)
    target = int(min(max(n * ratio, min(n, lo)), hi))
    if target < n:
        v, f = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int32),
                                            target_reduction=1 - target / n, agg=6)
    out = trimesh.Trimesh(vertices=v, faces=f, process=True)
    out.remove_unreferenced_vertices()
    return out


scene = trimesh.Scene()
meta = {"parts": {}, "stats": {}}
tot = 0


def add(name, mesh):
    global tot
    _ = mesh.vertex_normals  # smooth normals get exported
    scene.add_geometry(mesh, node_name=name, geom_name=name)
    meta["parts"][name] = {"faces": int(len(mesh.faces)),
                           "center": np.round(mesh.bounds.mean(0), 4).tolist(),
                           "size": np.round(mesh.extents, 4).tolist()}
    tot += len(mesh.faces)


for key, parts in MUSCLES.items():
    for fid, part in parts:
        add(f"m|{key}|{part or ''}", load(fid, 0.13, 1500, 14000))
import os
BONE_RATIO = float(os.environ.get("BONE_RATIO", "0.15"))
BONE_MAX = int(os.environ.get("BONE_MAX", "12000"))
for key, ids in BONES.items():
    for fid in ids:
        add(f"b|{key}", load(fid, BONE_RATIO, 1200, BONE_MAX))
for key, ids in OTHER.items():
    for fid in ids:
        add(f"o|{key}", load(fid, 0.15, 800, 6000))
for fid in CONTEXT:
    add(f"c|{fid}", load(fid, 0.05, 400, 2500))

# center on the limb (humerus+forearm region) so the orbit target is sensible
b = scene.bounds
meta["stats"] = {"faces": int(tot), "bounds": np.round(b, 4).tolist()}
scene.export(out_glb, file_type="glb", include_normals=True)
json.dump(meta, open(out_meta, "w"), indent=1)
print("faces", tot, "bounds", np.round(b, 3).tolist())

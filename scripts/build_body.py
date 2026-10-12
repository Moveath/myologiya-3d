"""Whole-body skeleton + skin as one GLB for offline rendering of the start-screen figure.
Node names: r|<region>|<fma id>  and  s|skin
"""
import sys, json
import numpy as np
import trimesh
import fast_simplification

parts_json, stl_dir, out_glb = sys.argv[1], sys.argv[2], sys.argv[3]
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
parts = json.load(open(parts_json))


def load(fid, target):
    m = trimesh.load(f"{stl_dir}/{fid}.stl", process=True)
    m.merge_vertices()
    v = (m.vertices @ R.T) / 1000.0
    f = m.faces
    if len(f) > target:
        v, f = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int32), target_reduction=1 - target / len(f), agg=5)
    out = trimesh.Trimesh(vertices=v, faces=f, process=True)
    out.remove_unreferenced_vertices()
    _ = out.vertex_normals
    return out


scene = trimesh.Scene()
tot = 0
for fid, name, region in parts:
    if region == 'skin':
        mesh = load(fid, 160000)
        scene.add_geometry(mesh, node_name='s|skin', geom_name='s|skin')
    else:
        mesh = load(fid, 9000)
        kind = 'disc' if 'intervertebral disk' in name else ('tooth' if 'tooth' in name else 'bone')
        nm = f"r|{region}|{fid}|{kind}"
        scene.add_geometry(mesh, node_name=nm, geom_name=nm)
    tot += len(mesh.faces)
scene.export(out_glb, file_type="glb", include_normals=True)
print("faces", tot, "bounds", np.round(scene.bounds, 3).tolist())

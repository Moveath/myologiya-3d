"""Exact reflection, orientation, topology and source integrity; no anatomy inference."""
import hashlib
import json
import pathlib
import sys
import struct
import numpy as np
import trimesh
root=pathlib.Path(__file__).resolve().parents[1];run=pathlib.Path(sys.argv[1])
config=json.loads((run/"batch.json").read_text(encoding="utf8"))
arrays=json.loads((run/"mesh-arrays.json").read_text())
assert hashlib.sha256((root/config["sourceAsset"]).read_bytes()).hexdigest()==config["sourceAssetSha256"]
rows=[]
for bone in config["targets"]:
    row=arrays[bone]
    expected=trimesh.Trimesh(np.array(row["vertices"]).reshape(-1,3),
                            np.array(row["faces"]).reshape(-1,3),process=False)
    file=root/config["output"]/(bone+".glb")
    data=file.read_bytes();json_length=struct.unpack_from("<I",data,12)[0]
    header=json.loads(data[20:20+json_length])
    assert len(header["scenes"])==1 and len(header["meshes"])==1, "Unselected scene content in export"
    scene=trimesh.load(file,force="scene",process=False)
    assert len(scene.graph.nodes_geometry)==1
    node=next(iter(scene.graph.nodes_geometry));transform,key=scene.graph[node]
    mesh=scene.geometry[key].copy();mesh.apply_transform(transform)
    assert np.linalg.det(transform[:3,:3])>0
    assert len(mesh.faces)==len(expected.faces)
    err=float(np.max(np.abs(mesh.triangles-expected.triangles)))
    assert err<2e-7,(bone,err)
    weld=mesh.copy();weld.merge_vertices()
    row=dict(id=bone,triangles=len(mesh.faces),roundTripMaxCornerMM=err*1000,
        watertight=bool(weld.is_watertight),windingConsistent=bool(weld.is_winding_consistent),
        volume=float(weld.volume),components=len(weld.split(only_watertight=False,repair=False)),
        degenerate=int((mesh.area_faces<1e-15).sum()),
        duplicateFaces=len(weld.faces)-len(np.unique(np.sort(weld.faces,axis=1),axis=0)),
        bounds=mesh.bounds.tolist(),extentsMM=(mesh.extents*1000).tolist(),
        determinant=float(np.linalg.det(transform[:3,:3])))
    # Report defects rather than silently repairing or admitting them.
    row["technicalPass"]=bool(row["windingConsistent"] and row["volume"]>0 and
        not row["degenerate"] and not row["duplicateFaces"] and mesh.bounds[0,0]>0)
    rows.append(row)
with (run/"trimesh-check.json").open("x",encoding="utf8") as f:
    json.dump(dict(status="passed" if all(r["technicalPass"] for r in rows) else "defects_found",rows=rows),f,indent=2)
print(json.dumps(dict(models=len(rows),rows=rows)))

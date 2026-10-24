"""Recover quantization-damaged candidate from its exact archived right OBJ."""
import hashlib
import json
import pathlib
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
root=pathlib.Path(__file__).resolve().parents[1]
parent,run=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2])
file=root/"research/cache/stage6-sources/FMA32658.obj"
m=trimesh.load(file,force="mesh",process=False)
m.vertices=m.vertices[:,[0,2,1]]*[-1,1,-1]/1000
m.faces=m.faces[:,[0,2,1]]
old=json.loads((parent/"mesh-arrays.json").read_text())
v=np.array(old["toe_dist_5_left"]["vertices"]).reshape(-1,3)
diff=max(cKDTree(v).query(m.vertices)[0].max(),cKDTree(m.vertices).query(v)[0].max())*1000
arrays={"toe_dist_5_left":dict(vertices=m.vertices.flatten().tolist(),faces=m.faces.flatten().tolist()),
    **{k:old[k] for k in ["toe_mid_5_left","toe_prox_5_left"]}}
config=dict(region="lower",targets={"toe_dist_5_left":"toe_dist_5"},
    controls={"toe_mid_5_left":"prior mirrored control","toe_prox_5_left":"prior mirrored control"},
    output="build_stage6/mirror_toe5_source_v1",sourceAsset=file.relative_to(root).as_posix(),
    sourceAssetSha256=hashlib.sha256(file.read_bytes()).hexdigest(),
    sourceId="FMA32658",license="CC BY-SA 2.1 Japan",
    transform="BP3D mm -> reflected atlas metres (-x,z,-y)/1000; reverse winding, no repair/deformation",
    sourceVersion="BodyParts3D 3.0 / 20110915 / OBJ95")
for name,data in [("batch.json",config),("mesh-arrays.json",arrays),("quantization-comparison.json",
    dict(originalTriangles=len(m.faces),publishedTriangles=len(old["toe_dist_5_left"]["faces"])//3,
         bidirectionalNearestVertexMaxMM=diff,originalRightGLBUnchanged=True,
         removedOrAddedFaces=0,anatomicalAcceptance=False))]:
    with (run/name).open("x",encoding="utf8") as f:json.dump(data,f,ensure_ascii=False)
print(json.dumps(dict(sourceTriangles=len(m.faces),maxNearestVertexMM=diff)))

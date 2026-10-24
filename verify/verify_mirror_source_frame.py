"""Screen a candidate reflection plane against existing bilateral bones; no fitting."""
import hashlib
import json
import pathlib
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = pathlib.Path(__file__).resolve().parents[1]
run = pathlib.Path(sys.argv[1])
arrays = json.loads((run / "right-source-arrays.json").read_text())
atlas = json.loads((run / "atlas-before.json").read_text())
names = dict(line.rstrip().split("\t", 1) for line in (root / "bp/all_named.tsv").read_text().splitlines())
cache = root / "research/cache/stage6-sources"
rows = []
for row in arrays.values():
    if row["file"] not in ("arm-glb.txt", "leg-glb.txt"):
        continue
    bone = row["id"]
    left = atlas["bones"].get(bone + "_left", {})
    fma = left.get("sourceId")
    if not fma or not (cache / (fma + ".obj")).exists():
        continue
    a = np.array(row["vertices"]).reshape(-1, 3)
    b = trimesh.load(cache / (fma + ".obj"), force="mesh", process=False).vertices
    b = b[:, [0, 2, 1]] * [1, 1, -1] / 1000
    reflected = a * [-1, 1, 1]
    delta = b.mean(0) - reflected.mean(0)
    da = cKDTree(b).query(reflected)[0]
    db = cKDTree(reflected).query(b)[0]
    rows.append(dict(right=bone, left=bone+"_left", sourceId=fma,
        rightBounds=a.min(0).tolist()+a.max(0).tolist(),
        leftBounds=b.min(0).tolist()+b.max(0).tolist(),
        mirrorX0CentroidDeltaMM=(delta*1000).tolist(),
        mirrorX0BidirectionalNearestVertexMaxMM=float(max(da.max(), db.max())*1000),
        mirrorX0BidirectionalNearestVertexMeanMM=float(np.mean(np.r_[da,db])*1000),
        midpointXMM=float((a.mean(0)[0]+b.mean(0)[0])*500),
        rightExtentsMM=(np.ptp(a,axis=0)*1000).tolist(),
        leftExtentsMM=(np.ptp(b,axis=0)*1000).tolist(),
        sourceSha256=hashlib.sha256((cache/(fma+".obj")).read_bytes()).hexdigest()))
result=dict(candidatePlane=dict(normal=[1,0,0],offset=0,space="atlas metres Y up"),
    method="No rigid fit or per-bone adjustment; bidirectional nearest vertices, not surface distance",
    rows=rows, anatomicalMidsagittalAcceptance=False)
with (run/"plane-screen.json").open("x",encoding="utf8") as f:
    json.dump(result,f,indent=2)
print(json.dumps([dict(id=r["right"],midXmm=round(r["midpointXMM"],3),
    deltaMM=np.round(r["mirrorX0CentroidDeltaMM"],3).tolist(),
    meanNNmm=round(r["mirrorX0BidirectionalNearestVertexMeanMM"],3),
    maxNNmm=round(r["mirrorX0BidirectionalNearestVertexMaxMM"],3)) for r in rows]))

"""Addressed identity/side/part checks, never a claim of anatomical surface acceptance."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_thorax_landmark_review import BONES,source_path
from evidence_output import write_report
rows=json.loads((ROOT/'pins_thorax/ta.json').read_text(encoding='utf8'))
selected=[r for r in rows if r['bone'].startswith('rib_') or r['bone']=='sternum']
assert len(selected)==113
names=dict(line.rstrip('\n').split('\t') for line in (ROOT/'bp/all_named.tsv').read_text(encoding='utf8').splitlines())
rib_sides=[]
for r in selected:
    if not r['bone'].startswith('rib_'):continue
    side=r['bone'].split('_')[-1]
    assert (r['p'][0]<0 if side=='right' else r['p'][0]>0),(r['bone'],r['p'])
    fid=BONES[r['bone']][0]
    assert names[fid].startswith(side+' ')
    rib_sides.append(dict(bone=r['bone'],code=r['code'],source=fid,sourceLabel=names[fid],x=r['p'][0]))
queries={};hashes={}
for fid in BONES['sternum']:
    file=source_path(fid);hashes[str(file.relative_to(ROOT))]=hashlib.sha256(file.read_bytes()).hexdigest()
    mesh=trimesh.load(file,process=False);mesh.vertices=mesh.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
    queries[fid]=SurfaceQuery(mesh)
sternum=[]
for r in selected:
    if r['bone']!='sternum':continue
    distances={fid:float(q.closest([r['p']])[1][0]) for fid,q in queries.items()}
    suffix=int(r['code'].rsplit('.',1)[1])
    expected='FMA7486' if suffix in (2,3,4) else 'FMA7487' if suffix==6 else 'FMA7488' if suffix==7 else None
    if expected:assert distances[expected]<.3,(r['code'],distances)
    sternum.append(dict(code=r['code'],nearest=min(distances,key=distances.get),distanceMm=distances,expectedPart=expected,
        limitation='Side, full surface and transition contour are not accepted from proximity.'))
report=dict(status='passed',ribMarkers=106,ribIdentities=24,sternalMarkers=7,sternalComponents=3,
    sourceHashes=hashes,ribSides=rib_sides,sternum=sternum,acceptedCoordinates=0,acceptedExtents=0)
print(write_report(report,'ribs-source-parts','source-parts.json',sys.argv[1] if len(sys.argv)>1 else None))
print(json.dumps({k:v for k,v in report.items() if k not in ('sourceHashes','ribSides','sternum')}))

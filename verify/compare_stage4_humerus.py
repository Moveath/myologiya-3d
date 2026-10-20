from pathlib import Path
import sys,json,hashlib
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'verify'))
from geometry_distance import SurfaceQuery
out=ROOT/'research/stage4-2026-10-16'
src=ROOT/'stl_thorax/FMA23130.stl'
mesh=trimesh.load(src,process=False)
mesh.vertices=(mesh.vertices@np.array([[1,0,0],[0,0,1],[0,-1,0]]).T)/1000
query=SurfaceQuery(mesh)
records=[]
for p in json.loads((ROOT/'pins/ta.json').read_text()):
    if p['id'] in ['hum_collum_chirurgicum','hum_corpus','hum_facies_anterolateralis','hum_sulcus_n_radialis']:
        _,d,_=query.closest([p['p']]);records.append(dict(id=p['id'],distance_mm=float(d[0]),p=p['p']))
report=dict(source=str(src.relative_to(ROOT)),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),faces=len(mesh.faces),measurements=records,
note='A local source for thorax context, not proof of identity with the lost historical arm_raw.glb. Coordinates unchanged.')
(out/'humerus-source-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))


"""Bounded measurements of existing specimen coordinates, not exact congruence."""
import json,pathlib,sys,numpy as np,trimesh
from scipy.spatial import cKDTree
ROOT=pathlib.Path(__file__).resolve().parents[1];run=pathlib.Path(sys.argv[1]);build=ROOT/'build_cardiovascular/bp3d-3.0-v1'
records={p.stem:json.loads(p.read_text())for p in build.glob('*.json')}
meshes={id:trimesh.load(ROOT/r['trial'],force='mesh',process=False)for id,r in records.items()}
pairs=[('cv_heart',id)for id in ['cv_a_aorta_ascending','cv_v_cava_superior','cv_v_cava_inferior','cv_valve_mitral','cv_valve_tricuspid','cv_valve_pulmonary']]
pairs += [('cv_a_aorta_ascending','cv_a_aorta_arch'),('cv_a_aorta_arch','cv_a_aorta_descending')]
metrics=[]
for a,b in pairs:
    distance=cKDTree(meshes[a].vertices).query(meshes[b].vertices)[0]
    metrics.append(dict(a=a,b=b,minimumVertexDistanceMm=float(distance.min()*1000),medianVertexDistanceMm=float(np.median(distance)*1000),meaning='Vertex proximity only; not a lumen, seam, intersection or attachment acceptance'))
result=dict(status='measured',models=len(records),triangles=sum(r['triangles']for r in records.values()),pairs=metrics,scope='Original BP3D specimen frame, no registration, deformation, reconstruction or inferred segmentation',geometryNotEstablished=['Exact luminal continuity','Wall thickness validity','Leaflet attachments and motion','Regional end-cut completeness','Absence of every triangle intersection'])
with(run/'geometry-measurements.json').open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
print(json.dumps({'models':len(records),'triangles':result['triangles'],'pairs':len(pairs)}))

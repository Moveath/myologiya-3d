"""One rigid reflection using the saved bone-only fit; no collision-based fitting."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
run=(ROOT/sys.argv[1]).resolve()
fit=json.loads((run/'bone-plane-fit.json').read_text())
old=json.loads((ROOT/'research/evidence-runs/stage7-interspinales-mirror-candidate-2026-10-22T07-10-51-528Z-2xay0X/mirror-preparation.json').read_text())
source=ROOT/old['sourceFile'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==old['sourceSHA256']
m=trimesh.load(source,force='mesh',process=False)
q=fit['commonFits'][0];n=np.array(q['normal']);d=q['worldPlaneConstantMM']/1000
R=np.eye(3)-2*np.outer(n,n)
v=m.vertices@R.T+2*d*n;f=m.faces[:,[0,2,1]];normals=m.vertex_normals@R.T
mesh=trimesh.Trimesh(v,f,vertex_normals=normals,process=False)
out=ROOT/'build_stage7/interspinales_localplane_v1';out.mkdir(exist_ok=True)
target=out/'interspinales_cervicis_left-local-plane-trial.glb'
s=trimesh.Scene();s.add_geometry(mesh,node_name='m|interspinales_cervicis_left|',geom_name='m|interspinales_cervicis_left|')
raw=s.export(file_type='glb')
if target.exists(): assert target.read_bytes()==raw, 'Never overwrite a different derivative'
else:
 with target.open('xb')as h:h.write(raw)
back=trimesh.load(target,force='mesh',process=False)
checks=dict(sourceHash=sha(source)==old['sourceSHA256'],exactFloat32Vertices=np.array_equal(back.vertices,v.astype(np.float32).astype(float)),
            faces=np.array_equal(back.faces,f),watertight=bool(back.is_watertight),winding=bool(back.is_winding_consistent),
            normals=bool(np.max(abs(back.vertex_normals-normals))<.001),area=bool(np.isclose(back.area,m.area,rtol=1e-4)),
            volume=bool(np.isclose(back.volume,m.volume,rtol=1e-4)),rigidReflection=bool(np.allclose(R.T@R,np.eye(3))))
assert all(checks.values()),checks
record={**old,'id':'interspinales-local-plane-candidate-left','file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),
        'method':'One rigid reflection about a plane fitted to C2-C7 bones only. No change to muscle shape, no per-bundle shift and no fitting to collisions.',
        'checks':checks,'exportDiagnostics':{'maxNormalComponentDifference':float(np.max(abs(back.vertex_normals-normals))),
            'normalNote':'Float32 vertex quantization and loader normal recalculation; unit-vector component tolerance 0.001 is technical, not anatomical.',
            'verticesAcrossFittedPlane':int((back.vertices@n<d).sum()),'minimumSignedDistanceMM':float(((back.vertices@n-d)*1000).min())},
        'plane':{'normal':n.tolist(),'worldConstantM':d,'fitEvidence':(run/'bone-plane-fit.json').relative_to(ROOT).as_posix(),
                               'anatomicalValidation':False,'uncertainty':fit['uncertainty']}}
record['candidates']=[dict(id='local-plane-left-trial',file=record['file'],sha=record['sha256'])]
for p in [run/'mirror-preparation.json',out/'provenance.json']:
 with p.open('x',encoding='utf8')as h:json.dump(record,h,ensure_ascii=False,indent=2)
with(out/'ATTRIBUTION.txt').open('x',encoding='utf8')as h:
 h.write('BodyParts3D 3.0 / FMA71309, copyright DBCLS, CC BY-SA 2.1 Japan.\nhttps://creativecommons.org/licenses/by-sa/2.1/jp/\nDerivative Myology 3D 2026: rigid reflection of admitted right C2-C7 components about bone-fitted plane; winding/normals reflected. Shape and scale preserved.\nRESEARCH ONLY: plane not independently labelled anatomical; exact attachments and C7-T1 missing. Attribution and ShareAlike retained.\n')
print(json.dumps(dict(file=record['file'],checks=len(checks),admitted=False)))

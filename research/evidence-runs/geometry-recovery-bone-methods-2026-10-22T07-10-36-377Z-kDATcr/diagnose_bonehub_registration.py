"""One shared rigid/similarity diagnostic. Never move or replace application meshes."""
import json, pathlib
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT=pathlib.Path(__file__).resolve().parent
old=ROOT.parent/'stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj/comparison-arrays.json'
bp=json.loads(old.read_text())
controls=['trapezium_left','trapezoid_left','capitate_left','metacarpal_2_left','metacarpal_4_left']
def cloud(key):return np.array(bp['live__'+key]['vertices']).reshape(-1,3)*1000
def candidate(key):return trimesh.load(ROOT/'bonehub-candidates'/f'{key.upper()}.stl',force='mesh',process=True)
def center(v):return (v.min(axis=0)+v.max(axis=0))/2
X=np.array([center(candidate(k).vertices) for k in controls])
Y=np.array([center(cloud(k)) for k in controls])
xc,yc=X.mean(axis=0),Y.mean(axis=0)
U,S,Vt=np.linalg.svd((X-xc).T@(Y-yc))
D=np.eye(3);D[-1,-1]=np.linalg.det(U@Vt)
R=U@D@Vt
models=[]
for mode,scale in [('rigid',1.0),('similarity',float(np.sum(S*np.diag(D))/np.sum((X-xc)**2)))]:
    t=yc-scale*xc@R
    residuals=np.linalg.norm(scale*X@R+t-Y,axis=1)
    models.append({'mode':mode,'scale':scale,'rotation_for_row_vectors':R.tolist(),'rotation_determinant':float(np.linalg.det(R)),'translation_mm':t.tolist(),'control_residuals_mm':dict(zip(controls,residuals.tolist())),'rms_center_residual_mm':float(np.sqrt(np.mean(residuals**2))), 'transformed_controls':[]})
    for key in controls:
        v=np.asarray(candidate(key).vertices)*scale@R+t
        q=cloud(key)
        # nearest sampled vertex is only diagnostic; it is not exact distance to surface.
        dist=cKDTree(q).query(v)[0]
        models[-1]['transformed_controls'].append({'id':key,'median_nearest_vertex_mm':float(np.median(dist)),'p95_nearest_vertex_mm':float(np.quantile(dist,.95))})
out={'source_commit':'7d520ffe410b3f79d82991b8368b2d51844feb80','source_coordinate_header':'3D Slicer output. SPACE=LPS','target':'existing Three world coordinates *1000; diagnostic only','method':'Least-squares registration of five unlabelled geometric AABB centers. One transform per region, positive determinant; no per-bone pose fitting or deformation. BBox centers are not anatomical landmarks. Similarity is diagnostic only, not admitted subject scaling.','models':models,'decision':'Not integrated. A different subject/pose is not interchangeable by center fit; anatomy and joint surfaces need separate review. No threshold converts these residuals to admission.'}
with (ROOT/'bonehub-registration-diagnostic.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps([{'mode':m['mode'],'scale':m['scale'],'rms_mm':m['rms_center_residual_mm'],'residuals_mm':m['control_residuals_mm']} for m in models],indent=2))

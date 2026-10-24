"""Shape-based rigid test alignment. Neighbours never enter the optimisation objective."""
import json, pathlib, time, hashlib, sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT=pathlib.Path(__file__).resolve().parent
PREV=ROOT.parent/'geometry-recovery-bone-methods-2026-10-22T07-10-36-377Z-kDATcr'
OLD=ROOT.parent/'stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj'
arrays=json.loads((OLD/'comparison-arrays.json').read_text())
owner=sys.argv[1]
assert owner in ['metacarpal_1_left','metacarpal_3_left']
deadline=time.monotonic()+50
def guard():
    if time.monotonic()>deadline:raise TimeoutError('50-second per-owner registration limit')
def native(key):
    a=arrays[key];return trimesh.Trimesh(np.array(a['vertices']).reshape(-1,3)*1000,np.array(a['faces']).reshape(-1,3),process=False)
sourcefile=PREV/'bonehub-candidates'/f'{owner.upper()}.stl'
source=trimesh.load(sourcefile,force='mesh',process=True)
target=native('native__'+owner)
carpals=['trapezium_left'] if owner=='metacarpal_1_left' else ['capitate_left','trapezoid_left']
scarp=np.mean([trimesh.load(PREV/'bonehub-candidates'/f'{c.upper()}.stl',force='mesh',process=True).vertices.mean(axis=0) for c in carpals],axis=0)
tcarp=np.mean([native('live__'+c).vertices.mean(axis=0) for c in carpals],axis=0)

def samples(mesh,count,seed):
    rng=np.random.default_rng(seed);idx=rng.choice(len(mesh.faces),size=count,p=mesh.area_faces/mesh.area)
    uv=rng.random((count,2));over=uv.sum(1)>1;uv[over]=1-uv[over]
    t=mesh.triangles[idx]
    return t[:,0]+uv[:,0,None]*(t[:,1]-t[:,0])+uv[:,1,None]*(t[:,2]-t[:,0])
def basis(points,carpal):
    c=points.mean(0);_,_,vt=np.linalg.svd(points-c,full_matrices=False);b=vt.T
    if np.dot(b[:,0],c-carpal)<0:b[:,0]*=-1
    b[:,2]=np.cross(b[:,0],b[:,1]);return c,b
def rigid(x,y):
    xc=x.mean(0);yc=y.mean(0);u,_,vt=np.linalg.svd((x-xc).T@(y-yc));d=np.eye(3);d[-1,-1]=np.linalg.det(u@vt);r=u@d@vt
    return r,yc-xc@r
sp=samples(source,3200,62);tp=samples(target,5000,63)
sc,sb=basis(sp,scarp);tc,tb=basis(tp,tcarp)
def subset(points,c,b,mode):
    if mode=='whole':return points
    v=(points-c)@b[:,0];lo,hi=np.quantile(v,[.20,.80]);return points[(v>=lo)&(v<=hi)]
fits=[]
for mode in ['whole','shaft60']:
    ss=subset(sp,sc,sb,mode);tt=subset(tp,tc,tb,mode);tree=cKDTree(tt)
    for angle in [0,90,180,270]:
        guard();a=np.deg2rad(angle);rot=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
        R=sb@rot@tb.T;t=tc-sc@R
        prev=None
        for iteration in range(55):
            guard();moved=ss@R+t;dist,idx=tree.query(moved)
            # Symmetric point-cloud ICP; no joint gap objective and no scale fit.
            reverse=cKDTree(moved);rd,ridx=reverse.query(tt)
            x=np.concatenate([moved, moved[ridx]]);y=np.concatenate([tt[idx],tt])
            err=np.concatenate([dist,rd]);use=err<=np.quantile(err,.90)
            dR,dt=rigid(x[use],y[use]);R=R@dR;t=t@dR+dt
            rms=float(np.sqrt(np.mean(err[use]**2)))
            if prev is not None and abs(rms-prev)<1e-7:break
            prev=rms
        moved=sp@R+t;fd=cKDTree(tp).query(moved)[0];rd=cKDTree(moved).query(tp)[0];both=np.r_[fd,rd]
        score=float(np.sqrt(np.mean(both**2)))
        fits.append({'mode':mode,'initial_axial_rotation_deg':angle,'iterations':iteration+1,'rotation_row_vectors':R.tolist(),'translation_mm':t.tolist(),'determinant':float(np.linalg.det(R)),'scale':1,'symmetrical_sample_point_rms_mm':score,'median_mm':float(np.median(both)),'p95_mm':float(np.quantile(both,.95)),'long_axis_alignment_cosine':float(np.dot(sb[:,0]@R,tb[:,0])),'seed':'PCA with long axis directed away from labelled source carpals; minor-axis quarter turns'})
        print(owner,mode,angle,round(score,5),flush=True)

best=min((r for r in fits if r['mode']=='whole'),key=lambda r:r['symmetrical_sample_point_rms_mm'])
R=np.array(best['rotation_row_vectors']);t=np.array(best['translation_mm'])
alltrans=[sp@np.array(x['rotation_row_vectors'])+np.array(x['translation_mm']) for x in fits]
base=sp@R+t
for row,positions in zip(fits,alltrans):
    row['rms_displacement_from_best_mm']=float(np.sqrt(np.mean(np.sum((positions-base)**2,axis=1))))
    RR=np.array(row['rotation_row_vectors']);row['rotation_from_best_deg']=float(np.degrees(np.arccos(np.clip((np.trace(RR@R.T)-1)/2,-1,1))))
geometry=source.copy();geometry.vertices=(geometry.vertices@R+t)/1000
geometry.visual=trimesh.visual.ColorVisuals(geometry,vertex_colors=[175,150,80,255])
scene=trimesh.Scene();scene.add_geometry(geometry,node_name='b|'+owner,geom_name='trial_bonehub_'+owner)
glb=scene.export(file_type='glb');(ROOT/(owner+'-rigid-trial.glb')).open('xb').write(glb)
out={'owner':owner,'source':str(sourcefile),'sourceSha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'target':'native__'+owner,'targetSource':str(OLD/'comparison-arrays.json'),'sourceCoordinateHeader':sourcefile.read_bytes()[:80].decode('ascii').strip('\x00'),'identity':'source-labelled left; no mirroring','method':'One rigid mapping to existing native BP3D whole bone using PCA ends + symmetric sampled point-cloud ICP. Working neighbours excluded from optimisation. Shaft-only sensitivity fit is diagnostic, not admitted. Neither registration nor error thresholds establish articular anatomy.','source_long_axis_extent_mm':float(np.ptp(np.asarray(source.vertices)@sb[:,0])),'target_long_axis_extent_mm':float(np.ptp(np.asarray(target.vertices)@tb[:,0])),'fits':fits,'chosen':best,'status':'test_only_anatomically_unverified','GLB':owner+'-rigid-trial.glb','GLBsha256':hashlib.sha256(glb).hexdigest(),'elapsed_seconds':time.monotonic()-(deadline-50)}
with (ROOT/(owner+'-registration.json')).open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
with (ROOT/(owner+'-registered-arrays.json')).open('x',encoding='utf8') as f:json.dump({'vertices':geometry.vertices.ravel().tolist(),'faces':geometry.faces.ravel().tolist()},f)

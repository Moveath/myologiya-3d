"""Bone-only symmetry fit, independent of muscle collision outcomes.

This estimates a geometric reflection plane, not an anatomically labelled
midsagittal plane. All operations are bounded to 60 seconds per invocation.
"""
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

START = time.monotonic()
RUN = pathlib.Path(sys.argv[1])
PREVIOUS = pathlib.Path('research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT')
raw = json.loads((PREVIOUS/'context-arrays.json').read_text())
NAMES = ['b|axis'] + [f'b|cervical_{i}' for i in range(3,8)]
ORIGIN = np.array([0,1420,45.0])

def clock():
    if time.monotonic()-START > 59:
        raise TimeoutError('Bone-only plane fit stopped at 59 second bound')

def sample(v,f,n,seed):
    rng=np.random.default_rng(seed)
    tri=v[f]
    area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    choice=rng.choice(len(f),size=n,p=area/area.sum())
    uv=rng.random((n,2))
    uv[uv.sum(1)>1]=1-uv[uv.sum(1)>1]
    t=tri[choice]
    return t[:,0]+uv[:,0,None]*(t[:,1]-t[:,0])+uv[:,1,None]*(t[:,2]-t[:,0])

bones=[]
for i,name in enumerate(NAMES):
    row=next(r for r in raw if r['file']=='neck' and r['name']==name)
    v=np.array(row['positions']).reshape(-1,3)*1000-ORIGIN
    f=np.array(row['indices']).reshape(-1,3)
    target=np.vstack([sample(v,f,20000,130+i),v])
    bones.append(dict(name=name,v=v,f=f,target=target,tree=cKDTree(target)))

def unpack(params):
    n=np.array([1,params[0],params[1]])
    return n/np.linalg.norm(n),params[2]

def reflect(p,params):
    n,d=unpack(params)
    return p-2*((p@n)-d)[:,None]*n

def fit(indices,seed,start):
    clock()
    samples={i:sample(bones[i]['v'],bones[i]['f'],768,seed+10*i) for i in indices}
    calls=0
    def objective(params):
        nonlocal calls
        clock();calls+=1
        errors=[]
        for i in indices:
            d=bones[i]['tree'].query(reflect(samples[i],params),workers=1)[0]
            # Fixed robust truncation avoids one gross individual outlier
            # dominating the plane. Full residuals are reported separately.
            errors.append(np.mean(np.minimum(d*d,4)))
        return np.mean(errors)
    result=minimize(objective,np.array(start),method='Powell',bounds=[(-.18,.18),(-.18,.18),(-6,6)],options=dict(maxiter=45,xtol=1e-5,ftol=1e-6))
    n,d=unpack(result.x)
    return dict(parameters=result.x.tolist(),normal=n.tolist(),offsetFromLocalOriginMM=float(d),worldPlaneConstantMM=float(d+ORIGIN@n),lossMM2=float(result.fun),success=bool(result.success),functionCalls=calls,seed=seed,bones=[NAMES[i] for i in indices])

fits=[]
for seed,start in [(1000,[0,0,0]),(2000,[.03,-.03,-2]),(3000,[-.03,.03,2])]:
    fits.append(fit(list(range(6)),seed,start))
    with (RUN/f'fit-common-{seed}.json').open('x',encoding='utf8') as h:json.dump(fits[-1],h,indent=2)
best=fits[0]['parameters']
leave=[]
for i in range(6):
    leave.append(fit([j for j in range(6) if j!=i],1000,best))
    with (RUN/f'fit-without-{i}.json').open('x',encoding='utf8') as h:json.dump(leave[-1],h,indent=2)
validation=[]
for i,bone in enumerate(bones):
    points=sample(bone['v'],bone['f'],2048,8000+i)
    for label,params in [('X=0',[0,0,0]),('common-bone-fit',best)]:
        d=bone['tree'].query(reflect(points,params),workers=1)[0]
        validation.append(dict(bone=bone['name'],plane=label,meanMM=float(d.mean()),rmsMM=float(np.sqrt(np.mean(d*d))),medianMM=float(np.median(d)),p95MM=float(np.quantile(d,.95)),maxSampleMM=float(d.max())))
landmarks=np.array([[0,y,z] for y in [1390,1420,1452] for z in [30,45,53]])-ORIGIN
allfit=fits+leave
normals=np.array([r['normal'] for r in allfit])
angles=np.degrees(np.arccos(np.clip(normals@normals[0],-1,1)))
signed=np.array([landmarks@np.array(r['normal'])-r['offsetFromLocalOriginMM'] for r in allfit])
result=dict(method='Bone-only area-uniform deterministic surface samples; reflection about one rigid plane; nearest dense surface cloud (20000 samples + original vertices per bone); equal weight C2-C7; loss capped at 2mm. Three independent training samples/initializations and six leave-one-bone-out fits. No muscle points, collisions, endpoint distances or desired admission enter the objective.',
            approximation='Cloud distances approximate surface distances. Geometric reflection symmetry is not independently labelled anatomical midsagittal anatomy. Fit does not license deforming a muscle or shifting each bundle.',
            originMM=ORIGIN.tolist(),commonFits=fits,leaveOneOut=leave,validation=validation,
            uncertainty=dict(maxNormalDifferenceDegrees=float(angles.max()),sampledSignedPlaneVariationMM=float(np.ptp(signed,axis=0).max())),
            elapsedSeconds=time.monotonic()-START,selectedParameters=best,sourceContext=str(PREVIOUS/'context-arrays.json'))
with (RUN/'bone-plane-fit.json').open('x',encoding='utf8') as h:json.dump(result,h,indent=2)
print(json.dumps({k:result[k] for k in ['selectedParameters','uncertainty','elapsedSeconds']}))

"""Common rigid frame diagnostic from five controls, never per-bone joint fitting."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import numpy as np
import trimesh

run=Path(sys.argv[1]).resolve()
spec=importlib.util.spec_from_file_location('ranges',Path(__file__).with_name('inspect-stage6-sources.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
url=json.loads((run/'bp4-extraction.json').read_text(encoding='utf8'))['url']
rows=(run/'bp4-elements.txt').read_text(encoding='utf8').splitlines()
controls=dict(trapezium_left='FMA24444',trapezoid_left='FMA24445',capitate_left='FMA24447',metacarpal_2_left='FMA24467',metacarpal_4_left='FMA24471')
fma_to_file={f:next(r.split('\t')[2] for r in rows if r.startswith(f+'\t')) for f in controls.values()}
source=mod.RemoteZip(url,budget=3_000_000);downloads=[]
with zipfile.ZipFile(source) as z:
    for owner,fma in controls.items():
        element=fma_to_file[fma];entry=next(n for n in z.namelist() if Path(n).name==element+'.obj')
        data=z.read(entry);file=run/('bp4-'+element+'.obj')
        with file.open('xb') as f:f.write(data)
        downloads.append(dict(id=owner,fma=fma,entry=entry,file=file.name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
with (run/'bp4-control-sources.json').open('x',encoding='utf8') as f:json.dump(dict(url=url,rangeBytesRead=source.used,downloads=downloads),f,indent=2)
arrays=json.loads((run/'comparison-arrays.json').read_text(encoding='utf8'))
def oldmesh(key):
    a=arrays[key];return trimesh.Trimesh(np.asarray(a['vertices']).reshape(-1,3),np.asarray(a['faces']).reshape(-1,3),process=False)
def newmesh(file):
    m=trimesh.load_mesh(run/file,process=False);m.vertices=m.vertices[:,[0,2,1]]*[1,1,-1]/1000;return m
new={r['id']:newmesh(r['file']) for r in downloads}
old={k:oldmesh('live__'+k) for k in controls}
# Bounding centres are reproducible controls, not landmarks or a medical registration.
x=np.asarray([new[k].bounds.mean(0) for k in controls]);y=np.asarray([old[k].bounds.mean(0) for k in controls])
xc,yc=x.mean(0),y.mean(0);u,s,vt=np.linalg.svd((x-xc).T@(y-yc));r=vt.T@u.T
if np.linalg.det(r)<0:vt[-1]*=-1;r=vt.T@u.T
t=yc-r@xc;matrix=np.eye(4);matrix[:3,:3]=r;matrix[:3,3]=t
result=dict(matrix=matrix.tolist(),controls=list(controls),scale=1,reflection=False,
            residualCentreMM=(np.linalg.norm((x@r.T+t)-y,axis=1)*1000).tolist(),
            limitation='Approximate common rigid registration from control bounding centres; not anatomical landmarks or acceptance. No published geometry is changed.',candidates=[])
for id,file,neighbors in [
 ('metacarpal_1_left','bp4-FJ3240.obj',['trapezium_left','phalanx_prox_1_left']),
 ('metacarpal_3_left','bp4-FJ3246.obj',['trapezoid_left','capitate_left','phalanx_prox_3_left'])]:
    m=newmesh(file);m.apply_transform(matrix)
    candidate=dict(id=id,joints=[])
    for neighbor in neighbors:
        n=oldmesh('live__'+neighbor);points=np.concatenate([m.vertices,m.triangles_center]);tri=n.triangles;inside=[]
        for i in range(0,len(points),16):
            v=tri[None]-points[i:i+16,None,None,:];a,b,c=v[:,:,0],v[:,:,1],v[:,:,2]
            la,lb,lc=[np.linalg.norm(q,axis=2) for q in (a,b,c)];dot=lambda x,y:np.einsum('ijk,ijk->ij',x,y)
            w=np.sum(2*np.arctan2(dot(a,np.cross(b,c)),la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb),axis=1)/(4*np.pi)
            inside.extend((i+np.where(np.abs(w)>.5)[0]).tolist())
        depth=[]
        for i in range(0,len(inside),16):depth.extend(trimesh.proximity.closest_point_naive(n,points[inside[i:i+16]])[1]*1000)
        candidate['joints'].append(dict(neighbor=neighbor,insideSamples=len(inside),maxSampleDepthMM=float(max(depth,default=0)),direction='candidate into working neighbor only'))
    result['candidates'].append(candidate)
with (run/'bp4-frame-diagnostic.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result),flush=True)

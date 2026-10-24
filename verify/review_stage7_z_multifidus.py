"""Bounded labelled-bone registration of authored Z-Anatomy thoracic parts.

Diagnostic only: no model displacement, no source writes, no anatomical admission.
Nearest vertices are a registration proxy, not proof of muscle attachments.
"""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import trimesh

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
z={r['name']:r for r in json.loads((RUN/'z-target-arrays-v2.json').read_text(encoding='utf8'))}
a={r['name']:r for r in json.loads((RUN/'atlas-multifidus-context.json').read_text(encoding='utf8'))}
axis=np.array([[1,0,0],[0,0,1],[0,-1,0.]])
source=[np.array(z[f'Vertebra T{n}']['vertices'])@axis.T for n in range(1,13)]
target=[np.array(a[f'b|thoracic_{n}']['vertices'])for n in range(1,13)]
trees=[cKDTree(v)for v in target]

def fit(x,y,scaling=False):
    xc=x-x.mean(0);yc=y-y.mean(0)
    u,s,vt=np.linalg.svd(xc.T@yc)
    d=np.eye(3);d[-1,-1]=np.linalg.det(u@vt)
    rot=u@d@vt
    scale=float(np.sum(s*np.diag(d))/np.sum(xc*xc)) if scaling else 1.
    offset=y.mean(0)-scale*x.mean(0)@rot
    return rot,scale,offset

def stats(d):return {k:float(v)for k,v in zip(['min','median','p95','max'],np.quantile(d,[0,.5,.95,1])*1000)}
allx=np.vstack(source)
results=[]
for scaling in [False,True]:
    rot,scale,offset=fit(np.array([x.mean(0)for x in source]),np.array([y.mean(0)for y in target]),scaling)
    history=[]
    for iteration in range(25):
        destinations=[]
        for xs,yt,tree in zip(source,target,trees):
            distances,ix=tree.query(scale*xs@rot+offset)
            destinations.append(yt[ix])
        yr=np.vstack(destinations)
        rot,scale,offset=fit(allx,yr,scaling)
        history.append(float(np.sqrt(np.mean(np.sum((scale*allx@rot+offset-yr)**2,axis=1)))*1000))
    matrix=np.eye(4);matrix[:3,:3]=scale*rot.T@axis;matrix[:3,3]=offset
    perbone=[]
    for n,(xs,yt,tree)in enumerate(zip(source,target,trees),1):
        d,ix=tree.query(scale*xs@rot+offset)
        perbone.append({'bone':f'T{n}','nearest_vertex_mm':stats(d)})
    muscles=[]
    for side,ending in [('right','r'),('left','l')]:
        row=z[f'Multifidus thoracis muscle.{ending}']
        vertices=np.array(row['vertices'])@matrix[:3,:3].T+matrix[:3,3]
        faces=np.array(row['faces'])
        if row['determinant']<0:faces=faces[:,[0,2,1]]
        mesh=trimesh.Trimesh(vertices,faces,process=False)
        whole=np.array(a[f'm|thorax_multifidus_{side}|']['vertices'])
        distance,ix=cKDTree(whole).query(vertices)
        muscles.append({'side':side,'vertices':len(vertices),'triangles':len(faces),
            'bounds':mesh.bounds.tolist(),'watertight':bool(mesh.is_watertight),
            'winding_consistent':bool(mesh.is_winding_consistent),'volume_mm3':float(mesh.volume*1e9),
            'parent_nearest_vertex_mm':stats(distance),
            'negative_source_determinant_winding_reversed':row['determinant']<0})
    results.append({'kind':'similarity'if scaling else'rigid','scale':scale,
        'matrix_source_blender_to_atlas_three':matrix.tolist(),
        'rotation_determinant':float(np.linalg.det(rot)),
        'iterations':len(history),'nearest_vertex_rms_history_mm':history,
        'bones':perbone,'muscles':muscles,
        'admitted':False,'reason':'Bone registration only; muscle topology and attachment relations require individual review.'})
with(RUN/'z-multifidus-registration.json').open('x',encoding='utf8')as f:json.dump(results,f,indent=2)
print(json.dumps([{k:r[k]for k in ['kind','scale','muscles']}|{'final_rms_mm':r['nearest_vertex_rms_history_mm'][-1]}for r in results],indent=2))

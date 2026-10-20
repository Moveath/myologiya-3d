"""Read-only topology audit of exact r170-decoded assets; no mesh repair."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage4-2026-10-16'
CACHE=ROOT/'.venv/geometry-audit-cache'

def topology(v,f,n,matrix):
    triangles=v[f]
    cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
    zero=np.all(cross==0,axis=1)
    # Exact position welding is diagnostic only; source arrays remain unchanged.
    unique,inv=np.unique(v,axis=0,return_inverse=True)
    welded=inv[f]
    keys=np.sort(welded,axis=1)
    _,first,labels,counts=np.unique(keys,axis=0,return_index=True,return_inverse=True,return_counts=True)
    duplicate=np.flatnonzero(np.arange(len(f))!=first[labels])
    clean=welded[~zero]
    e=trimesh.geometry.faces_to_edges(clean)
    ek=np.sort(e,axis=1)
    ue,ei,ec=np.unique(ek,axis=0,return_inverse=True,return_counts=True)
    directions=np.where(e[:,0]<e[:,1],1,-1)
    sums=np.bincount(ei,weights=directions)
    winding=np.flatnonzero((ec==2)&(sums!=0))
    graph=coo_matrix((np.ones(len(ue),dtype=np.int8),(ue[:,0],ue[:,1])),shape=(len(unique),len(unique))).tocsr()
    component_count,component=connected_components(graph,directed=False)
    normal_bad=np.array([],dtype=int);normal_lengths_bad=np.array([],dtype=int)
    if len(n):
        lens=np.linalg.norm(n,axis=1)
        normal_lengths_bad=np.flatnonzero(~np.isfinite(lens)|(lens<.95)|(lens>1.05))
        avg=n[f].mean(axis=1)
        denominator=np.linalg.norm(avg,axis=1)*np.linalg.norm(cross,axis=1)
        dot=np.einsum('ij,ij->i',avg,cross)
        normal_bad=np.flatnonzero((~zero)&(denominator>0)&(dot < -.01*denominator))
    world=v@matrix[:3,:3].T+matrix[:3,3]
    wt=world[f];wc=np.cross(wt[:,1]-wt[:,0],wt[:,2]-wt[:,0])
    degenerate_world=np.all(wc==0,axis=1)
    scale=np.linalg.svd(matrix[:3,:3],compute_uv=False)
    summary=dict(vertices=len(v),triangles=len(f),finite=bool(np.isfinite(v).all()),local_zero=int(zero.sum()),world_zero=int(degenerate_world.sum()),
        duplicate_faces=len(duplicate),boundary_edges=int((ec==1).sum()),nonmanifold_edges=int((ec>2).sum()),
        inconsistent_two_face_edges=len(winding),components=int(component_count),component_vertex_counts=np.bincount(component).tolist(),
        bad_normal_lengths=len(normal_lengths_bad),opposed_average_normals=len(normal_bad),normals_present=bool(len(n)),
        determinant=float(np.linalg.det(matrix[:3,:3])),singular_values=scale.tolist(),bounds_m=[world.min(axis=0).tolist(),world.max(axis=0).tolist()])
    flags=dict(degenerate_faces=np.flatnonzero(zero),duplicate_faces=duplicate,opposed_average_normal_faces=normal_bad,
               bad_normal_vertices=normal_lengths_bad,boundary_edges=ue[ec==1],nonmanifold_edges=ue[ec>2],winding_edges=ue[winding])
    return summary,flags

def main():
    result=[]
    for row in json.loads((CACHE/'index.json').read_text()):
        meta=json.loads((CACHE/(row['file']+'.json')).read_text())
        source=ROOT/'site'/row['file']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['sha256']
        details=[]
        for mesh in meta['meshes']:
            prefix=mesh['prefix']
            v=np.fromfile(CACHE/(prefix+'.v'),dtype='<f8').reshape(-1,3)
            f=np.fromfile(CACHE/(prefix+'.f'),dtype='<u4').reshape(-1,3)
            n=np.fromfile(CACHE/(prefix+'.n'),dtype='<f8').reshape(-1,3)
            matrix=np.array(mesh['matrix']).reshape(4,4).T
            summary,flags=topology(v,f,n,matrix)
            summary.update(id=mesh['id'],name=mesh['name'],owner=mesh['owner'],positionType=mesh['positionType'],normalized=mesh['normalized'])
            flagfile=OUT/'face-flags'/(prefix+'.npz')
            flagfile.parent.mkdir(exist_ok=True)
            np.savez_compressed(flagfile,**flags)
            summary['face_flags']=str(flagfile.relative_to(ROOT)).replace('\\','/')
            details.append(summary)
        totals={k:sum(m[k] for m in details) for k in ['vertices','triangles','local_zero','world_zero','duplicate_faces','boundary_edges','nonmanifold_edges','inconsistent_two_face_edges','bad_normal_lengths','opposed_average_normals']}
        result.append(dict(file=row['file'],sha256=meta['sha256'],meshes=details,totals=totals))
        print(row['file'],json.dumps(totals),flush=True)
        (OUT/'topology.json').write_text(json.dumps(dict(method='Exact decoded local positions; exact coordinate welding for diagnostic topology; zero-area faces excluded from edge incidence. Negative normal dot is a review flag, not an automatic anatomical defect. No self-intersection test.',packages=result),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Completed',len(result),'packages')
if __name__=='__main__':main()


"""Summarize provenance, encoding differences and source/packed degeneracy."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage4-2026-10-16';CACHE=ROOT/'.venv/geometry-audit-cache'
source=[]
for region in ('head','neck','thorax'):
    path=ROOT/f'build_{region}/{region}_hi.glb'
    scene=trimesh.load(path,force='scene',process=False)
    rows=[]
    for name,mesh in scene.geometry.items():
        t=mesh.triangles;c=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        rows.append(dict(name=name,triangles=len(t),zero=int(np.all(c==0,axis=1).sum())))
    source.append(dict(file=str(path.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),meshes=rows))
pairs=[];normals=[]
for region in ('arm','leg','head','neck','thorax'):
    a=json.loads((CACHE/f'{region}-glb.txt.json').read_text());b=json.loads((CACHE/f'{region}-q-glb.txt.json').read_text())
    same=True;different=[];index_equal=True;world_delta=0.
    for x,y in zip(a['meshes'],b['meshes'],strict=True):
        for suffix in ('.v','.f'):
            same &= (CACHE/(x['prefix']+suffix)).read_bytes()==(CACHE/(y['prefix']+suffix)).read_bytes()
        same &= x['matrix']==y['matrix']
        index_equal &= (CACHE/(x['prefix']+'.f')).read_bytes()==(CACHE/(y['prefix']+'.f')).read_bytes()
        vx=np.fromfile(CACHE/(x['prefix']+'.v'),dtype='<f8').reshape(-1,3)
        vy=np.fromfile(CACHE/(y['prefix']+'.v'),dtype='<f8').reshape(-1,3)
        mx=np.array(x['matrix']).reshape(4,4).T;my=np.array(y['matrix']).reshape(4,4).T
        wx=vx@mx[:3,:3].T+mx[:3,3];wy=vy@my[:3,:3].T+my[:3,3]
        # gltfpack reorders vertices/indices between encodings. Pair by location,
        # never compare the same array offset as if it were the same vertex.
        world_delta=max(world_delta,float(max(cKDTree(wx).query(wy)[0].max(),cKDTree(wy).query(wx)[0].max()))*1000)
        normal_a=(CACHE/(x['prefix']+'.n')).read_bytes()
        normal_b=(CACHE/(y['prefix']+'.n')).read_bytes()
        if normal_a!=normal_b:different.append(x['owner'])
        n=np.frombuffer(normal_b,dtype='<f8').reshape(-1,3);zero=np.all(n==0,axis=1)
        if zero.any():
            v=np.fromfile(CACHE/(y['prefix']+'.v'),dtype='<f8').reshape(-1,3)
            f=np.fromfile(CACHE/(y['prefix']+'.f'),dtype='<u4').reshape(-1,3);t=v[f]
            good=np.any(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])!=0,axis=1)
            used=np.unique(f[good])
            normals.append(dict(region=region,mesh=y['id'],owner=y['owner'],zero=int(zero.sum()),zero_with_nondegenerate_faces=int(zero[used].sum())))
    pairs.append(dict(region=region,local_buffers_and_transforms_identical=bool(same),indices_identical=bool(index_equal),maximum_bidirectional_vertex_set_distance_mm=world_delta,normal_buffers_different_meshes=len(different),note='Buffer/normal differences include reordering; vertex-set distance is not a face-index correspondence.'))
head=json.loads((CACHE/'head-q-glb.txt.json').read_text());jugular=[]
for m in head['meshes']:
    if m['owner'] not in ('b|occipital','b|temporal_right','b|temporal_left'):continue
    v=np.fromfile(CACHE/(m['prefix']+'.v'),dtype='<f8').reshape(-1,3)
    f=np.fromfile(CACHE/(m['prefix']+'.f'),dtype='<u4').reshape(-1,3)
    mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
    edges=np.sort(mesh.edges,axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
    jugular.append(dict(owner=m['owner'],indexed_boundary_edges=int((counts==1).sum()),indexed_nonmanifold=int((counts>2).sum()),winding_consistent=bool(mesh.is_winding_consistent),watertight=bool(mesh.is_watertight)))
report=dict(source=source,pairs=pairs,zero_normals=normals,jugular_indexed=jugular)
(OUT/'encoding-source-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(source=[(s['file'],sum(r['zero'] for r in s['meshes'])) for s in source],pairs=pairs,zero_normals=sum(n['zero'] for n in normals),jugular=jugular)))


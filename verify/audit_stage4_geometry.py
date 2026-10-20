"""Read-only stage 4 diagnostics; distances are flags, not anatomical verdicts."""
from pathlib import Path
import base64, hashlib, io, json
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from geometry_distance import SurfaceQuery

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage4-2026-10-15'
pins=json.loads((OUT/'diagnostic-pins.json').read_text(encoding='utf8'))
models=[]; measurements=[]
for region in ('arm','leg','head','neck','thorax'):
    path=ROOT/'site'/f'{region}-q-glb.txt'
    scene=trimesh.load(io.BytesIO(base64.b64decode(path.read_bytes())),file_type='glb',force='scene',process=False)
    parents=scene.graph.transforms.parents; groups={}; parts=[]
    for node in scene.graph.nodes_geometry:
        owner=node
        while owner and not owner.startswith('b|'): owner=parents.get(owner)
        transform,key=scene.graph[node]
        mesh=scene.geometry[key].copy()
        mesh.apply_transform(transform)
        if owner: groups.setdefault(owner.split('|')[1],[]).append(mesh)
        area=np.linalg.norm(np.cross(mesh.triangles[:,1]-mesh.triangles[:,0],mesh.triangles[:,2]-mesh.triangles[:,0]),axis=1)/2
        record=dict(node=node,owner=owner,vertices=len(mesh.vertices),triangles=len(mesh.faces),
                    finite=bool(np.isfinite(mesh.vertices).all()),zero_area_triangles=int(np.count_nonzero(area==0)),
                    transform_determinant=float(np.linalg.det(transform[:3,:3])),bounds_m=mesh.bounds.tolist())
        if owner and owner.split('|')[1] in ('metacarpal_1','phalanx_prox_1','pisiform','sacrum'):
            _, inverse=np.unique(mesh.vertices,axis=0,return_inverse=True)
            edges=inverse[mesh.edges]
            n=int(inverse.max())+1
            graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(n,n)).tocsr()
            count,labels=connected_components(graph,directed=False)
            record['components_after_exact_coordinate_welding']=int(count)
            record['component_vertex_counts']=np.bincount(labels).tolist()
            record['component_bounds_m']=[mesh.vertices[labels[inverse]==i].min(axis=0).tolist()+mesh.vertices[labels[inverse]==i].max(axis=0).tolist() for i in range(count)]
        parts.append(record)
    merged={b:trimesh.util.concatenate(ms) for b,ms in groups.items()}
    queries={b:SurfaceQuery(mesh) for b,mesh in merged.items()}
    for p in pins:
        if p['b'] not in merged or not p.get('p'):continue
        _,distance,_=queries[p['b']].closest([p['p']])
        related=p.get('related',[])
        distances={p['b']:float(distance[0])}
        for b in related:
            if b in merged and b not in distances:
                _,d,_=queries[b].closest([p['p']])
                distances[b]=float(d[0])
        measurements.append(dict(id=p['id'],model=str(path.relative_to(ROOT)),localization=p.get('loc'),
                                 anchorStatus=p.get('anchorStatus'),side=p.get('side'),p=p['p'],
                                 distances_mm=distances,normal_length=float(np.linalg.norm(p['n'])) if p.get('n') else None,
                                 verdict='measurement_only_no_coordinate_change'))
    models.append(dict(region=region,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       bones=sorted(groups),meshes=len(parts),total_triangles=sum(p['triangles'] for p in parts),
                       zero_area_triangles=sum(p['zero_area_triangles'] for p in parts),parts=parts))
    print(region,'meshes',len(parts),'zero-area',models[-1]['zero_area_triangles'],flush=True)
report=dict(tool='trimesh',version=trimesh.__version__,numpy=np.__version__,process=False,query_units='rebased millimetres',
            note='World-space glTF meters. Exact zero area; no repair/export. Connected components use exact coordinate equality only, not anatomical segmentation. Not a self-intersection test.',
            models=models,points=measurements)
(OUT/'mesh-diagnostics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Measured points',len(measurements))


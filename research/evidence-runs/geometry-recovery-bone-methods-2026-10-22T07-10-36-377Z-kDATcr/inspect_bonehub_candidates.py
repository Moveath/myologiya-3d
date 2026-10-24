"""Bounded topology inventory, not anatomical admission or repair."""
import json, hashlib, pathlib
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT=pathlib.Path(__file__).resolve().parent
rows=[]
for p in sorted((ROOT/'bonehub-candidates').glob('*.stl')):
    m=trimesh.load(p,force='mesh',process=True)
    adjacency=m.face_adjacency
    graph=coo_matrix((np.ones(len(adjacency)),(adjacency[:,0],adjacency[:,1])),shape=(len(m.faces),len(m.faces)))
    count,labels=connected_components(graph,directed=False)
    sizes=np.bincount(labels)
    comp=[]
    for k in np.argsort(sizes)[::-1][:8]:
        mask=np.where(labels==k)[0]
        vertices=m.vertices[m.faces[mask]].reshape(-1,3)
        comp.append({'faces':len(mask),'bounds_source_units':np.stack([vertices.min(axis=0),vertices.max(axis=0)]).tolist(),'centroid_surface_vertices':vertices.mean(axis=0).tolist()})
    row={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'vertices_after_read_merge':len(m.vertices),'triangles':len(m.faces),'components':int(count),'largest_components':comp,'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'volume_source_units_cubed':float(m.volume),'bounds_source_units':m.bounds.tolist(),'extent_source_units':m.extents.tolist(),'degenerate_faces':int((m.area_faces<1e-10).sum()),'duplicate_faces':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'status':'candidate_not_registered_or_admitted','mesh_notes':'STL imported in analysis memory with identical triangle positions and merged coincident vertices; source unchanged. No selfintersection or joint conformity claim.'}
    rows.append(row)
    print(p.name, 'faces',len(m.faces),'components',count,'major',[int(x) for x in sorted(sizes,reverse=True)[:5]],'closed',m.is_watertight,flush=True)
with (ROOT/'bonehub-quality.json').open('x',encoding='utf8') as f:json.dump(rows,f,ensure_ascii=False,indent=2)

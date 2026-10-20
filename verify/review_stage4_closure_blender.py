"""Execute with Blender MCP; measurements only, no saved .blend or source writes."""
from pathlib import Path
import json, re
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

ROOT=Path(r'C:/Users/Пользователь/Desktop/учеба/Миология 3D')
OUT=ROOT/'research/stage4-closure-2026-10-16'
CACHE=ROOT/'.venv/geometry-audit-cache'
rows=json.loads((OUT/'self-intersections.json').read_text())['results']
selected=[r for r in rows if r['file']=='head-glb.txt' and r['owner'] in ('b|occipital','b|temporal_right','b|parietal_right')]
checks=[]
for r in selected:
    meta=json.loads((CACHE/(r['file']+'.json')).read_text())['meshes'][r['mesh']]
    v=np.fromfile(CACHE/(meta['prefix']+'.v'),dtype='<f8').reshape(-1,3)
    f=np.fromfile(CACHE/(meta['prefix']+'.f'),dtype='<u4').reshape(-1,3)
    v=(v-v.mean(0))/np.ptp(v,axis=0).max()
    tree=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True,epsilon=0)
    overlap={tuple(sorted(pair)) for pair in tree.overlap(tree) if pair[0]!=pair[1]}
    candidates=[{**e,'blenderOverlap':(e['i'],e['j']) in overlap} for e in r['examples']]
    checks.append({'owner':r['owner'],'file':r['file'],'sha256':r['sha256'],'examples':candidates})

def vtk_points(path):
    data=path.read_bytes();match=re.search(rb'POINTS (\d+) float\n',data)
    return np.frombuffer(data,dtype='>f4',count=int(match[1])*3,offset=match.end()).reshape(-1,3).astype(float)

spl=[]
# No objects or transforms are added to the user's scene.
for name in ('Model_140_Malleus_Bone.vtk','Model_17_Stapes_Bone.vtk'):
    v=vtk_points(OUT/name)
    mesh=bpy.data.meshes.new('Stage4 temporary SPL bounds')
    mesh.from_pydata(v.tolist(),[],[])
    observed=np.array([tuple(p.co) for p in mesh.vertices])
    spl.append({'file':name,'vertices':len(observed),'bounds_source_units':[observed.min(0).tolist(),observed.max(0).tolist()],
                'extent_source_units':np.ptp(observed,axis=0).tolist(),'physical_mm_confirmed':False})
    bpy.data.meshes.remove(mesh)
result={'blender':bpy.app.version_string,'active_scene_unchanged':bpy.context.scene.name,
        'intersection_spotchecks':checks,'spl':spl,
        'limits':'BVHTree overlap is an independent numeric candidate check, not anatomical acceptance or exact-arithmetic proof; SPL source coordinate units are not independently calibrated millimetres.'}
(OUT/'blender-crosscheck.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'checked_bones':len(checks),'candidates':sum(len(x['examples']) for x in checks),'spl':spl}))

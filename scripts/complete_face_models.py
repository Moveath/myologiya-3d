"""Build independent comparison meshes; never register or transfer labels."""
from pathlib import Path
import json,sys
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from manifest_head import BONES
OUT=ROOT/'research/cache/face-completion'
OUT.mkdir(parents=True,exist_ok=True)
scene=trimesh.Scene()
rows=[]
for bone,ids in BONES.items():
 if not bone.startswith(('maxilla','zygomatic','palatine','lacrimal','nasal','inferior_concha','mandible','vomer')):continue
 bp=trimesh.load(ROOT/'stl_head'/f'{ids[0]}.stl',force='mesh')
 bp.vertices=bp.vertices[:,[0,2,1]]*np.array([.001,.001,-.001])
 zdata=json.loads((ROOT/'research/cache/z-detail'/f'{bone}.json').read_text())
 z=trimesh.Trimesh(zdata['vertices'],zdata['faces'],process=False)
 for name,mesh in [('bp',bp),('z',z)]:
  scene.add_geometry(mesh,node_name='b|'+name+'_'+bone,geom_name=name+'_'+bone)
  rows.append({'bone':bone,'source':name,'vertices':len(mesh.vertices),'faces':len(mesh.faces),'watertight':mesh.is_watertight,'bounds':mesh.bounds.tolist()})
scene.export(OUT/'comparison.glb')
(OUT/'geometry.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('Saved',len(rows),'comparison meshes')

"""Blender MCP: exact decoded source triangles; temporary scene only."""
import json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
run=Path(RUN)
data=json.loads((run/'head-glb-source.json').read_text(encoding='utf8'))
prior=bpy.context.window.scene
before={k:set(getattr(bpy.data,k)) for k in ['objects','meshes','curves','cameras','materials','images']}
scene=bpy.data.scenes.new('skull_region_review')
def bv(v):return Vector((v[0],-v[2],v[1]))
results=[]
try:
 bpy.context.window.scene=scene
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
 scene.render.image_settings.file_format='PNG'
 base=bpy.data.materials.new('source');base.diffuse_color=(.66,.72,.76,1)
 marked=bpy.data.materials.new('reviewed_region');marked.diffuse_color=(.95,.24,.08,1)
 cd=bpy.data.cameras.new('review_camera');cam=bpy.data.objects.new('review_camera',cd);scene.collection.objects.link(cam);scene.camera=cam
 cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=10
 maskfile=run/globals().get('MASKFILE','candidate-masks.json')
 masks=json.loads(maskfile.read_text(encoding='utf8')) if maskfile.exists() else {}
 for r in data['rows']:
  if 'BONES' in globals() and r['bone'] not in BONES:continue
  v=np.array(r['positions']).reshape(-1,3);f=np.array(r['indices']).reshape(-1,3)
  me=bpy.data.meshes.new(r['bone']);me.from_pydata([bv(q) for q in v],[],f.tolist());o=bpy.data.objects.new(r['bone'],me);scene.collection.objects.link(o)
  me.materials.append(base);me.materials.append(marked)
  for i in masks.get(r['bone'],{}).get('faces',[]):me.polygons[i].material_index=1
  line=None
  if masks.get(r['bone'],{}).get('edges'):
   curve=bpy.data.curves.new('review_contour','CURVE');curve.dimensions='3D';curve.bevel_depth=.00024;curve.bevel_resolution=0
   for a,b in masks[r['bone']]['edges']:
    s=curve.splines.new('POLY');s.points.add(1)
    for point,coord in zip(s.points,[v[a],v[b]]):point.co=(*bv(coord),1)
   curve.materials.append(marked);line=bpy.data.objects.new('review_contour',curve);scene.collection.objects.link(line)
  views=globals().get('VIEWS',[('inferior',(0,-1,0)),('lateral',(-1 if r['bone']!='temporal_left' else 1,-.4,.1)),('medial',(1 if r['bone']!='temporal_left' else -1,.35,0))])
  for label,direction in views:
   center=np.array(globals().get('CENTER',(v.min(0)+v.max(0))/2))
   cam.location=bv(center)+bv(direction);cam.rotation_euler=(bv(center)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=globals().get('SCALE',.14)
   file=run/(PREFIX+r['bone']+'-'+label+'.png')
   if file.exists():raise FileExistsError(file)
   scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
   results.append(dict(file=file.name,bone=r['bone'],direction=direction,triangles=len(f)))
  bpy.data.objects.remove(o,do_unlink=True)
  if line:
   curve=line.data;bpy.data.objects.remove(line,do_unlink=True);bpy.data.curves.remove(curve)
finally:
 bpy.context.window.scene=prior
 for k in ['objects','meshes','curves','cameras','materials','images']:
  col=getattr(bpy.data,k)
  for item in set(col)-before[k]:
   if k=='objects':col.remove(item,do_unlink=True)
   elif item.users==0:col.remove(item)
 bpy.data.scenes.remove(scene)
with (run/(PREFIX+'blender.json')).open('x',encoding='utf8') as f:json.dump(dict(views=results,sceneRestored=set(bpy.data.objects)==before['objects']),f,indent=2)
print(json.dumps(dict(views=len(results),sceneRestored=set(bpy.data.objects)==before['objects'])))

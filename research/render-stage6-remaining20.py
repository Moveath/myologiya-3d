"""Addressed Blender MCP diagnostics. ROOT, RUN, CASES are supplied by caller."""
import json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

root,run=Path(ROOT),Path(RUN)
arrays=json.loads((run/'comparison-arrays.json').read_text(encoding='utf8'))
depth=json.loads((run/'comparison-depth.json').read_text(encoding='utf8'))['rows']
patch={(r['a'],r['b']):set(r['affectedSourceFaces']) for r in depth}
cases={
 'mc1-native-cmc':('native__metacarpal_1_left','live__trapezium_left',(0,0,1),.055),
 'mc1-mirror-mcp':('mirror__metacarpal_1_left','live__phalanx_prox_1_left',(0,0,1),.055),
 'mc3-native-base':('native__metacarpal_3_left','live__trapezoid_left',(.6,.3,1),.045),
 'mc3-mirror-base':('mirror__metacarpal_3_left','live__trapezoid_left',(.6,.3,1),.045),
 'hindfoot-native':('native__talus_left','native__calcaneus_left',(1,.4,.2),.10),
 'hindfoot-mirror':('mirror__talus_left','mirror__calcaneus_left',(1,.4,.2),.10),
 'midfoot-native':('native__cuboid_left','native__cuneiform_lat_left',(0,1,.1),.065),
 'midfoot-mixed':('mirror__cuboid_left','native__cuneiform_lat_left',(0,1,.1),.065),
 'hallux-native':('native__toe_prox_1_left','native__toe_dist_1_left',(0,1,.2),.065),
 'toe5-pip-native':('native__toe_prox_5_left','native__toe_mid_5_left',(0,1,.2),.05),
 'toe5-dip-native':('native__toe_mid_5_left','native__toe_dist_5_left',(0,1,.2),.035),
}
prior=bpy.context.window.scene
before={kind:set(getattr(bpy.data,kind)) for kind in ['objects','meshes','cameras','materials','images']}
scene=bpy.data.scenes.new('remaining20_diagnostic');results=[]
def bv(v):return Vector((v[0],-v[2],v[1]))
try:
 bpy.context.window.scene=scene
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=850;scene.render.resolution_y=850;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
 scene.render.image_settings.file_format='PNG'
 materials=[]
 for name,color in [('first',(1,.65,.2,1)),('second',(.3,.65,1,1)),('sampled_overlap',(1,.05,.05,1))]:
  m=bpy.data.materials.new(name);m.diffuse_color=color;materials.append(m)
 cd=bpy.data.cameras.new('diagnostic_camera');cam=bpy.data.objects.new('diagnostic_camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=10
 for name in CASES:
  a,b,offset,scale=cases[name];objects=[];centres=[];observed=[]
  for i,k in enumerate([a,b]):
   ar=arrays[k];v=np.asarray(ar['vertices']).reshape(-1,3);f=np.asarray(ar['faces']).reshape(-1,3)
   data=bpy.data.meshes.new(k);data.from_pydata([bv(q) for q in v],[],f.tolist());obj=bpy.data.objects.new(k,data);scene.collection.objects.link(obj);objects.append(obj)
   data.materials.append(materials[i]);data.materials.append(materials[2])
   marked=patch.get((k,b if k==a else a),set())
   for index in marked:data.polygons[index].material_index=1
   if marked:centres.extend(v[f[list(marked)]].mean(axis=1).tolist())
   observed.append(dict(id=k,triangles=len(f),highlightedFaces=len(marked),objectScale=list(obj.scale)))
  if not centres:centres=[np.asarray(arrays[k]['vertices']).reshape(-1,3).mean(0).tolist() for k in [a,b]]
  center=np.mean(centres,axis=0);cam.location=bv(center)+bv(offset);cam.rotation_euler=(bv(center)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
  file=run/(name+'.png')
  if file.exists():raise FileExistsError(file)
  scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
  results.append(dict(file=file.name,pair=[a,b],cameraCenter=center.tolist(),scale=scale,objects=observed))
  for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
finally:
 bpy.context.window.scene=prior
 for kind in ['objects','meshes','cameras','materials','images']:
  collection=getattr(bpy.data,kind)
  for item in set(collection)-before[kind]:
   if kind=='objects':collection.remove(item,do_unlink=True)
   elif item.users==0:collection.remove(item)
 bpy.data.scenes.remove(scene)
result=dict(views=results,sceneRestored=set(bpy.data.objects)==before['objects'],originalScene=prior.name,
 limitation='Red faces are sampled penetrating face centres, not independently segmented anatomical joint surfaces. No source/model edits.')
with (run/RESULT_NAME).open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(views=len(results),sceneRestored=result['sceneRestored'])))

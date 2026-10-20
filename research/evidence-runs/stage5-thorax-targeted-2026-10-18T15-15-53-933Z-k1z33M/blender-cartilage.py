from pathlib import Path
from contextlib import redirect_stdout
import bpy, json, io, tempfile, hashlib, base64
from mathutils import Vector
ROOT=Path("C:/Users/Пользователь/Desktop/учеба/Миология 3D"); OUT=Path("C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-thorax-targeted-2026-10-18T15-15-53-933Z-k1z33M")
old_scene=bpy.context.scene
old={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
paths=[ROOT/'build_thorax/thorax_hi.glb',ROOT/'site/arm-q-glb.txt']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
scene=bpy.data.scenes.new('Thorax cartilage read-only'); bpy.context.window.scene=scene
rows=[]; ribs=[]
def label(o):
 while o:
  if o.name.startswith(('b|','o|','c|')):return o.name.split('.')[0]
  o=o.parent
 return ''
try:
 with tempfile.TemporaryDirectory(prefix='thorax-cartilage-') as temp:
  for i,p in enumerate(paths):
   before={o.as_pointer() for o in scene.objects}; copy=Path(temp)/('model'+str(i)+'.glb')
   copy.write_bytes(base64.b64decode(p.read_bytes()) if p.suffix=='.txt' else p.read_bytes())
   with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
   bpy.context.view_layer.update()
   for o in scene.objects:
    if o.as_pointer() in before or o.type!='MESH':continue
    name=label(o); cartilage=(i==0 and name.startswith('o|thorax_costal_cartilages')) or (i==1 and name in ['c|'+x for x in ['FMA7875','FMA7886','FMA7913','FMA7976','FMA8070','FMA8194','FMA8248']])
    bone=i==0 and (name.startswith('b|rib_') or name.startswith('b|sternum'))
    o.hide_render=not(cartilage or bone)
    if cartilage or bone:
     pts=[o.matrix_world@Vector(c) for c in o.bound_box]
     # Blender z corresponds to atlas y, metres; only bounds, not landmarks.
     bounds=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]]
     if cartilage:rows.append(dict(source=str(p.relative_to(ROOT)),node=name,vertices=len(o.data.vertices),triangles=sum(len(x.vertices)-2 for x in o.data.polygons),blenderBounds_m=bounds,anatomicalLevelAccepted=False))
     else:ribs.append(dict(node=name,blenderBounds_m=bounds))
     o.color=(.1,.55,.8,1) if i==0 and cartilage else (.95,.55,.12,1) if cartilage else (.55,.6,.6,1)
 assert len(rows)==9,(len(rows),rows)
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=950;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_cavity=True
 scene.render.image_settings.file_format='PNG'
 cam=bpy.data.objects.new('cartilage camera',bpy.data.cameras.new('cartilage camera'));scene.collection.objects.link(cam);scene.camera=cam
 cam.data.type='ORTHO';cam.data.ortho_scale=.62
 center=Vector((0,-.1,1.25));cam.location=center+Vector((0,-1,0));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 target=OUT/'cartilage-context.png';assert not target.exists();scene.render.filepath=str(target)
 with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
finally:
 bpy.context.window.scene=old_scene
 for o in list(bpy.data.objects):
  if o.as_pointer() not in old['objects']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.scenes.remove(scene)
 for kind in ('meshes','materials','images','cameras','worlds'):
  coll=getattr(bpy.data,kind)
  for o in list(coll):
   if o.as_pointer() not in old[kind] and o.users==0:coll.remove(o)
assert {o.as_pointer() for o in bpy.data.objects}==old['objects']
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
result=dict(status='passed',hashes=hashes,meshes=rows,ribBounds=ribs,originalScenePreserved=True,modelsUnchanged=True,acceptedCoordinates=0,acceptedCartilageContours=0,screenshot=str(target.relative_to(ROOT)))
with (OUT/'blender-cartilage.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',cartilageMeshes=len(rows),levelAssignmentsAccepted=0,scenePreserved=True)))

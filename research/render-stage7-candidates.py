"""Executed inside Blender MCP; review copies, restore the user's scene."""
import bpy,json,pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Пользователь/Desktop/учеба/Миология 3D')
RUN=ROOT/'research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT'
rows=json.loads((RUN/'context-arrays.json').read_text())
old=bpy.context.window.scene
results=[]
try:
 for group in ['neck','pelvis']:
  scene=bpy.data.scenes.new('Stage7 review '+group);bpy.context.window.scene=scene
  for row in rows:
   if (row['file']=='neck') != (group=='neck'):continue
   if row['name'].startswith('m|omohyoid'):continue
   v=list(zip(*[iter(row['positions'])]*3));f=list(zip(*[iter(row['indices'])]*3))
   mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata(v,[],f);mesh.update()
   o=bpy.data.objects.new(row['name'],mesh);scene.collection.objects.link(o);o.color=(.68,.64,.50,1) if row['name'].startswith('b|') else (.4,.2,.45,1)
  ids=['FMA71309','FMA71442','FMA71443']if group=='neck'else['FMA45856','FMA45857']
  for fid in ids:
   # Source GLB is Y-up; Blender importer rotates to Z-up. Convert imported
   # vertex world coordinates back for this Three.js-space review scene.
   before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'build_stage7/source_trials'/f'{fid}.glb'))
   for o in set(scene.objects)-before:
    if o.type!='MESH':continue
    world=[o.matrix_world@v.co for v in o.data.vertices]
    o.matrix_world.identity()
    for vertex,w in zip(o.data.vertices,world):vertex.co=(w.x,w.z,-w.y)
    o.color=({'FMA71309':(.12,.65,.75,1),'FMA71442':(.85,.28,.12,1),'FMA71443':(.6,.25,.8,1)}.get(fid,(.85,.2,.15,1)))
    o.data.calc_loop_triangles();results.append(dict(id=fid,triangles=len(o.data.loop_triangles),vertices=len(o.data.vertices),bounds=[list(min(v.co[i] for v in o.data.vertices) for i in range(3)),list(max(v.co[i] for v in o.data.vertices) for i in range(3))]))
  scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
  scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Stage7 white '+group);scene.world.color=(.8,.8,.8)
  scene.render.resolution_x=1000;scene.render.resolution_y=850;scene.render.resolution_percentage=100
  camera=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
  target=Vector((0,1.44,.065)if group=='neck'else(0,.80,.07));camera.data.ortho_scale=.17 if group=='neck'else .31
  for view,direction in [('posterior',(1,.3,-2)),('inferior',(0,-2,.5))]if group=='pelvis'else[('posterior',(1,.2,-2)),('anterior',(1,.2,2))]:
   camera.location=target+Vector(direction)*.3;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
   scene.render.filepath=str(RUN/f'blender-{group}-{view}.png');bpy.ops.render.render(write_still=True)
 with(RUN/'blender-candidates.json').open('x',encoding='utf8')as f:json.dump(results,f,indent=2)
finally:
 bpy.context.window.scene=old
print(json.dumps(results))

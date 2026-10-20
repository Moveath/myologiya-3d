"""Blender MCP read-only lumbar inspection. OUT must be a new evidence run."""
from pathlib import Path
import bpy, hashlib, json, io, tempfile
from contextlib import redirect_stdout
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
source=ROOT/'build_context_bones/leg_extra_hi.glb';digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={k:{x.as_pointer() for x in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Lumbar read-only review');bpy.context.window.scene=scene
rows=[];images=[]
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
try:
    with tempfile.TemporaryDirectory(prefix='atlas-lumbar-review-') as td:
        copy=Path(td)/'copy.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={owner(o):o for o in scene.objects if o.type=='MESH' and (owner(o) or '').startswith('lumbar_')}
    assert set(bones)=={f'lumbar_{i}' for i in range(1,6)}
    for bone,obj in sorted(bones.items()):
        pts=[obj.matrix_world@Vector(v) for v in obj.bound_box]
        lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
        rows.append(dict(bone=bone,vertices=len(obj.data.vertices),triangles=sum(len(p.vertices)-2 for p in obj.data.polygons),
            dimensionsMm=list((hi-lo)*1000),matrixDeterminant=obj.matrix_world.determinant(),
            anatomicalCoordinatesAccepted=0,contoursAccepted=0))
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=800;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_cavity=True
    scene.render.image_settings.file_format='PNG'
    cam=bpy.data.objects.new('review camera',bpy.data.cameras.new('review camera'));scene.collection.objects.link(cam);scene.camera=cam
    cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=20
    for bone in ('lumbar_1','lumbar_5'):
        obj=bones[bone];pts=[obj.matrix_world@Vector(v) for v in obj.bound_box]
        lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
        center=(lo+hi)/2
        for o in scene.objects:
            if o.type=='MESH':o.hide_render=o!=obj;o.color=(.72,.72,.66,1)
        for label,offset in [('superior',(0,0,.3)),('posterior_oblique',(.13,.17,.15))]:
            cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(hi-lo)*1.35
            path=OUT/(bone+'-'+label+'.png');assert not path.exists();scene.render.filepath=str(path)
            with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
            images.append(str(path.relative_to(ROOT)))
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in old_data['objects']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for kind in ('meshes','materials','images','cameras','worlds'):
        for item in list(getattr(bpy.data,kind)):
            if item.as_pointer() not in old_data[kind] and item.users==0:getattr(bpy.data,kind).remove(item)
assert {o.as_pointer() for o in bpy.data.objects}==old_data['objects']
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
with (OUT/'blender-lumbar.json').open('x',encoding='utf8') as f:
    json.dump(dict(status='passed',source=str(source.relative_to(ROOT)),sourceSha256=digest,sourceUnchanged=True,originalScenePreserved=True,rows=rows,images=images,
        scope='Whole meshes only. No pre-existing lumbar coordinates, accepted masks or new geometric landmarks.'),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',meshes=len(rows),images=len(images),anatomicallyAcceptedCoordinates=0)))

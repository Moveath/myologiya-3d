"""MCP visual review after review_shared_expansion_blender.py; disposable scenes only."""
import json, io
from contextlib import redirect_stdout
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'verify/shared-expansion-geometry.json').read_text(encoding='utf-8'))['points']
out=ROOT/'shots/shared-landmarks';out.mkdir(exist_ok=True,parents=True)
original=bpy.context.scene
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
for row in rows:
    scene=next(s for s in bpy.data.scenes if s.name=='Shared review '+Path(row['model']).name)
    bpy.context.window.scene=scene
    for obj in scene.objects:
        obj.hide_render=owner(obj) not in row['related']
        if obj.type=='MESH':obj.color=(.65,.78,.95,1) if owner(obj)==row['related'][0] else (.95,.73,.48,1)
    x,y,z=row['p'];point=Vector((x,-z,y))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.0008,location=point)
    marker=bpy.context.object;marker.name='Review marker';marker.color=(1,.02,.04,1)
    camera=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    views=[('lateral',Vector((-1,-.5,.5))),('superior',Vector((-.4,0,1)))] if row['id']=='cal_sinus_tarsi' else [('oblique',Vector((0,.8,1)) if 'occipital' in row['id'] else Vector((0,-.4,1)))]
    camera.data.ortho_scale=.09 if row['id']=='cal_sinus_tarsi' else .08
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.render.resolution_x=800;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    for name,direction in views:
        camera.location=point+direction.normalized()*.3
        camera.rotation_euler=(point-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(row['id']+'-'+name+'.png'))
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
bpy.context.window.scene=original
print('Rendered five review views; source files unchanged')

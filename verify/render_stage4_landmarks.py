"""Run through Blender MCP after the measurement scripts; review images only."""
from pathlib import Path
import bpy, json, io
from contextlib import redirect_stdout
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'shots/stage4-2026-10-15'
original=bpy.context.scene
scene=bpy.data.scenes.get('Shared landmark measurement')
assert scene is not None
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
cases=[]
for p in json.loads((ROOT/'research/shared-landmarks-geometry.json').read_text(encoding='utf8'))['candidates']:
    side='right' if p['bone'].endswith('right') else 'left'
    cases.append((f'jugular-{side}',[p['bone'],'occipital'],p['p'],.065,
                  [('inferior',(0,0,-1)),('superior',(0,0,1))]))
for side in ('right','left'):
    cases.append((f'zygomaticotemporal-{side}',[f'temporal_{side}',f'zygomatic_{side}'],None,.17,
                  [('lateral',(-1 if side=='right' else 1,-.15,0)),('inferior',(0,0,-1))]))
images=[]
try:
    bpy.context.window.scene=scene
    camera=bpy.data.objects.new('Stage4 review camera',bpy.data.cameras.new('Stage4 review camera'))
    scene.collection.objects.link(camera); scene.camera=camera;camera.data.type='ORTHO'
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
    scene.render.resolution_x=900;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    for label,bones,p,width,views in cases:
        visible=[]
        for obj in scene.objects:
            b=owner(obj)
            obj.hide_render=obj.type!='MESH' or b not in bones
            if obj.type=='MESH' and b in bones:
                obj.color=(.65,.78,.95,1) if b==bones[0] else (.95,.73,.48,1)
                visible.extend(obj.matrix_world@Vector(c) for c in obj.bound_box)
        if p is not None:
            x,y,z=p;center=Vector((x,-z,y))
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.0006,location=center)
            marker=bpy.context.object;marker.name='Existing jugular anchor';marker.color=(1,.02,.04,1)
        else:
            center=Vector(tuple((min(v[i] for v in visible)+max(v[i] for v in visible))/2 for i in range(3)))
        camera.data.ortho_scale=width
        for view,direction in views:
            camera.location=center+Vector(direction).normalized()*.3
            camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            path=OUT/(label+'-'+view+'.png');scene.render.filepath=str(path)
            with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
            images.append(str(path.relative_to(ROOT)))
finally:
    bpy.context.window.scene=original
(ROOT/'research/stage4-2026-10-15/review-images.json').write_text(json.dumps(images,indent=2),encoding='utf8')
print('Rendered',len(images),'views; existing pins only; no mesh export.')


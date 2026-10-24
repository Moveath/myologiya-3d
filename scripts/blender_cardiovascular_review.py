"""Run in Blender MCP, isolated review scene. Does not modify original resources."""
import bpy,json,pathlib,base64
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=ROOT/'build_cardiovascular/bp3d-3.0-v1'
def setup():
    scene=bpy.data.scenes.new('CV_Review_20261022');bpy.context.window.scene=scene
    scene.unit_settings.system='METRIC'
    for p in sorted(BUILD.glob('*.glb')):
        bpy.ops.import_scene.gltf(filepath=str(p))
    # Existing thorax provides an unchanged coordinate/scale reference.
    p=ROOT/'build_cardiovascular/thorax-context.glb'
    if not p.exists():p.write_bytes(base64.b64decode((ROOT/'site/thorax-glb.txt').read_text().strip()))
    bpy.ops.import_scene.gltf(filepath=str(p))
    records=[]
    for o in scene.objects:
        if o.type!='MESH':continue
        owner=o
        while owner and not owner.name.startswith(('s|','b|')):owner=owner.parent
        iscv=owner and owner.name.startswith('s|')
        o.hide_render=not iscv
        if iscv:
            bounds=[o.matrix_world@Vector(v)for v in o.bound_box]
            records.append(dict(owner=owner.name,faces=len(o.data.polygons),bounds=[[min(v[i]for v in bounds)for i in range(3)],[max(v[i]for v in bounds)for i in range(3)]]))
            mat=bpy.data.materials.new('review_'+owner.name);mat.diffuse_color=(.75,.24,.23,1)if's|cv_a_'in owner.name else(.2,.35,.7,1)if's|cv_v_'in owner.name else(.72,.43,.4,1)
            o.data.materials.clear();o.data.materials.append(mat)
    (ROOT/'build_cardiovascular/blender-import.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    camera=bpy.data.objects.new('CV_review_camera',bpy.data.cameras.new('CV_review_camera'));scene.collection.objects.link(camera);scene.camera=camera
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.world=bpy.data.worlds.new('CV_review_world');scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'build_cardiovascular/review.blend'),copy=True)
    print(json.dumps({'scene':scene.name,'imported':len(records),'faces':sum(r['faces']for r in records)}))
def render(name,view='anterior',context=False):
    scene=bpy.context.scene
    for o in scene.objects:
        if o.type!='MESH':continue
        owner=o
        while owner and not owner.name.startswith(('s|','b|')):owner=owner.parent
        iscv=owner and owner.name.startswith('s|')
        o.hide_render=not iscv and not(context and owner and owner.name.startswith('b|'))
    # Blender glTF import restores Z-up; anterior is negative Y here.
    center=Vector((0,-.12,1.22));direction=Vector({'anterior':(0,-1,0),'left':(1,0,0),'posterior':(0,1,0),'overview':(.5,-1,.2)}[view])
    scene.camera.location=center+direction.normalized()*.7
    scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=.65 if view=='overview'else .3
    scene.render.filepath=str(ROOT/'build_cardiovascular'/name);bpy.ops.render.render(write_still=True)
    print(scene.render.filepath)

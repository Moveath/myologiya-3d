"""Addressed read-only occipital/joint views. No surface proximity acceptance."""
from pathlib import Path
import hashlib, io, json, tempfile, sys
from contextlib import redirect_stdout
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch2-2026-10-16'
sys.path.insert(0,str(ROOT/'scripts'))
from head_localization import positions
from head_skull_batch2 import BILATERAL_OCCIPITAL
source=ROOT/'build_head/head_hi.glb'; digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene; old_objects={o.as_pointer() for o in bpy.data.objects}
scene=bpy.data.scenes.new('Skull batch2 read-only');bpy.context.window.scene=scene
images=[]; records=[]
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
try:
    with tempfile.TemporaryDirectory(prefix='atlas-skull-b2-') as td:
        copy=Path(td)/'head.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH':bones.setdefault(b,[]).append(obj)
    assert len(bones)==22
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('batch2 white world');scene.world.color=(0.8,0.8,0.8)
    scene.render.image_settings.file_format='PNG'
    camera=bpy.data.objects.new('batch2 camera',bpy.data.cameras.new('batch2 camera'));scene.collection.objects.link(camera);scene.camera=camera
    camera.data.type='ORTHO';camera.data.lens=50;camera.data.clip_start=.001;camera.data.clip_end=20
    views=[
      ('occipital-internal',{'occipital'},(0,-.19,1.54),(0,-.045,1.54),.19),
      ('occipital-inferior',{'occipital'},(0,-.055,1.25),(0,-.055,1.53),.20),
      ('jugular-base',{'occipital','temporal_right','temporal_left'},(0,-.08,1.25),(0,-.06,1.52),.21),
      ('zygomatic-right',{'temporal_right','zygomatic_right','maxilla_right'},(-.24,-.17,1.53),(-.055,-.08,1.53),.16),
      ('zygomatic-left',{'temporal_left','zygomatic_left','maxilla_left'},(.24,-.17,1.53),(.055,-.08,1.53),.16),
    ]
    palette={'occipital':(.73,.68,.51,1),'temporal_right':(.46,.65,.77,1),'temporal_left':(.46,.65,.77,1),'zygomatic_right':(.65,.77,.48,1),'zygomatic_left':(.65,.77,.48,1),'maxilla_right':(.80,.62,.46,1),'maxilla_left':(.80,.62,.46,1)}
    for name,visible,eye,target,scale in views:
        for obj in list(scene.objects):
            if obj.type=='MESH':
                obj.hide_render=owner(obj) not in visible;obj.color=palette.get(owner(obj),(.7,.7,.7,1))
        camera.location=eye;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
        path=OUT/(name+'.png');scene.render.filepath=str(path)
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
        images.append({'file':str(path.relative_to(ROOT)),'bones':sorted(visible),'camera':list(eye),'target':list(target),'purpose':'diagnostic view only; colours temporary, no app colour system or model changes'})
    for (bone,code),row in positions().items():
        if bone!='occipital':continue
        number=int(code.rsplit('.',1)[1]);x=row['p'][0]
        records.append({'id':'head_'+bone+'_'+code.replace('.','_'),'code':code,'p':row['p'],
                        'source_file':row['source_file'],'bilateralTerm':number in BILATERAL_OCCIPITAL,
                        'coordinateHalfSpace':'right' if x<0 else 'left' if x>0 else 'midplane',
                        'halfSpaceIsNotAnatomicalSideAcceptance':True,'anatomicalPlacementAccepted':False})
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in old_objects:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
assert {o.as_pointer() for o in bpy.data.objects}==old_objects
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'passed','tool':'Blender MCP','date':'2026-10-16','source':'build_head/head_hi.glb','sourceSha256':digest,
        'sourceUnchanged':True,'originalScenePreserved':True,'records':records,'images':images,
        'scope':'origin/coordinate half-space and diagnostic views; no new coordinates, contours, widths or specimen-specific anatomical acceptance'}
(OUT/'blender-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','occipitalRecords':len(records),'images':len(images),'originalModelUnchanged':True}))

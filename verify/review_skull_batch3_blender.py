"""Read-only views and provenance checks; distances are not anatomy acceptance."""
from pathlib import Path
import hashlib, io, json, tempfile, sys
from contextlib import redirect_stdout
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch3-2026-10-16'
sys.path.insert(0,str(ROOT/'scripts'))
from head_localization import positions
from head_skull_batch2 import BILATERAL_OCCIPITAL
source=ROOT/'build_head/head_hi.glb'; digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={kind:{o.as_pointer() for o in getattr(bpy.data,kind)} for kind in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Skull batch3 read-only');bpy.context.window.scene=scene
images=[];records=[]

def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent

try:
    with tempfile.TemporaryDirectory(prefix='atlas-skull-b3-') as td:
        copy=Path(td)/'head.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH':bones.setdefault(b,[]).append(obj)
    assert len(bones)==22
    trees={}
    for b in ('frontal','ethmoid','sphenoid','occipital'):
        trees[b]=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                     [tuple(p.vertices) for p in o.data.polygons]) for o in bones[b]]
    for (bone,code),row in positions().items():
        if not (bone=='occipital' and int(code.rsplit('.',1)[1]) in BILATERAL_OCCIPITAL) and (bone,code) not in [('frontal','A02.1.03.018'),('sphenoid','A02.1.05.023')]:continue
        point=Vector((row['p'][0],-row['p'][2],row['p'][1]))
        targets=('frontal','ethmoid') if code=='A02.1.03.018' else ('sphenoid','frontal') if code=='A02.1.05.023' else ('occipital',)
        distances={b:min(tree.find_nearest(point)[3] for tree in trees[b])*1000 for b in targets}
        records.append({'id':'head_'+bone+'_'+code.replace('.','_'),'code':code,'sourceFile':row['source_file'],
                        'p':row['p'],'n':row['n'],'localization':row['localization'],
                        'nearestSurfaceMm':distances,'coordinateX':row['p'][0],
                        'anatomicalSideAccepted':False,'fullExtentAccepted':False})
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('batch3 world');scene.world.color=(.8,.8,.8)
    scene.render.image_settings.file_format='PNG'
    camera=bpy.data.objects.new('batch3 camera',bpy.data.cameras.new('batch3 camera'));scene.collection.objects.link(camera);scene.camera=camera
    camera.data.type='ORTHO';camera.data.clip_start=.001;camera.data.clip_end=20
    views=[
      ('frontal-ethmoid-internal',{'frontal','ethmoid'},(0,.04,1.60),(0,-.15,1.545),.13),
      ('orbital-right',{'frontal','sphenoid'},(-.06,-.30,1.535),(-.03,-.14,1.535),.10),
      ('orbital-left',{'frontal','sphenoid'},(.06,-.30,1.535),(.03,-.14,1.535),.10),
      ('coronal-sagittal',{'frontal','parietal_right','parietal_left'},(0,-.23,1.85),(0,-.07,1.62),.23),
      ('occipital-internal-right',{'occipital'},(-.13,-.22,1.57),(-.025,-.055,1.54),.14),
      ('occipital-internal-left',{'occipital'},(.13,-.22,1.57),(.025,-.055,1.54),.14),
      ('jugular-right',{'occipital','temporal_right'},(-.045,-.08,1.32),(-.035,-.075,1.51),.105),
      ('jugular-left',{'occipital','temporal_left'},(.045,-.08,1.32),(.035,-.075,1.51),.105),
    ]
    palette={'frontal':(.75,.68,.52,1),'ethmoid':(.56,.72,.58,1),'sphenoid':(.48,.64,.78,1),'occipital':(.75,.68,.52,1)}
    for name,visible,eye,target,scale in views:
        for obj in scene.objects:
            if obj.type=='MESH':obj.hide_render=owner(obj) not in visible;obj.color=palette.get(owner(obj),(.60,.68,.76,1))
        camera.location=eye;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
        path=OUT/(name+'.png');scene.render.filepath=str(path)
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
        images.append({'file':str(path.relative_to(ROOT)),'bones':sorted(visible),'camera':list(eye),'target':list(target),'purpose':'diagnostic only; not new app colours or model geometry'})
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in old_data['objects']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for kind in ('meshes','materials','images','cameras','worlds'):
        collection=getattr(bpy.data,kind)
        for item in list(collection):
            if item.as_pointer() not in old_data[kind] and item.users==0:collection.remove(item)
assert {o.as_pointer() for o in bpy.data.objects}==old_data['objects']
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'passed','tool':'Blender MCP','date':'2026-10-16','source':'build_head/head_hi.glb','sourceSha256':digest,
        'sourceUnchanged':True,'originalScenePreserved':True,'records':records,'images':images,
        'scope':'surface distances/provenance and diagnostic views; no anatomical localization, curves, widths or shape acceptance'}
(OUT/'blender-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','records':len(records),'images':len(images),'originalModelUnchanged':True}))

"""Read-only views and provenance checks; distances are not anatomy acceptance."""
from pathlib import Path
import hashlib, io, json, tempfile, sys
from contextlib import redirect_stdout
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch6-2026-10-16'
sys.path.insert(0,str(ROOT/'scripts'))
from head_localization import positions
from head_skull_batch6 import reviewed_decisions
selected=reviewed_decisions()

source=ROOT/'build_head/head_hi.glb'; digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={kind:{o.as_pointer() for o in getattr(bpy.data,kind)} for kind in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Skull batch6 read-only');bpy.context.window.scene=scene
images=[];records=[]

def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent

try:
    with tempfile.TemporaryDirectory(prefix='atlas-skull-b6-') as td:
        copy=Path(td)/'head.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH':bones.setdefault(b,[]).append(obj)
    assert len(bones)==22
    trees={}
    for b in ('maxilla_right','maxilla_left','palatine_right','palatine_left'):
        trees[b]=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                     [tuple(p.vertices) for p in o.data.polygons]) for o in bones[b]]
    for (bone,code),row in positions().items():
        if (bone,code) not in selected:continue
        point=Vector((row['p'][0],-row['p'][2],row['p'][1]))
        targets=(bone,)
        distances={b:min(tree.find_nearest(point)[3] for tree in trees[b])*1000 for b in targets}
        records.append({'id':'head_'+bone+'_'+code.replace('.','_'),'code':code,'sourceFile':row['source_file'],
                        'p':row['p'],'n':row['n'],'localization':row['localization'],
                        'nearestSurfaceMm':distances,'coordinateX':row['p'][0],
                        'anatomicalSideAccepted':False,'fullExtentAccepted':False})
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('batch6 world');scene.world.color=(.8,.8,.8)
    scene.render.image_settings.file_format='PNG'
    camera=bpy.data.objects.new('batch6 camera',bpy.data.cameras.new('batch6 camera'));scene.collection.objects.link(camera);scene.camera=camera
    camera.data.type='ORTHO';camera.data.clip_start=.001;camera.data.clip_end=20
    views=[]
    for bone in ('maxilla_right','maxilla_left','palatine_right','palatine_left'):
        coords=[o.matrix_world@Vector(v) for o in bones[bone] for v in o.bound_box]
        lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
        hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
        center=(lo+hi)/2;size=max(hi-lo)*1.5
        nums=[int(c.rsplit('.',1)[1]) for b,c in selected if b==bone]
        medial=Vector((.20 if bone.endswith('right') else -.20,0,.02))
        for label,direction in [('medial',medial),('inferior',Vector((0,0,-.20)))]:
            views.append((bone+'-'+label,{bone},tuple(center+direction),tuple(center),size,(bone,nums)))
    all_bones={'maxilla_right','maxilla_left','palatine_right','palatine_left'}
    coords=[o.matrix_world@Vector(v) for bone in all_bones for o in bones[bone] for v in o.bound_box]
    center=Vector(tuple((min(v[i] for v in coords)+max(v[i] for v in coords))/2 for i in range(3)))
    for label,direction in [('inferior',Vector((0,0,-.20))),('superior',Vector((0,0,.20)))]:
        views.append(('assembled-palate-'+label,all_bones,tuple(center+direction),tuple(center),.13,(None,[])))
    palette={'maxilla_right':(.75,.68,.52,1),'maxilla_left':(.75,.68,.52,1),'palatine_right':(.48,.64,.78,1),'palatine_left':(.48,.64,.78,1)}
    for name,visible,eye,target,scale,marker_selection in views:
        for obj in scene.objects:
            if obj.type=='MESH':obj.hide_render=owner(obj) not in visible;obj.color=palette.get(owner(obj),(.60,.68,.76,1))
        dots=[];marked=[]
        for (b,c),row in positions().items():
            if (b,c) not in selected or b!=marker_selection[0]:continue
            p=row['p'];bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.0008,location=(p[0],-p[2],p[1]))
            dot=bpy.context.object;dot.name='audit_point_'+c;dot.color=(.9,.04,.03,1);dots.append(dot)
            marked.append({'id':'head_'+b+'_'+c.replace('.','_'),'p':p,'glyphRadiusM':.0008})
        camera.location=eye;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
        path=OUT/(name+'.png');scene.render.filepath=str(path)
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
        images.append({'file':str(path.relative_to(ROOT)),'bones':sorted(visible),'camera':list(eye),'target':list(target),'markers':marked,'purpose':'red dots are old point coordinates, not contours; glyph radius is display only'})
        for dot in dots:bpy.data.objects.remove(dot,do_unlink=True)
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

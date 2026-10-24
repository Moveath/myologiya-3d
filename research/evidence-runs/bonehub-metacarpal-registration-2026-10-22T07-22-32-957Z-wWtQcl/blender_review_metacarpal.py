"""MCP: runpy.run_path(..., init_globals={'OWNER':'metacarpal_1_left'}).
One owner per invocation; three workbench views, new scene/library, old scene restored.
Saved positions are source-to-BP3D rigid test transforms; no fitting in Blender.
"""
import bpy, json, pathlib, math, time
from mathutils import Vector, Matrix
RUN=pathlib.Path(__file__).resolve().parent
OWNER=globals().get('OWNER','metacarpal_1_left')
assert OWNER in ['metacarpal_1_left','metacarpal_3_left']
OLD=RUN.parent/'stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj'
arrays=json.loads((OLD/'comparison-arrays.json').read_text())
candidate=json.loads((RUN/(OWNER+'-registered-arrays.json')).read_text())
diagnostic=json.loads((RUN/(OWNER+'-neighbors-summary.json')).read_text())
names=[r['neighbor'] for r in diagnostic['results'] if not r.get('aabbDisjoint')]
paths=[RUN/(OWNER+'-blender-'+view+'.png') for view in ['positive-z','negative-z','oblique']]
blend=RUN/(OWNER+'-review.blend'); report=RUN/(OWNER+'-blender.json')
assert not any(p.exists() for p in paths+[blend,report]),'refuse historical overwrite'
start=time.monotonic();oldscene=bpy.context.window.scene
def coord(v):return (v[0],-v[2],v[1])
def add(name,arr,color):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([coord(arr['vertices'][i:i+3]) for i in range(0,len(arr['vertices']),3)],[],[arr['faces'][i:i+3] for i in range(0,len(arr['faces']),3)])
    mesh.update();obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.color=color
    for p in mesh.polygons:p.use_smooth=True
    return obj
try:
    scene=bpy.data.scenes.new('BoneHub '+OWNER+' TEST NOT ADMITTED');bpy.context.window.scene=scene
    scene.unit_settings.system='METRIC'
    for name in names:add(name,arrays[name],(.65,.61,.49,1))
    obj=add('b|'+OWNER,candidate,(.06,.56,.68,1));obj['admission']='test_only';obj['method']='rigid shape registration, scale1, no reflection';obj['source']='BoneHub CC BY4.0; commit7d520ffe'
    # Red polygons are a few existing BVH diagnostic examples, not articular masks.
    material=bpy.data.materials.new(OWNER+' candidate cyan');material.diffuse_color=(.06,.56,.68,1)
    red=bpy.data.materials.new(OWNER+' diagnostic crossing examples');red.diffuse_color=(.9,.08,.06,1)
    obj.data.materials.append(material);obj.data.materials.append(red)
    faceids={e['candidateFace'] for r in diagnostic['results'] for e in r.get('examples',[])}
    for i in faceids:obj.data.polygons[i].material_index=1
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    # Assign neighbour materials explicitly under MATERIAL shading.
    for o in scene.objects:
        if o.type=='MESH' and o!=obj:
            m=bpy.data.materials.new(o.name+' ivory');m.diffuse_color=o.color;o.data.materials.append(m)
    scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True;scene.display.shading.background_type='WORLD'
    scene.world=bpy.data.worlds.new(OWNER+' review world');scene.world.color=(.075,.085,.095)
    scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    camera=bpy.data.objects.new(OWNER+' review camera',bpy.data.cameras.new(OWNER+' review camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.11
    points=[Vector(coord(candidate['vertices'][i:i+3])) for i in range(0,len(candidate['vertices']),3)]
    target=sum(points,Vector())/len(points)
    views=[]
    for (view,direction),filename in zip([('positive-z',(0,0,1)),('negative-z',(0,0,-1)),('oblique',(1,.2,.65))],paths):
        if time.monotonic()-start>40:raise TimeoutError('40 sec budget before next render; previous views retained')
        camera.location=target+Vector(coord(direction)).normalized()*.25
        forward=(target-camera.location).normalized();right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward)
        camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
        scene.render.filepath=str(filename);bpy.ops.render.render(write_still=True)
        views.append(filename.name)
        checkpoint=RUN/(OWNER+'-blender-'+view+'.json')
        with checkpoint.open('x',encoding='utf8') as f:json.dump({'status':'rendered','owner':OWNER,'view':view,'file':filename.name,'elapsedSeconds':time.monotonic()-start},f)
    bpy.data.libraries.write(str(blend),{scene},fake_user=True)
    result={'status':'technical_review_scene_created','owner':OWNER,'scene':scene.name,'triangles':len(obj.data.polygons),'vertices':len(obj.data.vertices),'finiteNormals':all(all(math.isfinite(x) for x in p.normal) for p in obj.data.polygons),'markedExampleFaces':len(faceids),'views':views,'blend':blend.name,'elapsedSeconds':time.monotonic()-start,'admitted':False,'warning':'Red patches show sampled diagnostic crossing faces, not anatomical segmentations. Visual acceptance must be recorded separately.'}
    with report.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
finally:
    bpy.context.window.scene=oldscene
print(json.dumps(result))

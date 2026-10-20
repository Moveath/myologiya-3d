"""Blender MCP: immutable arm/forearm models, distances and illustrative views."""
import base64, hashlib, io, json, tempfile
from contextlib import redirect_stdout
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
pins=json.loads((OUT/'atlas-before.json').read_text(encoding='utf8'))['pins']
files=['site/arm-q-glb.txt','build_context_bones/arm_extra_hi.glb']
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Arm forearm read-only review'); bpy.context.window.scene=scene
records=[]; metrics=[]; images=[]
def owner(obj):
    while obj:
        if obj.name.startswith(('b|','o|')):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
try:
    for f in files:
        with tempfile.TemporaryDirectory(prefix='atlas-girdle-') as td:
            raw=(ROOT/f).read_bytes(); copy=Path(td)/'copy.glb'
            copy.write_bytes(base64.b64decode(raw) if f.endswith('.txt') else raw)
            with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={b:[] for b in ('humerus','radius','ulna','interosseous_membrane','humerus_left')}
    for o in scene.objects:
        if o.type=='MESH' and owner(o) in bones:bones[owner(o)].append(o)
    for bone,objects in bones.items():
        assert objects,bone
        verts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
        trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in objects]
        metrics.append(dict(bone=bone,meshObjects=len(objects),vertices=len(verts),
            triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),
            boundsBlenderM=[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]],
            attributes=[dict(name=o.name,attributes=[a.name for a in o.data.attributes],groups=[g.name for g in o.vertex_groups]) for o in objects],anatomyAccepted=False))
        for p in pins:
            if p['b']==bone and p.get('p'):
                x,y,z=p['p']; distance=min(t.find_nearest(Vector((x,-z,y)))[3] for t in trees)*1000
                records.append(dict(id=p['id'],bone=bone,nearestSurfaceMm=distance,anatomyAccepted=False))
    scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=800; scene.render.resolution_y=650; scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='OBJECT'; scene.display.shading.show_cavity=True
    scene.render.image_settings.file_format='PNG'
    cam=bpy.data.objects.new('review camera',bpy.data.cameras.new('review camera')); scene.collection.objects.link(cam); scene.camera=cam
    cam.data.type='ORTHO'; cam.data.clip_start=.001; cam.data.clip_end=20
    for bone,objects in bones.items():
        pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
        lo=Vector([min(p[i] for p in pts) for i in range(3)]); hi=Vector([max(p[i] for p in pts) for i in range(3)]); center=(lo+hi)/2
        views=[('anterior',(0,-.4,0)),('posterior',(0,.4,0))] if bone != 'interosseous_membrane' else [('anterior',(0,-.4,0))]
        for label,offset in views:
            for o in scene.objects:
                if o.type=='MESH':o.hide_render=owner(o)!=bone; o.color=(.72,.72,.68,1)
            dots=[]; ids=[]
            for p in pins:
                if p['b']!=bone or not p.get('p'):continue
                x,y,z=p['p']; bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.0008,location=(x,-z,y))
                dot=bpy.context.object; dot.color=(.95,.03,.03,1); dots.append(dot); ids.append(p['id'])
            cam.location=center+Vector(offset); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=max(hi-lo)*1.25
            file=OUT/(bone+'-'+label+'.png'); assert not file.exists(); scene.render.filepath=str(file)
            with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
            images.append(dict(file=str(file.relative_to(ROOT)),bone=bone,view=label,markerIds=ids,glyphRadiusM=.0008))
            for d in dots:bpy.data.objects.remove(d,do_unlink=True)
finally:
    bpy.context.window.scene=old_scene
    for o in list(bpy.data.objects):
        if o.as_pointer() not in old_data['objects']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for k in ('meshes','materials','images','cameras','worlds'):
        for d in list(getattr(bpy.data,k)):
            if d.as_pointer() not in old_data[k] and d.users==0:getattr(bpy.data,k).remove(d)
assert old_data['objects']=={o.as_pointer() for o in bpy.data.objects}
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes.items())
result=dict(status='passed',models=metrics,records=records,images=images,hashes=hashes,sourceModelsUnchanged=True,originalScenePreserved=True,
    acceptedCoordinates=0,acceptedMasks=0,scope='Mesh proximity and side/extent plausibility only. No anatomy inferred from distance.')
with (OUT/'blender-arm-forearm.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(meshes=len(metrics),anchors=len(records),images=len(images),maximumDistanceMm=max(p['nearestSurfaceMm'] for p in records))))


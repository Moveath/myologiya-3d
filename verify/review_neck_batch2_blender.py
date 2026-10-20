"""Addressed read-only views of unresolved neck regions, executed by Blender MCP.
OUT must be a fresh evidence-run directory. No landmark coordinates are authored.
"""
from pathlib import Path
from contextlib import redirect_stdout
import hashlib, io, json, tempfile
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
source=ROOT/'build_neck/neck_hi.glb'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Neck batch2 read-only'); bpy.context.window.scene=scene
metrics=[]; measured=[]; images=[]

def owner(obj):
    while obj:
        if obj.name.startswith('b|'): return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent

try:
    with tempfile.TemporaryDirectory(prefix='neck-batch2-') as tmp:
        copy=Path(tmp)/'neck.glb'; copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()): bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH': bones.setdefault(b,[]).append(obj)
    assert len(bones)==8
    bounds={}
    for b,objects in bones.items():
        points=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
        low=Vector([min(p[i] for p in points) for i in range(3)])
        high=Vector([max(p[i] for p in points) for i in range(3)])
        bounds[b]=((low+high)/2, max(high-low)*1.4)
        metrics.append(dict(bone=b,meshNames=[o.name for o in objects],vertices=sum(len(o.data.vertices) for o in objects),
            triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),dimensionsMm=list((high-low)*1000),
            semanticSubregionsAccepted=False))
    wanted={('atlas','A02.2.02.102'),('axis','A02.2.02.202'),('hyoid','A02.1.16.002'),
            ('cervical_6','A02.2.01.013'),('cervical_7','A02.2.01.013')}
    rows=json.loads((ROOT/'pins_neck/ta.json').read_text(encoding='utf-8'))
    for row in rows:
        if (row['bone'],row['code']) not in wanted: continue
        trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in bones[row['bone']]]
        for n,anchor in enumerate([row]+row.get('secondaryMarkers',[])):
            p=anchor['p']; world=Vector((p[0],-p[2],p[1]))
            measured.append(dict(id='neck_'+row['bone']+'_'+row['code'].replace('.','_'),secondary=n>0,
                nearestSurfaceMm=min(t.find_nearest(world)[3] for t in trees)*1000,
                reuseForChildAccepted=False,anatomicalAcceptance=False))
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=800;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_cavity=True
    scene.render.image_settings.file_format='PNG'
    cam=bpy.data.objects.new('batch2 camera',bpy.data.cameras.new('batch2 camera'));scene.collection.objects.link(cam);scene.camera=cam
    cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=20
    views=[('atlas','superior',(0,0,.2)),('atlas','inferior',(0,0,-.2)),
           ('axis','anterior',(0,-.2,.03)),('cervical_6','oblique',(-.16,-.16,.1)),
           ('cervical_7','oblique',(-.16,-.16,.1)),('hyoid','anterior',(0,-.2,.01)),('hyoid','posterior',(0,.2,.01))]
    for b,label,direction in views:
        for obj in scene.objects:
            if obj.type=='MESH':obj.hide_render=owner(obj)!=b;obj.color=(.65,.7,.75,1)
        center,size=bounds[b];cam.location=center+Vector(direction)
        cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
        target=OUT/f'batch2-{b}-{label}.png';assert not target.exists()
        scene.render.filepath=str(target)
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
        images.append(dict(bone=b,view=label,file=str(target.relative_to(ROOT))))
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in old_data['objects']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for kind in ('meshes','materials','images','cameras','worlds'):
        collection=getattr(bpy.data,kind)
        for item in list(collection):
            if item.as_pointer() not in old_data[kind] and item.users==0:collection.remove(item)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
assert {o.as_pointer() for o in bpy.data.objects}==old_data['objects']
result=dict(status='passed',source=str(source.relative_to(ROOT)),sourceSha256=digest,sourceUnchanged=True,originalScenePreserved=True,
    meshes=metrics,contextAnchors=measured,images=images,acceptedCoordinates=0,acceptedExtents=0)
with (OUT/'blender-neck-batch2.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',meshes=len(metrics),contextAnchors=len(measured),images=len(images),acceptedCoordinates=0)))

"""Run through Blender MCP with OUT set to an allocated evidence-run directory.

Read-only import, distances for all anchors, diagnostic views. No anatomical
acceptance is inferred from a nearest triangle or a rendering.
"""
from pathlib import Path
import hashlib, io, json, tempfile
from contextlib import redirect_stdout
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
rows=json.loads((ROOT/'pins_neck/ta.json').read_text(encoding='utf-8'))
source=ROOT/'build_neck/neck_hi.glb'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Neck read-only stage5');bpy.context.window.scene=scene
records=[];metrics=[];images=[]

def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent

try:
    with tempfile.TemporaryDirectory(prefix='atlas-neck-stage5-') as td:
        copy=Path(td)/'neck.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH':bones.setdefault(b,[]).append(obj)
    assert set(bones)=={'atlas','axis','hyoid',*[f'cervical_{n}' for n in range(3,8)]}
    trees={b:[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
            [tuple(p.vertices) for p in o.data.polygons]) for o in objects] for b,objects in bones.items()}
    bounds={}
    for b,objects in bones.items():
        coords=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
        lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
        hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
        bounds[b]=((lo+hi)/2,max(hi-lo)*1.4)
        metrics.append(dict(bone=b,meshes=len(objects),vertices=sum(len(o.data.vertices) for o in objects),
            triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),
            dimensionsMm=[v*1000 for v in hi-lo],matrixDeterminants=[o.matrix_world.determinant() for o in objects]))
    for row in rows:
        for i,p in enumerate([row]+row.get('secondaryMarkers',[])):
            point=Vector((p['p'][0],-p['p'][2],p['p'][1]))
            distance=min(tree.find_nearest(point)[3] for tree in trees[row['bone']])*1000
            records.append(dict(id='neck_'+row['bone']+'_'+row['code'].replace('.','_'),secondary=i>0,
                p=p['p'],n=p.get('n'),bone=row['bone'],nearestSurfaceMm=distance,
                coordinateX=p['p'][0],anatomicalAcceptance=False,fullExtentAccepted=False))
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=800;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('neck audit world');scene.world.color=(.8,.8,.8)
    scene.render.image_settings.file_format='PNG'
    cam=bpy.data.objects.new('neck audit camera',bpy.data.cameras.new('neck audit camera'));scene.collection.objects.link(cam);scene.camera=cam
    cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=20
    for bone in bones:
        center,size=bounds[bone]
        for label,direction in [('superior',Vector((0,0,.2))),('oblique',Vector((-.16,-.16,.10)))]:
            for obj in scene.objects:
                if obj.type=='MESH':obj.hide_render=owner(obj)!=bone;obj.color=(.65,.70,.75,1)
            dots=[];marked=[]
            for row in rows:
                if row['bone']!=bone:continue
                # Fewer glyphs so holes and facets remain visible; all anchors
                # are measured above, irrespective of the diagnostic view.
                if row['code'] not in {'A02.2.02.003','A02.2.01.011','A02.2.01.015','A02.2.01.017','A02.2.02.103','A02.2.02.104','A02.1.16.002','A02.1.16.003','A02.1.16.004'}:continue
                for i,point in enumerate([row]+row.get('secondaryMarkers',[])):
                    p=point['p'];bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.0005,location=(p[0],-p[2],p[1]))
                    dot=bpy.context.object;dot.name='audit glyph';dot.color=(.95,.04,.03,1);dots.append(dot)
                    marked.append(dict(code=row['code'],secondary=i>0,p=p))
            cam.location=center+direction;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
            path=OUT/(bone+'-'+label+'.png');assert not path.exists()
            scene.render.filepath=str(path)
            with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
            images.append(dict(file=str(path.relative_to(ROOT)),bone=bone,view=label,markers=marked,glyphRadiusM=.0005))
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
report=dict(status='passed',tool='Blender MCP',source=str(source.relative_to(ROOT)),sourceSha256=digest,
    sourceUnchanged=True,originalScenePreserved=True,records=records,meshes=metrics,images=images,
    scope='Coordinate frame, surface proximity and diagnostic views only; anatomical identities and extents not accepted.')
with (OUT/'blender-neck.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',bones=len(metrics),anchors=len(records),images=len(images),maximumDistanceMm=max(r['nearestSurfaceMm'] for r in records))))

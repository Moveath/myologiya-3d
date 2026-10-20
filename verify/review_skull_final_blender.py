"""Read-only bridge audit of all skull anchors and three diagnostic views."""
from pathlib import Path
import bpy, json, hashlib, tempfile, io, sys
from contextlib import redirect_stdout
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-final-2026-10-17'
sys.path.insert(0,str(ROOT/'scripts'))
from head_localization import positions
source=ROOT/'build_head/head_hi.glb'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
kinds=('objects','meshes','materials','images','cameras','worlds')
before={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in kinds}
scene=bpy.data.scenes.new('Skull final read-only')
bpy.context.window.scene=scene
rows=[];meshes=[];images=[]
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
try:
    with tempfile.TemporaryDirectory(prefix='skull-final-') as td:
        copy=Path(td)/'head.glb';copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    bones={}
    for obj in scene.objects:
        b=owner(obj)
        if b and obj.type=='MESH':bones.setdefault(b,[]).append(obj)
    assert len(bones)==22
    trees={b:[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                    [tuple(p.vertices) for p in o.data.polygons]) for o in objs] for b,objs in bones.items()}
    for b,objs in bones.items():
        meshes.append(dict(bone=b,objects=[o.name for o in objs],vertices=sum(len(o.data.vertices) for o in objs),
            triangles=sum(len(p.vertices)-2 for o in objs for p in o.data.polygons),
            transforms=[list(v for row in o.matrix_world for v in row) for o in objs]))
    for (bone,code),r in positions().items():
        point=Vector((r['p'][0],-r['p'][2],r['p'][1]))
        distance=min(tree.find_nearest(point)[3] for tree in trees[bone])*1000
        rows.append(dict(id='head_'+bone+'_'+code.replace('.','_'),bone=bone,code=code,p=r['p'],
            sourceFile=r['source_file'],localization=r['localization'],surfaceDistanceMm=distance,
            anatomicalLocalizationAccepted=False,extentAccepted=False))
    assert len(rows)==521
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1100;scene.render.resolution_y=900
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_cavity=True
    camera=bpy.data.objects.new('audit camera',bpy.data.cameras.new('audit camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    camera.data.clip_start=.001;camera.data.clip_end=20
    views=[('maxilla-anterior',{'maxilla_right','maxilla_left'},Vector((0,-.2,.03))),
           ('mandible-lingual',{'mandible'},Vector((0,.20,.10))),
           ('lacrimal-isolated',{'lacrimal_right','lacrimal_left'},Vector((-.15,-.15,.05)))]
    for name,visible,direction in views:
        coords=[o.matrix_world@Vector(v) for b in visible for o in bones[b] for v in o.bound_box]
        lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
        hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)));center=(lo+hi)/2
        for obj in scene.objects:
            if obj.type=='MESH':obj.hide_render=owner(obj) not in visible;obj.color=(.68,.72,.77,1)
        camera.location=center+direction;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=max(hi-lo)*1.3
        scene.render.filepath=str(OUT/(name+'.png'))
        with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
        images.append({'file':str(Path(scene.render.filepath).relative_to(ROOT)),'bones':sorted(visible),
            'purpose':'Diagnostic view only; no new points, contours or segmentation.'})
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in before['objects']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for kind in kinds[1:]:
        items=getattr(bpy.data,kind)
        for item in list(items):
            if item.as_pointer() not in before[kind] and item.users==0:items.remove(item)
assert {o.as_pointer() for o in bpy.data.objects}==before['objects']
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
result=dict(status='passed',tool='Blender MCP',source=str(source.relative_to(ROOT)),sha256=digest,
    originalScenePreserved=True,sourceUnchanged=True,bones=meshes,records=rows,images=images,
    scope='All 22 bone meshes and 521 anchor provenance/distances, not 521 anatomical acceptances.')
(OUT/'blender-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','bones':len(bones),'anchors':len(rows),'images':len(images),
                 'maxDistanceMm':max(r['surfaceDistanceMm'] for r in rows)}))

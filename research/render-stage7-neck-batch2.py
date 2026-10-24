"""Blender MCP review of unchanged components and normal-repaired derivatives."""
import bpy, json, pathlib
from mathutils import Matrix, Vector
ROOT = pathlib.Path(r'C:/Users/Пользователь/Desktop/учеба/Миология 3D')
RUN = ROOT/'research/evidence-runs/stage7-muscle-batch2-2026-10-21T11-24-13-460Z-zNgJ41'
PREV = ROOT/'research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT'
old = bpy.context.window.scene
rows = json.loads((PREV/'context-arrays.json').read_text())
records = json.loads((RUN/'derivatives.json').read_text())
results = []
try:
    scene = bpy.data.scenes.new('Stage7 batch2 neck review'); bpy.context.window.scene = scene
    for row in rows:
        if row['file'] != 'neck' or not row['name'].startswith('b|'): continue
        mesh = bpy.data.meshes.new(row['name'])
        mesh.from_pydata(list(zip(*[iter(row['positions'])]*3)), [], list(zip(*[iter(row['indices'])]*3))); mesh.update()
        o = bpy.data.objects.new(row['name'],mesh); scene.collection.objects.link(o); o.color=(.55,.52,.43,1)
    groups = {}
    for rec in records:
        before = set(scene.objects); bpy.ops.import_scene.gltf(filepath=str(ROOT/rec['file']))
        objects = list(set(scene.objects)-before); groups[rec['id']] = objects
        for o in objects:
            if o.type != 'MESH': continue
            world = [o.matrix_world@v.co for v in o.data.vertices]; o.matrix_world.identity()
            for vertex,w in zip(o.data.vertices,world): vertex.co=(w.x,w.z,-w.y)
            o.color=(.1,.6,.8,1) if 'candidate' in rec['id'] else (.85,.3,.15,1)
            o.data.calc_loop_triangles()
            assert len(o.data.loop_triangles)==rec['triangles']
            results.append(dict(id=rec['id'],triangles=len(o.data.loop_triangles),vertices=len(o.data.vertices),
                                finiteNormals=all(all(abs(v)<2 for v in p.normal) for p in o.data.polygons)))
    scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    scene.world=bpy.data.worlds.new('Stage7 batch2 world'); scene.world.color=(.78,.78,.78)
    scene.display.shading.background_type='WORLD'
    scene.render.resolution_x=900; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
    camera=bpy.data.objects.new('Batch2 review camera',bpy.data.cameras.new('Batch2 review camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.17
    target=Vector((0,1.42,.045))
    for view,direction,group in [('posterior',(0,0,-1),'candidate'),('oblique',(1,0,-1),'candidate'),('normals',(1,0,1),'normals')]:
        for name,objects in groups.items():
            for o in objects: o.hide_render = (('candidate' in name) != (group=='candidate'))
        camera.location=target+Vector(direction).normalized()*.35
        forward=(target-camera.location).normalized(); right=forward.cross(Vector((0,1,0))).normalized(); up=right.cross(forward)
        camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
        targetfile=RUN/f'blender-neck-{view}.png';assert not targetfile.exists()
        scene.render.filepath=str(targetfile);bpy.ops.render.render(write_still=True)
    with (RUN/'blender-neck.json').open('x',encoding='utf8') as f:json.dump(results,f,indent=2)
finally:
    bpy.context.window.scene=old
print(json.dumps(results))

"""Addressed research scene only; original scene and files remain untouched.

Run via Blender MCP with RUN supplied as the allocated evidence directory.
"""
import bpy
import json
import pathlib
from mathutils import Vector, Matrix

ROOT = pathlib.Path(r'C:/Users/Пользователь/Desktop/учеба/Миология 3D')
run = pathlib.Path(globals().get('RUN', ROOT/'research/evidence-runs/stage7-interspinales-mirror-candidate-2026-10-22T07-10-51-528Z-2xay0X'))
rec = json.loads((run/'mirror-preparation.json').read_text())
context = json.loads((ROOT/rec['reusedContext']).read_text())
old = bpy.context.window.scene
result = dict(scope='Research only. '+rec['method']+' Not admitted. No original files modified.', models=[])
try:
    scene = bpy.data.scenes.new('Interspinales left reflection addressed review')
    bpy.context.window.scene = scene
    for row in context:
        if row['file'] != 'neck' or not row['name'].startswith('b|') or 'hyoid' in row['name']:
            continue
        mesh = bpy.data.meshes.new(row['name'])
        mesh.from_pydata(list(zip(*[iter(row['positions'])]*3)),[],list(zip(*[iter(row['indices'])]*3)))
        mesh.update()
        obj = bpy.data.objects.new(row['name'],mesh)
        scene.collection.objects.link(obj)
        obj.color = (.54,.51,.43,1)
    groups = {}
    for label,path,color in [('right',rec['sourceFile'],(.72,.17,.12,1)),('original-left',rec['originalLeftTestFile'],(.12,.60,.23,1)),('mirrored-left',rec['file'],(.05,.65,.92,1))]:
        before = set(scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT/path))
        objects = [o for o in set(scene.objects)-before if o.type=='MESH']
        assert len(objects)==1
        groups[label] = objects
        obj = objects[0]
        world = [obj.matrix_world@v.co for v in obj.data.vertices]
        obj.matrix_world.identity()
        for v,w in zip(obj.data.vertices,world):
            v.co = (w.x,w.z,-w.y)
        obj.data.update()
        obj.color = color
        obj.name = label+' diagnostic'
        obj.data.calc_loop_triangles()
        result['models'].append(dict(label=label,triangles=len(obj.data.loop_triangles),vertices=len(obj.data.vertices),bounds=[[min(v.co[k] for v in obj.data.vertices) for k in range(3)],[max(v.co[k] for v in obj.data.vertices) for k in range(3)]]))
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'OBJECT'
    scene.display.shading.show_cavity = True
    scene.world = bpy.data.worlds.new('Interspinales reflection review world')
    scene.world.color = (.76,.76,.76)
    scene.display.shading.background_type = 'WORLD'
    scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage = 960,1100,100
    camera = bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type='ORTHO'
    views = [('mirror-posterior','mirrored-left',(0,0,-1),(0,1.42,.045),.095),('mirror-oblique','mirrored-left',(1,0,-1),(0,1.42,.045),.095),('mirror-C2-detail','mirrored-left',(.7,.1,-1),(0,1.444,.05),.035),('original-left-posterior','original-left',(0,0,-1),(0,1.42,.045),.095)]
    for name,selected,direction,target,scale in views:
        for label,objects in groups.items():
            for obj in objects:
                obj.hide_render = label not in [selected,'right']
        target=Vector(target)
        camera.location=target+Vector(direction).normalized()*.3
        forward=(target-camera.location).normalized()
        right=forward.cross(Vector((0,1,0))).normalized()
        up=right.cross(forward)
        camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
        camera.data.ortho_scale=scale
        output=run/('blender-'+name+'.png')
        assert not output.exists()
        scene.render.filepath=str(output)
        bpy.ops.render.render(write_still=True)
    scene_file=run/'interspinales-mirror-review.blend'
    assert not scene_file.exists()
    bpy.data.libraries.write(str(scene_file),{scene},fake_user=True)
    with (run/'blender-review.json').open('x',encoding='utf8') as f:
        json.dump(result,f,indent=2)
finally:
    bpy.context.window.scene=old
print(json.dumps(result))

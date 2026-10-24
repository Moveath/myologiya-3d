"""Run with Blender MCP using runpy.run_path(..., init_globals={RUN, BUILD}).
Creates a separate scene, derivative GLB and three views; restores user scene.
"""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
run=ROOT/RUN; out=ROOT/BUILD
revision=globals().get('REVISION','v2')
spec=json.loads((out/'recipe.json').read_text(encoding='utf8'))
rows=json.loads((ROOT/spec['source_context']).read_text())
for name in [f'palmaris_brevis-{revision}.glb',f'review-{revision}.blend']:
    assert not (out/name).exists(), 'Refuse overwrite'
old=bpy.context.window.scene
def coord(v):return (v[0],-v[2],v[1])  # Three Y-up -> Blender Z-up, once.
def obj(name,positions,indices,color):
    mesh=bpy.data.meshes.new(name)
    verts=[coord(positions[i:i+3]) for i in range(0,len(positions),3)]
    faces=[indices[i:i+3] for i in range(0,len(indices),3)]
    mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.color=color
    return o
try:
    scene=bpy.data.scenes.new('Stage7 palmaris — TEST NOT ADMITTED')
    bpy.context.window.scene=scene;scene.unit_settings.system='METRIC'
    for row in rows:
        color=(.64,.60,.48,1) if row['type']=='b' else (.40,.20,.18,1)
        if row['type']=='o':color=(.28,.42,.30,1)
        obj(row['name'],row['positions'],row['indices'],color)
    model=obj('m|palmaris_brevis|',spec['positions'],spec['indices'],(.03,.7,.83,1))
    model['status']=spec['status'];model['notice']=spec['notice'];model['source']='recipe.json'
    material=bpy.data.materials.new('Palmaris — prototype only');material.diffuse_color=(.05,.62,.72,1)
    model.data.materials.append(material)
    for poly in model.data.polygons:poly.use_smooth=True
    bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
    target_glb=out/f'palmaris_brevis-{revision}.glb'
    bpy.ops.export_scene.gltf(filepath=str(target_glb),export_format='GLB',use_selection=True,use_active_scene=True,
        export_yup=True,export_normals=True,export_extras=True,export_animations=False)
    model.data.calc_loop_triangles()
    checks=dict(blender=bpy.app.version_string,scene=scene.name,vertices=len(model.data.vertices),
        triangles=len(model.data.loop_triangles),negativeDeterminant=model.matrix_world.determinant()<0,
        finiteNormals=all(all(math.isfinite(v) for v in p.normal) for p in model.data.polygons),
        file=str(target_glb.relative_to(ROOT)).replace('\\','/'),
        sha256=hashlib.sha256(target_glb.read_bytes()).hexdigest(),admitted=False)
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='OBJECT';scene.display.shading.show_cavity=True
    scene.display.shading.show_shadows=True;scene.display.shading.background_type='WORLD'
    scene.world=bpy.data.worlds.new('Palmaris review world');scene.world.color=(.075,.085,.09)
    scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    camera=bpy.data.objects.new('Palmaris review camera',bpy.data.cameras.new('Palmaris review camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    basis=Matrix(spec['frame']['basis_columns']);radial,distal,palmar=[basis.col[i] for i in range(3)]
    origin=Vector(spec['frame']['origin_m']);target=Vector(coord(origin+distal*.025+palmar*.006))
    for name,direction,scale in [('palmar',palmar,.12),('ulnar',palmar*.55-radial,.12),('detail',palmar,.055)]:
        camera.data.ortho_scale=scale;camera.location=target+Vector(coord(direction)).normalized()*.3
        forward=(target-camera.location).normalized();up=Vector(coord(-distal))
        right=forward.cross(up).normalized();up=right.cross(forward)
        camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
        image=run/('blender-palmaris-'+revision+'-'+name+'.png');assert not image.exists()
        scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
    # Save just the research scene and its dependencies, not the user's project.
    bpy.data.libraries.write(str(out/f'review-{revision}.blend'),{scene},fake_user=True)
    with (run/f'blender-prototype-{revision}.json').open('x',encoding='utf8') as f:json.dump(checks,f,indent=2)
finally:
    bpy.context.window.scene=old
print(json.dumps(checks))

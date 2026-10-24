"""Render the prepared diagnostic scene through Blender MCP, preserving sources."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
run=Path(RUN);scene=bpy.data.scenes['Omohyoid_Diagnostic_NotAdmitted'];old=bpy.context.window.scene
try:
    bpy.context.window.scene=scene
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
    scene.world=bpy.data.worlds.new('Omohyoid review');scene.world.color=(.06,.07,.08)
    scene.display.shading.background_type='WORLD'
    scene.render.resolution_x=1000;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    camera=bpy.data.objects.new('Omohyoid review camera',bpy.data.cameras.new('Omohyoid review camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.29
    muscles=[o for o in scene.objects if o.type=='MESH' and 'omohyoid' in o.name]
    points=[o.matrix_world@v.co for o in muscles for v in o.data.vertices]
    target=Vector([(min(p[i]for p in points)+max(p[i]for p in points))/2 for i in range(3)])
    for name,direction,show_scm in [('anterior',Vector((0,-1,0)),False),('oblique-with-scm',Vector((1,-2,.3)).normalized(),True)]:
        for o in scene.objects:
            if 'sternocleidomastoid' in o.name:o.hide_render=not show_scm
        camera.location=target+direction*.6;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        path=run/('blender-omohyoid-'+name+'.png');assert not path.exists()
        scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    mesh_counts={}
    for o in scene.objects:
        if o.type=='MESH':
            o.data.calc_loop_triangles();mesh_counts[o.name]=len(o.data.loop_triangles)
            assert all(math.isfinite(c)for p in o.data.polygons for c in p.normal)
    file=run/'omohyoid-annotation-workspace.blend';assert not file.exists()
    bpy.data.libraries.write(str(file),{scene},fake_user=True)
    result=dict(status='passed',blender=bpy.app.version_string,meshTriangles=mesh_counts,
        meshes=len(mesh_counts),diagnosticContours=2,anatomicalMasks=0,views=2,originalsModified=False,
        limitation='Contours mark geometric narrowing only. No tendon/part boundary assigned.')
    with (run/'blender-review.json').open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
finally:bpy.context.window.scene=old
print(json.dumps(result))

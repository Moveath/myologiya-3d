"""Execute through Blender MCP. Inspect imported copies in a temporary scene."""
import bpy
import json
import pathlib
from mathutils import Vector

root=pathlib.Path(r"C:\Users\Пользователь\Desktop\учеба\Миология 3D")
run=root/"research/evidence-runs/stage6-source-recovery-2026-10-20T04-55-12-346Z-sIUkha"
prior=bpy.context.window.scene
prior_objects=[o.name for o in prior.objects]
scene=bpy.data.scenes.new("stage6_source_inspection")
created=[]
rows=[]
try:
    bpy.context.window.scene=scene
    for fma in ("FMA23464","FMA23465","FMA23467","FMA23468"):
        before=set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=str(root/"research/cache/stage6-sources"/(fma+".obj")),
                              forward_axis="Y",up_axis="Z")
        objects=list(set(bpy.data.objects)-before)
        created.extend(objects)
        for obj in objects:
            if obj.type!="MESH":
                continue
            mesh=obj.data
            mesh.calc_loop_triangles()
            points=[obj.matrix_world@v.co for v in mesh.vertices]
            bounds=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
            rows.append(dict(id=fma,object=obj.name,vertices=len(mesh.vertices),triangles=len(mesh.loop_triangles),
                             bounds=bounds,scale=list(obj.scale),matrix=[list(r) for r in obj.matrix_world],
                             zeroAreaFaces=sum(p.area<=1e-12 for p in mesh.polygons)))
    for obj in created:
        obj.color=(0.3,0.55,0.8,1) if obj.name in ('FMA23464','FMA23467') else (0.95,0.6,0.2,1)
    camera_data=bpy.data.cameras.new('stage6_camera')
    camera=bpy.data.objects.new('stage6_camera',camera_data)
    scene.collection.objects.link(camera)
    created.append(camera)
    camera.location=(0,-1000,940)
    camera.rotation_euler=(Vector((0,-80,940))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO'
    camera_data.ortho_scale=660
    camera_data.clip_end=3000
    scene.camera=camera
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1320
    scene.render.resolution_y=640
    scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='OBJECT'
    scene.display.shading.background_type='WORLD'
    scene.display.shading.show_shadows=True
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(run/'forearm-source-view.png')
    bpy.ops.render.render(write_still=True)

finally:
    bpy.context.window.scene=prior
    for obj in created:
        mesh=obj.data if obj.type=="MESH" else None
        bpy.data.objects.remove(obj,do_unlink=True)
        if mesh is not None and mesh.users==0:
            bpy.data.meshes.remove(mesh)
    bpy.data.scenes.remove(scene)
result=dict(status="passed",blender=bpy.app.version_string,rows=rows,
            previousScene=prior.name,previousObjects=prior_objects,
            sceneRestored=prior_objects==[o.name for o in prior.objects],originalFilesWritten=False,
            anatomyAccepted=False)
with (run/"blender-visual.json").open("x",encoding="utf8") as out:
    json.dump(result,out,indent=2)
print("Source view saved; scene restored: "+str(result["sceneRestored"]))

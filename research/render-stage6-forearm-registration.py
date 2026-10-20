"""Blender MCP: isolated visual registration controls; ROOT/RUN supplied by caller."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

root, run = Path(ROOT), Path(RUN)
prior = bpy.context.window.scene
objects, meshes, cameras = set(bpy.data.objects), set(bpy.data.meshes), set(bpy.data.cameras)
scene = bpy.data.scenes.new("forearm_registration_views")
views = []
try:
    bpy.context.window.scene = scene
    for fma, color in [
        ("FMA23465", (0.9, 0.55, 0.2, 1)), ("FMA23468", (0.25, 0.55, 0.9, 1)),
        ("FMA23131", (0.8, 0.8, 0.75, 1)), ("FMA24436", (0.3, 0.7, 0.4, 1)),
        ("FMA24438", (0.7, 0.4, 0.7, 1))]:
        old = set(scene.objects)
        bpy.ops.wm.obj_import(filepath=str(root / "research/cache/stage6-sources" / (fma + ".obj")),
                             forward_axis="Y", up_axis="Z")
        obj, = [o for o in scene.objects if o not in old and o.type == "MESH"]
        obj.color = color
    data = bpy.data.cameras.new("registration_camera")
    camera = bpy.data.objects.new("registration_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    data.type = "ORTHO"
    data.clip_end = 3000
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.image_settings.file_format = "PNG"
    for name, center, offset, scale in [
        ("whole-y", (238, -80, 945), (0, -700, 0), 330),
        ("elbow-y", (214, -63, 1050), (0, -700, 0), 85),
        ("elbow-x", (214, -63, 1050), (700, 0, 0), 85),
        ("wrist-y", (253, -104, 820), (0, -700, 0), 80)]:
        target = run / (name + ".png")
        if target.exists():
            raise FileExistsError(target)
        camera.location = Vector(center) + Vector(offset)
        camera.rotation_euler = (Vector(center)-camera.location).to_track_quat("-Z", "Y").to_euler()
        data.ortho_scale = scale
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        views.append(dict(file=target.name, centerMM=center, viewOffsetMM=offset, orthoMM=scale))
finally:
    bpy.context.window.scene = prior
    for obj in set(bpy.data.objects)-objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in set(bpy.data.meshes)-meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for camera in set(bpy.data.cameras)-cameras:
        if camera.users == 0:
            bpy.data.cameras.remove(camera)
    bpy.data.scenes.remove(scene)
with (run / "registration-views.json").open("x", encoding="utf8") as f:
    json.dump(dict(views=views, sceneRestored=set(bpy.data.objects)==objects,
                   sourcePoseUnchanged=True, clinicalAccuracyClaim=False), f, indent=2)
print(json.dumps(dict(views=len(views), restored=prior.name)))

"""Blender MCP: actual pilot GLBs and current atlas humerus; ROOT/RUN supplied."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

root, run = Path(ROOT), Path(RUN)
prior = bpy.context.window.scene
before = {kind: set(getattr(bpy.data, kind)) for kind in
          ("objects", "meshes", "cameras", "materials", "images")}
scene = bpy.data.scenes.new("forearm_joint_acceptance")
views, observed = [], {}


def bvec(three):
    x, y, z = three
    return Vector((x, -z, y))


try:
    bpy.context.window.scene = scene
    for name, color in [("radius_left", (.95, .52, .16, 1)),
                        ("ulna_left", (.22, .52, .95, 1))]:
        old = set(scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(root / "build_stage6/left_forearm_v1" / (name + ".glb")))
        obj, = [o for o in scene.objects if o not in old and o.type == "MESH"]
        obj.color = color
        observed[name] = obj
    arrays = json.loads((run / "current-mesh-arrays.json").read_text())["humerus_left"]
    data = bpy.data.meshes.new("current_humerus_mesh")
    data.from_pydata([bvec(v) for v in arrays["vertices"]], [], arrays["faces"])
    obj = bpy.data.objects.new("current_atlas_humerus_left", data)
    scene.collection.objects.link(obj)
    obj.color = (.75, .75, .72, 1)
    observed["humerus_left"] = obj
    camera_data = bpy.data.cameras.new("acceptance_camera")
    camera = bpy.data.objects.new("acceptance_camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"
    camera_data.clip_start, camera_data.clip_end = .001, 10
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.image_settings.file_format = "PNG"
    elbow, wrist = (.219, 1.047, .065), (.253, .830, .102)
    default_views = [
        ("proximal-anterior", elbow, (0, 0, 1), .100, None),
        ("proximal-posterior", elbow, (0, 0, -1), .100, None),
        ("proximal-lateral", elbow, (1, 0, 0), .100, None),
        ("proximal-medial", elbow, (-1, 0, 0), .100, None),
        ("radius-head-oblique", (.233, 1.037, .070), (0, 1, .7), .060, "radius_left"),
        ("ulna-notch-lateral", (.211, 1.047, .061), (1, 0, 0), .065, "ulna_left"),
        ("distal-anterior", wrist, (0, 0, 1), .075, None),
        ("distal-axial", wrist, (0, -1, 0), .075, None),
    ]
    for name, center, offset, scale, only in globals().get("VIEWS", default_views):
        target = run / (name + ".png")
        if target.exists():
            raise FileExistsError(target)
        for key, mesh in observed.items():
            mesh.hide_render = only is not None and key != only
        camera.location = bvec(center) + bvec(offset)
        camera.rotation_euler = (bvec(center)-camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.ortho_scale = scale
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        views.append(dict(file=target.name, cameraTargetThreeMeters=center,
                          offset=offset, orthoMeters=scale, isolated=only))
    geometry = {}
    for name, obj in observed.items():
        obj.data.calc_loop_triangles()
        geometry[name] = dict(triangles=len(obj.data.loop_triangles),
                             determinant=obj.matrix_world.determinant(),
                             objectScale=list(obj.scale))
finally:
    bpy.context.window.scene = prior
    for kind in ("objects", "meshes", "cameras", "materials", "images"):
        collection = getattr(bpy.data, kind)
        for item in set(collection) - before[kind]:
            if kind == "objects":
                collection.remove(item, do_unlink=True)
            elif item.users == 0:
                collection.remove(item)
    bpy.data.scenes.remove(scene)
with (run / globals().get("RESULT_NAME", "blender-joint-views.json")).open("x", encoding="utf8") as stream:
    json.dump(dict(views=views, geometry=geometry, originalScene=prior.name,
                   sceneRestored=set(bpy.data.objects) == before["objects"],
                   sourceModelsUnmodified=True, anatomicalAcceptance=False), stream, indent=2)
print(json.dumps(dict(views=len(views), sceneRestored=prior.name, geometry=geometry)))

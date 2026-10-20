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
    controls = ['radius_left','ulna_left','trapezium_left','trapezoid_left','capitate_left','hamate_left']
    targets = ['scaphoid_left','lunate_left','triquetrum_left','pisiform_left']
    colors = [(1,.55,.15,1),(.3,.65,1,1),(.4,.85,.45,1),(.9,.35,.7,1)]
    arrays=json.loads((run/'mesh-arrays.json').read_text())
    for name in targets+controls:
        a=arrays[name];v=a['vertices'];f=a['faces']
        data=bpy.data.meshes.new(name)
        data.from_pydata([bvec(v[i:i+3]) for i in range(0,len(v),3)],[],[f[i:i+3] for i in range(0,len(f),3)])
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
        obj.color=colors[targets.index(name)] if name in targets else (.65,.65,.62,1)
        observed[name]=obj
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
    import numpy as np
    verts=np.concatenate([np.array(arrays[k]['vertices']).reshape(-1,3) for k in targets])
    center=((verts.min(axis=0)+verts.max(axis=0))/2).tolist()
    default_views=[('carpal-palmar',center,(0,0,1),.085,None),('carpal-dorsal',center,(0,0,-1),.085,None),('carpal-ulnar',center,(-1,0,0),.085,None),('carpal-distal',center,(0,-1,0),.085,None)]
    for k in targets:
        v=np.array(arrays[k]['vertices']).reshape(-1,3);c=((v.min(axis=0)+v.max(axis=0))/2).tolist()
        default_views.append((k+'-shape',c,(.6,.5,1),float(np.max(np.ptp(v,axis=0))*1.6),k))
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
with (run / globals().get("RESULT_NAME", "blender-carpal-views.json")).open("x", encoding="utf8") as stream:
    json.dump(dict(views=views, geometry=geometry, originalScene=prior.name,
                   sceneRestored=set(bpy.data.objects) == before["objects"],
                   sourceModelsUnmodified=True, anatomicalAcceptance=False), stream, indent=2)
print(json.dumps(dict(views=len(views), sceneRestored=prior.name, geometry=geometry)))

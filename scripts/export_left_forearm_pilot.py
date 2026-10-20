"""Blender MCP entry: build NEW trial GLBs, preserve the user's scene and sources.

Execute with ROOT and RUN globals (absolute paths). Never run against old outputs.
"""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils.bvhtree import BVHTree

root, run = Path(ROOT), Path(RUN)
out = root / "build_stage6/left_forearm_v1"
out.mkdir(parents=True, exist_ok=True)
targets = {"radius_left": "FMA23465", "ulna_left": "FMA23468"}
for bone in targets:
    if (out / (bone + ".glb")).exists():
        raise FileExistsError("Refusing to overwrite a previous derivative")
original = bpy.context.window.scene
before_objects = set(bpy.data.objects)
before_meshes = set(bpy.data.meshes)
scene = bpy.data.scenes.new("stage6_forearm_trial")
rows = []
try:
    bpy.context.window.scene = scene
    for bone, fma in targets.items():
        source = root / "research/cache/stage6-sources" / (fma + ".obj")
        old = set(scene.objects)
        bpy.ops.wm.obj_import(filepath=str(source), forward_axis="Y", up_axis="Z")
        obj, = [o for o in scene.objects if o not in old and o.type == "MESH"]
        obj.name = "b|" + bone
        obj.data.name = obj.name
        mesh = obj.data
        mesh.calc_loop_triangles()
        faces = [tuple(t.vertices) for t in mesh.loop_triangles]
        vertices = [tuple(v.co) for v in mesh.vertices]
        tree = BVHTree.FromPolygons(vertices, faces, all_triangles=True, epsilon=0)
        overlaps = sorted({tuple(sorted(p)) for p in tree.overlap(tree) if p[0] != p[1]})
        nonadjacent = [p for p in overlaps if not set(faces[p[0]]) & set(faces[p[1]])]
        # OBJ in native millimetres / Blender Z-up; glTF exporter maps to Y-up.
        # Positive determinant: scale only, no reflection or registration offset.
        obj.scale = (0.001,) * 3
        obj["sourceId"] = fma
        obj["sourceRelease"] = "BodyParts3D 3.0 / 20110915 / obj_95"
        obj["license"] = "CC BY-SA 2.1 Japan"
        obj["geometryStatus"] = "trial; anatomical registration subject to acceptance"
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        target = out / (bone + ".glb")
        bpy.ops.export_scene.gltf(
            filepath=str(target), export_format="GLB", use_selection=True,
            use_active_scene=True, export_yup=True, export_apply=False,
            export_normals=True, export_materials="NONE", export_extras=True,
            export_copyright="BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan")
        rows.append(dict(id=bone, sourceId=fma, sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
                         derivative=target.relative_to(root).as_posix(),
                         derivativeSHA256=hashlib.sha256(target.read_bytes()).hexdigest(),
                         vertices=len(vertices), triangles=len(faces),
                         blenderNonadjacentOverlapCandidates=nonadjacent,
                         scale=list(obj.scale), determinant=obj.matrix_world.determinant(),
                         methods="BVHTree candidates are diagnostic, not exact intersection proof. No repair, decimation, reflection or pin edits."))
    # Export control scene for a separate visual comparison, not the application.
    for fma in ("FMA23131", "FMA24436", "FMA24438"):
        old = set(scene.objects)
        bpy.ops.wm.obj_import(filepath=str(root / "research/cache/stage6-sources" / (fma + ".obj")),
                             forward_axis="Y", up_axis="Z")
        obj, = [o for o in scene.objects if o not in old and o.type == "MESH"]
        obj.name = "reference|" + fma
        obj.scale = (0.001,) * 3
    control = out / "registration-reference.glb"
    if control.exists():
        raise FileExistsError(control)
    bpy.ops.export_scene.gltf(filepath=str(control), export_format="GLB",
                             use_active_scene=True, export_materials="NONE",
                             export_copyright="BodyParts3D © DBCLS, CC BY-SA 2.1 Japan")
finally:
    bpy.context.window.scene = original
    for obj in set(bpy.data.objects) - before_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in set(bpy.data.meshes) - before_meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    bpy.data.scenes.remove(scene)
result = dict(status="exported_for_testing", blender=bpy.app.version_string, rows=rows,
              sceneRestored=original.name, userObjectsUnchanged=set(bpy.data.objects) == before_objects)
with (run / "blender-export.json").open("x", encoding="utf8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(dict(status=result["status"], objects=len(rows), sceneRestored=result["sceneRestored"])))

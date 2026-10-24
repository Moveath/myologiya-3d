"""Blender MCP: export only prepared derivative arrays; preserve user's scene."""
import bpy
import hashlib
import json
import pathlib
from mathutils import Vector

root, run = pathlib.Path(ROOT), pathlib.Path(RUN)
config = json.loads((run/"batch.json").read_text(encoding="utf8"))
arrays = json.loads((run/"mesh-arrays.json").read_text())
output = root/config["output"]
output.mkdir(parents=True, exist_ok=True)
old_scene = bpy.context.window.scene
scene = bpy.data.scenes.new("MirrorEducationalReview")
created_meshes, created_objects, rows = [], [], []
try:
    bpy.context.window.scene = scene
    for bone in config["targets"]:
        target = output/(bone+".glb")
        if target.exists():raise FileExistsError(target)
        row=arrays[bone]
        v=[row["vertices"][i:i+3] for i in range(0,len(row["vertices"]),3)]
        # Three Y-up -> Blender Z-up, a proper rotation.
        v=[(x,-z,y) for x,y,z in v]
        f=[row["faces"][i:i+3] for i in range(0,len(row["faces"]),3)]
        mesh=bpy.data.meshes.new("mirror:"+bone);created_meshes.append(mesh)
        mesh.from_pydata(v,[],f);mesh.update()
        obj=bpy.data.objects.new("b|"+bone,mesh);created_objects.append(obj)
        scene.collection.objects.link(obj)
        for p in mesh.polygons:p.use_smooth=True
        obj["provenance"]="Mirrored educational reconstruction from "+config["targets"][bone]
        obj["sourceLicense"]="CC BY-SA 2.1 Japan"
        obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",use_selection=True,use_active_scene=True,
            export_apply=False,export_yup=True,export_extras=True,export_materials="NONE",
            export_texcoords=False,export_normals=True)
        rows.append(dict(id=bone,triangles=len(f),vertices=len(v),
            sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
        obj.select_set(False)
finally:
    bpy.context.window.scene=old_scene
    for obj in created_objects:bpy.data.objects.remove(obj,do_unlink=True)
    for mesh in created_meshes:
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    bpy.data.scenes.remove(scene)
with (run/"blender-export.json").open("x",encoding="utf8") as out:
    json.dump(dict(status="exported_pending_independent_check",rows=rows,restoredScene=old_scene.name,
                   noPinOrOriginalChanges=True),out,indent=2)
print(json.dumps(dict(status="passed",models=len(rows),triangles=sum(r["triangles"] for r in rows))))

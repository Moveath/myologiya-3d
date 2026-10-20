"""Blender MCP: inspect all arm mesh identities in a temporary scene."""
import base64, hashlib, io, json, tempfile
from contextlib import redirect_stdout
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
files=['site/arm-q-glb.txt','build_context_bones/arm_extra_hi.glb']
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Left forearm source inventory');bpy.context.window.scene=scene
rows=[]
try:
    for file in files:
        before={o.as_pointer() for o in scene.objects}
        with tempfile.TemporaryDirectory(prefix='atlas-left-forearm-') as td:
            raw=(ROOT/file).read_bytes(); copy=Path(td)/'copy.glb'
            copy.write_bytes(base64.b64decode(raw) if file.endswith('.txt') else raw)
            with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
        bpy.context.view_layer.update()
        for o in scene.objects:
            if o.type!='MESH' or o.as_pointer() in before:continue
            cur=o;ancestry=[]
            while cur:ancestry.append(cur.name);cur=cur.parent
            vertices=[o.matrix_world@v.co for v in o.data.vertices]
            rows.append(dict(file=file,name=o.name,ancestry=ancestry,vertices=len(vertices),
                triangles=sum(len(p.vertices)-2 for p in o.data.polygons),
                boundsThreeM=[[min((v.x,v.z,-v.y)[i] for v in vertices) for i in range(3)],
                              [max((v.x,v.z,-v.y)[i] for v in vertices) for i in range(3)]]))
finally:
    bpy.context.window.scene=old_scene
    for o in list(bpy.data.objects):
        if o.as_pointer() not in old_data['objects']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for k in ('meshes','materials','images','cameras','worlds'):
        for o in list(getattr(bpy.data,k)):
            if o.as_pointer() not in old_data[k] and not o.users:getattr(bpy.data,k).remove(o)
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes.items())
result=dict(meshes=rows,hashes=hashes,originalScenePreserved=bpy.context.scene==old_scene,
    anatomicalIdentityAccepted=False,coordinateAcceptance=False)
with (OUT/'blender-left-forearm.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(meshes=len(rows),scenePreserved=result['originalScenePreserved'],sourceHashesUnchanged=True)))

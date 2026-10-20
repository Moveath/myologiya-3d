"""Read-only semantic-boundary availability check, run by Blender MCP with OUT."""
import base64, hashlib, io, json, tempfile
from contextlib import redirect_stdout
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];OUT=Path(OUT).resolve()
assert OUT.is_relative_to(ROOT/'research/evidence-runs') and OUT.is_dir()
prior=ROOT/'research/evidence-runs/stage5-pelvis-2026-10-18T16-21-31-309Z-EguUlx'
before=json.loads((prior/'hashes-before.json').read_text(encoding='utf8'))
files=['site/leg-q-glb.txt','build_context_bones/leg_extra_hi.glb']
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
assert all(before[f]==h for f,h in hashes.items()),'Geometry changed: previous distance evidence cannot be reused'
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Lumbopelvic boundary availability');bpy.context.window.scene=scene
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
rows=[]
try:
    for f in files:
        with tempfile.TemporaryDirectory(prefix='atlas-boundary-read-') as td:
            raw=(ROOT/f).read_bytes();copy=Path(td)/'copy.glb'
            copy.write_bytes(base64.b64decode(raw) if f.endswith('.txt') else raw)
            with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    for obj in scene.objects:
        if obj.type!='MESH' or owner(obj) not in ('hip_bone','hip_bone_left','sacrum'):continue
        rows.append(dict(bone=owner(obj),name=obj.name,vertices=len(obj.data.vertices),
            polygons=len(obj.data.polygons),materials=[m.name for m in obj.data.materials],
            vertexGroups=[g.name for g in obj.vertex_groups],attributes=[a.name for a in obj.data.attributes],
            customPropertyKeys=list(obj.keys()),meshPropertyKeys=list(obj.data.keys()),
            anatomicalBoundaryAccepted=False))
finally:
    bpy.context.window.scene=old_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in old_data['objects']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for k in ('meshes','materials','images','cameras','worlds'):
        for d in list(getattr(bpy.data,k)):
            if d.as_pointer() not in old_data[k] and d.users==0:getattr(bpy.data,k).remove(d)
assert old_data['objects']=={o.as_pointer() for o in bpy.data.objects}
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes.items())
result=dict(method='Imported object metadata and stored masks, not new anatomical segmentation',models=rows,
    hashes=hashes,previousGeometryUnchanged=True,previousTrimesh='trimesh-pelvis-v2.json',
    originalScenePreserved=True,newMasks=0,newContours=0,newCoordinates=0,
    limitation='No labelled boundary can be inferred from a whole-bone mesh or nearest-surface distance.')
with (OUT/'blender-boundary-availability.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(meshes=len(rows),sourceHashesUnchanged=True,originalScenePreserved=True),ensure_ascii=False))

"""Addressed MCP inspection of masks and mesh owners; original scene restored."""
import base64,hashlib,io,json,tempfile
from contextlib import redirect_stdout
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];out=Path(OUT).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
source=ROOT/'site/arm-q-glb.txt';digest=hashlib.sha256(source.read_bytes()).hexdigest()
old_scene=bpy.context.scene
old_data={k:{o.as_pointer() for o in getattr(bpy.data,k)} for k in ('objects','meshes','materials','images','cameras','worlds')}
scene=bpy.data.scenes.new('Addressed hand mask review');bpy.context.window.scene=scene
def owner(o):
    while o:
        if o.name.startswith(('b|','o|')):return o.name.split('|')[1].split('.')[0]
        o=o.parent
try:
    with tempfile.TemporaryDirectory(prefix='atlas-hand-copy-') as td:
        copy=Path(td)/'copy.glb';copy.write_bytes(base64.b64decode(source.read_bytes()))
        with redirect_stdout(io.StringIO()):bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    wanted={'scaphoid','lunate','triquetrum','pisiform','trapezium','trapezoid','capitate','hamate','metacarpal_4'}
    rows=[];owners=sorted({owner(o) for o in scene.objects if o.type=='MESH' and owner(o)})
    for o in scene.objects:
        if o.type=='MESH' and owner(o) in wanted:
            rows.append(dict(bone=owner(o),mesh=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),
                groups=[g.name for g in o.vertex_groups],attributes=[a.name for a in o.data.attributes],
                materialNames=[m.name for m in o.data.materials if m],anatomicalMasksAccepted=False))
    assert {r['bone'] for r in rows}==wanted
    result=dict(status='passed',source=str(source.relative_to(ROOT)),sha256=digest,owners=owners,addressedMeshes=rows,
        namedLeftHandOwners=[b for b in owners if b.endswith('_left') and any(k in b for k in ('scaphoid','lunate','triquetr','pisiform','trapez','capitate','hamate','metacarpal','phalanx','sesamoid'))],
        acceptedCoordinates=0,acceptedContours=0,
        limits='No named anatomical masks for candidate facets/waist/neck. Whole-bone material/attribute does not establish a boundary. No new distances or shape claims.')
finally:
    bpy.context.window.scene=old_scene
    for o in list(bpy.data.objects):
        if o.as_pointer() not in old_data['objects']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(scene)
    for k in ('meshes','materials','images','cameras','worlds'):
        for d in list(getattr(bpy.data,k)):
            if d.as_pointer() not in old_data[k] and d.users==0:getattr(bpy.data,k).remove(d)
assert old_data['objects']=={o.as_pointer() for o in bpy.data.objects}
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
result.update(originalScenePreserved=True,originalSourceUnchanged=True)
with (out/'blender-targeted.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',addressedMeshes=len(rows),namedLeftHandOwners=result['namedLeftHandOwners'],originalScenePreserved=True,acceptedContours=0)))

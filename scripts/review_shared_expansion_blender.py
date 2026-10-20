"""Execute through Blender MCP. Disposable imports; no source/model writes."""
import base64, hashlib, io, json, tempfile
from contextlib import redirect_stdout
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'verify/shared-expansion-geometry.json'

def load_pins(name):
    raw=(ROOT/'site'/name).read_text(encoding='utf-8')
    body=raw.split('push(...',1)[1] if 'push(...' in raw else raw.split('.concat(',1)[1]
    return json.loads(body.rsplit(');',1)[0])

pins={p['id']:p for f in ['pins-head.js','pins-leg.js'] for p in load_pins(f)}
groups=[('leg-q-glb.txt',{'cal_sinus_tarsi':['calcaneus','talus']}),
        ('head-q-glb.txt',{'head_occipital_A02_1_04_006':['occipital','sphenoid'],
         **{f'head_maxilla_{s}_A02_1_12_012':[f'maxilla_{s}',f'zygomatic_{s}'] for s in ['right','left']}})]
original=bpy.context.scene
report=[]
for filename,candidates in groups:
    scene=bpy.data.scenes.new('Shared review '+filename)
    bpy.context.window.scene=scene
    src=ROOT/'site'/filename
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='atlas-shared-') as directory:
        copy=Path(directory)/'copy.glb';copy.write_bytes(base64.b64decode(src.read_bytes()))
        with redirect_stdout(io.StringIO()): bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    def owner(obj):
        while obj:
            if obj.name.startswith('b|'): return obj.name.split('|')[1].split('.')[0]
            obj=obj.parent
    bones={b for v in candidates.values() for b in v}
    trees={b:[] for b in bones}
    objects={b:[] for b in bones}
    for obj in scene.objects:
        b=owner(obj)
        if obj.type=='MESH' and b in bones:
            trees[b].append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons],all_triangles=True))
            objects[b].append(obj)
    for pid,related in candidates.items():
        pin=pins[pid];x,y,z=pin['p'];point=Vector((x,-z,y))
        distances={b: min(t.find_nearest(point)[3] for t in trees[b])*1000 for b in related}
        report.append(dict(id=pid,p=pin['p'],n=pin.get('n'),model='site/'+filename,sha256=digest,related=related,distanceMm=distances,
                           status='measured_not_anatomically_accepted'))
    assert hashlib.sha256(src.read_bytes()).hexdigest()==digest
bpy.context.window.scene=original
OUTPUT.write_text(json.dumps(dict(tool='Blender MCP',blender=bpy.app.version_string,transform='Three (x,y,z) -> Blender (x,-z,y)',sourceModelsUnchanged=True,points=report),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))

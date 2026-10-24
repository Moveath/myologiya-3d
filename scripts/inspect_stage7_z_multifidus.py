"""Read-only targeted Z-Anatomy inspection; no template scripts or source writes.

Run in an isolated Blender background process, with --disable-autoexec.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
SOURCE = ROOT / 'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
terms = ('multifid', 'subcost', 'intertransvers', 'rotatores', 'auricularis',
         'depressor supercili', 'transversus menti', 'sternalis', 'diaphragm',
         'nasalis', 'orbicularis oris', 'omohyoid')
inventory = []
arrays = []
for obj in bpy.data.objects:
    if any(term in obj.name.lower() for term in terms):
        row = {'name': obj.name, 'type': obj.type,
               'collections': [c.name for c in obj.users_collection]}
        if obj.type == 'MESH':
            row.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons),
                       matrix_world=[list(x) for x in obj.matrix_world],
                       modifiers=[{'name':m.name,'type':m.type} for m in obj.modifiers],
                       properties={k: str(v)[:1200] for k,v in obj.items()})
        inventory.append(row)
    if obj.type != 'MESH' or not (obj.name.startswith('Multifidus') or
        obj.name in [f'{kind}{n}' for kind in ['T','L','C'] for n in range(1,13)]):
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    arrays.append({'name': obj.name,
                   'vertices': [list(obj.matrix_world @ v.co) for v in mesh.vertices],
                   'faces': [list(t.vertices) for t in mesh.loop_triangles],
                   'materials': [m.name if m else None for m in mesh.materials]})

def write(name, value):
    with (RUN/name).open('x', encoding='utf8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)

write('z-target-inventory.json', {'source':str(SOURCE.relative_to(ROOT)),
    'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'blender':bpy.app.version_string,'objects':inventory,
    'text_names':[t.name for t in bpy.data.texts if any(x in t.name.lower() for x in terms)],
    'bone_name_candidates':[o.name for o in bpy.data.objects if o.type=='MESH' and
        any(t in o.name.lower() for t in ['thoracic vertebr','lumbar vertebr','cervical vertebr'])]})
write('z-multifidus-arrays.json', arrays)
print(json.dumps({'objects':len(inventory),'exports':[{k:v for k,v in r.items() if k not in ('vertices','faces')} |
    {'vertices':len(r['vertices']),'triangles':len(r['faces'])} for r in arrays]},ensure_ascii=False))

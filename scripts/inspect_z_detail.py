"""Export evaluated, author-supplied Z-Anatomy skull meshes for local review.

The existing six ethmoid Boolean modifiers are evaluated, not newly invented.
No BodyParts3D registration or old annotation transfer is performed. Run with
Python 3.13 and the local bpy runtime from the research cache; embedded scripts
are disabled. Exported meshes retain a separate coordinate frame.
"""
from pathlib import Path
import json
import sys
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/cache/bpy-runtime'))
import bpy

SOURCE = ROOT / 'research/cache/Z-Anatomy/Startup.blend'
OUT = ROOT / 'research/cache/z-detail'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)

SINGLE = {'frontal': 'Frontal bone', 'occipital': 'Occipital bone',
          'sphenoid': 'Sphenoid bone', 'ethmoid': 'Ethmoid bone',
          'vomer': 'Vomer', 'mandible': 'Mandible'}
PAIRED = {'parietal': 'Parietal bone', 'temporal': 'Temporal bone',
          'maxilla': 'Maxilla', 'zygomatic': 'Zygomatic bone',
          'palatine': 'Palatine bone', 'nasal': 'Nasal bone',
          'lacrimal': 'Lacrimal bone', 'inferior_concha': 'Inferior nasal concha bone'}
NAMES = {key: ('bone', value) for key, value in SINGLE.items()}
for key, name in PAIRED.items():
    for side, suffix in [('left', '.l'), ('right', '.r')]:
        NAMES[f'{key}_{side}'] = ('bone', name + suffix)
NAMES.update({'frontal_sinus': ('cavity', 'Sinus of frontal bone'),
              'sphenoidal_sinus': ('cavity', 'Sinus of sphenoid bone')})
for group in ('Anterior', 'Middle', 'Posterior'):
    for side, suffix in [('left', '.l'), ('right', '.r')]:
        NAMES[f'ethmoid_cells_{group.lower()}_{side}'] = (
            'cavity', group + ' cells of ethmoid bone' + suffix)

# Keep only the relevant source objects in the evaluation graph; the original
# .blend file is never saved or modified. Making existing modifiers visible is
# needed because this is a navigable atlas with hidden collections.
for col in bpy.data.collections:
    col.hide_viewport = False
def unexclude(layer):
    layer.exclude = False
    layer.hide_viewport = False
    for child in layer.children:
        unexclude(child)
unexclude(bpy.context.view_layer.layer_collection)
for obj in bpy.data.objects:
    if obj.name in {x[1] for x in NAMES.values()}:
        obj.hide_viewport = False
        obj.hide_set(False)
depsgraph = bpy.context.evaluated_depsgraph_get()
rows = []
for key, (kind, name) in NAMES.items():
    obj = bpy.data.objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    # Z-Anatomy's world positions are in metres: X unchanged, Y becomes -Z,
    # Z becomes Y in the atlas renderer. No translation or scale registration.
    vertices = []
    for vertex in mesh.vertices:
        x, y, z = evaluated.matrix_world @ vertex.co
        vertices.append([x, z, -y])
    # Paired left source objects use a reflected world transform. The vertex
    # transform changes handedness; preserve outward normals by reversing the
    # triangle winding as well. The [x,z,-y] axis conversion has determinant +1.
    world_determinant = evaluated.matrix_world.to_3x3().determinant()
    reflected = world_determinant < 0
    faces = [list(t.vertices)[::-1] if reflected else list(t.vertices)
             for t in mesh.loop_triangles]
    payload = {'vertices': vertices, 'faces': faces}
    filename = key + '.json'
    (OUT / filename).write_text(json.dumps(payload), encoding='utf-8')
    modifiers = []
    for m in obj.modifiers:
        row = {'name': m.name, 'type': m.type, 'enabled': m.show_viewport}
        if m.type == 'BOOLEAN':
            row.update(operation=m.operation, operand=m.object.name if m.object else None)
        modifiers.append(row)
    rows.append({'id': key, 'name': name, 'kind': kind, 'file': filename,
                 'raw_vertices': len(obj.data.vertices), 'vertices': len(vertices),
                 'triangles': len(faces), 'modifiers': modifiers,
                 'world_transform_determinant': world_determinant,
                 'reversed_winding_for_reflection': reflected})
    evaluated.to_mesh_clear()
report = {'source': 'https://github.com/Z-Anatomy/Models-of-human-anatomy',
          'license': 'CC BY-SA 4.0',
          'source_blend_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'export_method': 'evaluated_get / to_mesh; existing modifiers only',
          'coordinate_transform': '[x,y,z] -> [x,z,-y], metres; not registered to BodyParts3D',
          'excluded_assets': ['Inner ear', 'Kidney', 'Nerves', 'All non-skull structures'],
          'meshes': rows}
(OUT / 'meshes.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps([{'id': r['id'], 'raw': r['raw_vertices'], 'evaluated': r['vertices'],
                   'modifiers': r['modifiers']} for r in rows]))

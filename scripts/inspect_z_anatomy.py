"""Extract openly licensed Z-Anatomy skull geometry for comparative review.

Run with bpy available. No embedded Blender scripts are executed. This is a
research export, not an automatic replacement or registration of atlas models.
"""
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'research/cache/bpy-runtime'))
import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/cache/Z-Anatomy/Startup.blend'),
                         load_ui=False, use_scripts=False)
out = ROOT/'research/cache/z-skull'
out.mkdir(exist_ok=True)
names = ['Frontal bone','Parietal bone','Occipital bone','Temporal bone',
         'Sphenoid bone','Ethmoid bone','Vomer','Mandible','Maxilla',
         'Palatine bone','Nasal bone','Lacrimal bone','Zygomatic bone',
         'Inferior nasal concha bone','Sinus of frontal bone','Sinus of sphenoid bone',
         'Anterior cells of ethmoid bone','Middle cells of ethmoid bone',
         'Posterior cells of ethmoid bone']
labels = []
mesh_info = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if obj.name.endswith('.j') and len(obj.data.vertices) == 2:
        labels.append({'name':obj.name[:-2],
                       'points':[list(obj.matrix_world@v.co) for v in obj.data.vertices]})
    if obj.name not in names and obj.name.removesuffix('.l').removesuffix('.r') not in names:
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = [list(obj.matrix_world@v.co) for v in mesh.vertices]
    faces = [list(t.vertices) for t in mesh.loop_triangles]
    filename = obj.name.replace(' ','_')+'.json'
    (out/filename).write_text(json.dumps({'vertices':vertices,'faces':faces}),encoding='utf-8')
    mesh_info.append({'name':obj.name,'file':filename,'vertices':len(vertices),'triangles':len(faces)})
(out/'labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'meshes.json').write_text(json.dumps(mesh_info,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Exported {len(mesh_info)} skull/bone cavity meshes and {len(labels)} annotation lines for review.')

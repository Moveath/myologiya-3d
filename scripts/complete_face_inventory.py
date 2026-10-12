"""Inventory authored face structures in Z-Anatomy without executing scripts."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'research/cache/bpy-runtime'))
import bpy
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/cache/Z-Anatomy/Startup.blend'), load_ui=False, use_scripts=False)
terms = ('auricular', 'depressor supercili', 'transversus ment', 'nasalis', 'orbicularis', 'procerus')
rows=[]
for obj in bpy.data.objects:
    if any(t in obj.name.lower() for t in terms):
        rows.append({'name':obj.name,'type':obj.type,'vertices':len(obj.data.vertices) if obj.type=='MESH' else None,
                     'collections':[c.name for c in obj.users_collection]})
print('Bone determinants',json.dumps({obj.name:obj.matrix_world.to_3x3().determinant() for obj in bpy.data.objects if obj.name in ['Maxilla.l','Maxilla.r','Palatine bone.l','Palatine bone.r','Lacrimal bone.l','Lacrimal bone.r','Nasal bone.l','Nasal bone.r','Zygomatic bone.l','Zygomatic bone.r','Inferior nasal concha bone.l','Inferior nasal concha bone.r']}))
out=ROOT/'research/face-completion-source-inventory.json'
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))

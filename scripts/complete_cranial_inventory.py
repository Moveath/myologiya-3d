"""Inspect source object names and geometry, with embedded scripts disabled."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/cache/bpy-runtime'))
import bpy
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/cache/Z-Anatomy/Startup.blend'),load_ui=False,use_scripts=False)
rows=[]
for obj in bpy.data.objects:
 if obj.type!='MESH': continue
 if not any(term in obj.name.lower() for term in ['canal','foram','groove','sinus','frontal','ethmoid','sphenoid','occipital','parietal','clinoid','trochl','cribri','cribro','hamul','uncinat','infundibul','semilun','vaginal','lingula','concha']): continue
 rows.append({'name':obj.name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'collections':[c.name for c in obj.users_collection], 'modifiers':[{'name':m.name,'type':m.type,'operand':m.object.name if m.type=='BOOLEAN' and m.object else None} for m in obj.modifiers]})
out=ROOT/'build_head/complete_cranial/z-object-inventory.json'
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([r for r in rows if r['polygons'] and not r['name'].endswith('.j')]))

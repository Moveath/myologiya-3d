from pathlib import Path
import json,re,runpy,sys
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
import hand_stage5_review as hand, lower_proximal_stage5_review as lower, foot_stage5_review as foot, pelvis_stage5_review as pelvis
old=(root/'site/data-context-bones.js').read_text(encoding='utf8')
blocks=[json.JSONDecoder().raw_decode(old[m.end():])[0] for m in re.finditer(r'Object.entries\(',old)]
assert len(blocks)==4
for (module,attr),order in zip([(hand,'BONE_PATCHES'),(lower,'RIGHT_PATCHES'),(foot,'RIGHT_PATCHES'),(pelvis,'BONE_PATCHES')],blocks):
 value=getattr(module,attr); assert set(value)==set(order)
 setattr(module,attr,{key:value[key] for key in order})
runpy.run_path(str(root/'scripts/make_context_bone_data.py'),run_name='__main__')

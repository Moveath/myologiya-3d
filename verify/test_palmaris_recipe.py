"""Reproduce the saved mesh recipe and exercise a non-default parameter."""
from pathlib import Path
import importlib.util,json,shutil,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];run=ROOT/sys.argv[1]
s=importlib.util.spec_from_file_location('pb',ROOT/'scripts/prepare_palmaris_prototype.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
scratch=run/'recipe-tests-v1';scratch.mkdir(exist_ok=False)
results={}
for name,parameters in [('default',None),('thickness',{'thickness_mm':.7})]:
    r=scratch/name;r.mkdir();shutil.copyfile(run/'hand-context.json',r/'hand-context.json')
    m.prepare(r,r/'output',parameters)
    results[name]=json.loads((r/'output/recipe.json').read_text(encoding='utf8'))
old=json.loads((ROOT/'build_stage7/palmaris_brevis_v1/recipe.json').read_text(encoding='utf8'))
a,b=results['default'],results['thickness']
checks={
 'deterministic_vertices':bool(np.allclose(old['positions'],a['positions'],rtol=0,atol=1e-14)),
 'deterministic_faces':old['indices']==a['indices'],
 'same_source_hash':old['context_sha256']==a['context_sha256'],
 'parameter_changes_geometry':a['positions']!=b['positions'],
 'topology_preserved_across_thickness':a['indices']==b['indices'],
 'both_remain_unadmitted':all(r['status']=='technical_prototype_not_admitted' for r in [a,b]),
 'coordinate_frame_stable':a['frame']==b['frame']}
try:m.prepare(scratch/'default',scratch/'invalid',{'thickness_mm':-1})
except AssertionError:checks['reject_negative_thickness']=True
else:checks['reject_negative_thickness']=False
with (run/'recipe-tests.json').open('x',encoding='utf8') as f:json.dump({'status':'passed' if all(checks.values()) else 'failed','checks':checks},f,indent=2)
assert all(checks.values());print(json.dumps({'passed':len(checks)}))

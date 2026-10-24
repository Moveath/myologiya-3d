"""Adversarial checks of real annotations plus small topology fixtures, no anatomical admission."""
import copy
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
from region_mask_pipeline import (read_json, checked_json, compile_batch, validate_mask, select,
                                 admission, digest, exact_remap, write_new, local_path)
run = local_path(sys.argv[1]); checks = []
def ok(condition, name):
    assert condition, name
    checks.append(name)
def rejects(fn, name):
    try:
        fn()
    except (ValueError, KeyError, FileExistsError):
        checks.append(name); return
    raise AssertionError('Not rejected: ' + name)

config = read_json('scripts/skull_region_recipes.json'); reviews = read_json('scripts/skull_region_admissions.json')
cat = json.loads((run / 'catalogue.json').read_text())
result, metrics, guides = compile_batch(config, reviews, cat)
saved = json.loads((run / 'mask-candidates.json').read_text())
ok(result == saved, 'Deterministic rebuild equals saved candidates')
legacy = read_json('site/skull-region-masks.json')
ok([(r['id'], r['variants']) for r in result['regions']] == [(r['id'], r['variants']) for r in legacy['regions']], 'All 11 exact main/q selections preserved')
ok(sum(r['admission']['level']=='educational' for r in result['regions']) == 7, 'Seven existing limited projections; no new admission')
ok(sum(r['admission']['level']=='draft' for r in result['regions']) == 4, 'Four drafts still disabled')
ok(len(guides)==2 and all(g['status']=='review-only' for g in guides), 'Two technical boundary guides excluded from atlas')
ok(len(cat['noModel'])==20, '20 noModel unchanged')
single=copy.deepcopy(config); single['resources']=single['resources'][:1]
one,_,_=compile_batch(single,reviews,cat)
ok(all(len(r['variants'])==1 for r in one['regions']), 'Single-variant source supported without artificial fallback')
recipe=config['recipes'][0]; region=result['regions'][0]; review=reviews['decisions'][0]
ok(admission(recipe, region, None)['level']=='draft', 'No decision defaults to draft')
for field, value in [('explicitAdmission',False),('level','auto-approved'),('scope',''),('evidence',[]),('evidence',['research/nonexistent-proof.png']),('recipeHash','changed')]:
    changed=copy.deepcopy(review); changed[field]=value
    rejects(lambda:admission(recipe,region,changed), 'Reject invalid decision: '+field+' '+str(value))
changed=copy.deepcopy(recipe);changed['notice']=''
rr=copy.deepcopy(review);rr['recipeHash']=digest(changed)
rejects(lambda:admission(changed,region,rr),'Reject admission without warning')
changed=copy.deepcopy(recipe);changed['bone']='temporal_left'
rejects(lambda:admission(changed,region,review),'Changed owner invalidates decision')
rejects(lambda:checked_json(dict(path='scripts/skull_region_annotations.json',sha256='wrong')),'Changed raw annotation rejected')
rejects(lambda:local_path('../outside'),'Paths cannot escape project')
rejects(lambda:write_new(run/'mask-candidates.json',{}),'Historical evidence cannot be overwritten')

# Minimal real-index topology fixture exercises all supported recipe types cheaply.
row=dict(mesh='b|example',positions=[1,0,0, 2,0,0, 1,1,0, 2,1,0],indices=[0,1,2, 2,1,3],local=[1,0,0, 2,0,0, 1,1,0, 2,1,0])
surface=dict(side='left',selector={'kind':'indexed_surface'})
m=validate_mask(surface,row,[0,1],[])
ok(len(m['boundaryEdges'])==4,'Surface boundary extracted from edge incidence, not pin radius')
named=dict(selector=dict(kind='named_primitive',name='b|example',wholeOwner=True))
ok(select(named,row)==([0,1],[]),'Exact named whole primitive supported')
named['selector']['name']='wrong'
rejects(lambda:select(named,row),'Different named primitive rejected')
cycle=dict(side='left',selector={'kind':'edge_cycle'})
ok(validate_mask(cycle,row,[],[[0,1],[1,3],[3,2],[2,0]])['components']==1,'Closed source-edge cycle')
path=dict(side='left',selector={'kind':'edge_path'})
ok(validate_mask(path,row,[],[[0,1],[1,3]])['edges']==2,'Open source-edge path')
for faces, edges, label in [([0,0],[],'duplicate faces'),([-1],[],'invalid face'),([0.0],[],'noninteger face'),([0],[[0,1]],'mixed selection'),([],[[0,3]],'nonexistent source edge'),([],[[0,1],[1,0]],'duplicate edges'),([],[[0,0]],'zero edge')]:
    rejects(lambda:validate_mask(surface,row,faces,edges),label)
rejects(lambda:validate_mask(dict(side='right',selector={'kind':'indexed_surface'}),row,[0],[]),'Opposite side rejected')
rejects(lambda:validate_mask(cycle,row,[],[[0,1],[1,3]]),'Open chain cannot be a contour')
rejects(lambda:validate_mask(path,row,[],[[0,1],[1,2],[1,3]]),'Branched chain cannot be a path')
bad=copy.deepcopy(row);bad['positions'][3:6]=bad['positions'][0:3]
rejects(lambda:validate_mask(surface,bad,[0],[]),'Zero-area triangle rejected')
bad=copy.deepcopy(row);bad['indices'][0:3]=[2,1,0]
rejects(lambda:exact_remap(row,bad),'Reversed fallback winding rejected')
bad=copy.deepcopy(row);bad['positions'][0]+=0.000001
rejects(lambda:exact_remap(row,bad),'Approximate specimen transfer rejected')
name=sys.argv[2] if len(sys.argv)>2 else 'python-pipeline.json'
assert Path(name).name==name
write_new(run/name,dict(passed=len(checks),checks=checks,algorithm='source-mask-recipes-v1'))
print(json.dumps(dict(passed=len(checks))))

"""Prepare bounded Blender inspection of generated surfaces and technical edge guides."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from region_mask_pipeline import read_json, checked_json, write_new, local_path
run=local_path(sys.argv[1]);config=read_json('scripts/skull_region_recipes.json')
source=checked_json(config['resources'][0])
write_new(run/'head-glb-source.json', source)
regions=json.loads((run/'mask-candidates.json').read_text())['regions']
guides=json.loads((run/'technical-boundaries.json').read_text())
masks={}
for bone in ['occipital','temporal_right','temporal_left']:
    r=next(r for r in regions if r['bone']==bone);v=r['variants'][0]
    masks[bone]=dict(faces=v['faces'],edges=next((g['edges'] for g in guides if g['parent']==r['id']),v['edges']))
write_new(run/'review-masks.json',masks)
inventory=[dict(bone=r['bone'],namedMesh=r['mesh'],primitives=1,materials=r['materials'],vertices=len(r['local'])//3,triangles=len(r['indices'])//3,
                separateAnatomicalParts=False) for r in source['rows']]
write_new(run/'named-mesh-inventory.json',dict(rows=inventory,knownMasks=len(regions),newAnatomicalApprovals=0,
    limitation='Names identify whole bones; no named subparts in these five owners. A technical boundary is not an anatomical one.'))
print(json.dumps(dict(reviewBones=list(masks),technicalGuides=len(guides))))

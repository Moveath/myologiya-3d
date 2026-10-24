"""One-time migration of the 11 reviewed legacy annotations, not automatic admission.
Creates versioned source recipes and explicit limited-scope decisions without changing indices.
"""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from region_mask_pipeline import digest, write_new
read = lambda p: json.loads((ROOT / p).read_text(encoding='utf8'))
ref = lambda p: dict(path=p, sha256=hashlib.sha256((ROOT / p).read_bytes()).hexdigest())
manifest = read('site/skull-region-masks.json')
extra = read('scripts/skull_region_expansion_annotations.json')
report = 'research/stage6-skull-region-highlighting-2026-10-21.md'
expanded = 'research/stage6-skull-region-expansion-2026-10-21.md'
run = extra['sourceRun']
recipes = []; decisions = []
for region in manifest['regions']:
    require_keys = ('id', 'bone', 'pinIds', 'status', 'label', 'notice', 'source', 'license', 'licenseUrl', 'sourceUrl', 'report', 'view')
    recipe = {k: region[k] for k in require_keys}
    recipe['side'] = region.get('side') or ('left' if region['bone'].endswith('_left') else 'right' if region['bone'].endswith('_right') else None)
    is_surface = bool(region['variants'][0]['faces'])
    recipe['representation'] = 'surface' if is_surface else 'projection_contour'
    if region['id'] in [r['id'] for r in extra['regions']]:
        i = next(i for i, r in enumerate(extra['regions']) if r['id'] == region['id'])
        annotation = 'scripts/skull_region_expansion_annotations.json'
        pointer = ['regions', i, 'faces' if is_surface else 'edges']
        refs = extra['regions'][i]['refs']
    else:
        annotation = 'scripts/skull_region_annotations.json'
        pointer = ['annotations', region['bone'], 'faces' if is_surface else 'edges']
        refs = [dict(url='https://ifaa.unifr.ch/Public/EntryPage/HomePublic.html', scope='TA98; existing terminology, not a geometric boundary'),
                dict(url='https://www.anatomystandard.com/ossa-et-juncturae/cranium/' + ('os-occipitale.html' if region['bone'] == 'occipital' else 'os-temporale.html'), scope='Labelled views; previous review documented in ' + report),
                dict(report=report, scope='Independent Gray/Sobotta references, source access and limits retained in prior report')]
    recipe['refs'] = refs
    recipe['selector'] = dict(kind='indexed_surface' if is_surface else 'edge_cycle', annotation=ref(annotation), pointer=pointer)
    recipes.append(recipe)
    admitted = region['status'].startswith('reviewed_')
    decisions.append(dict(id=region['id'], recipeHash=digest(recipe), date='2026-10-21',
        reviewedBy='Codex; reconciliation of existing saved reviews, not independent anatomical certification',
        level='educational' if admitted else 'draft', explicitAdmission=admitted,
        scope='projection_of_lumen_only' if admitted else 'insufficient_boundary_evidence',
        reason=region['notice'], evidence=[region['report']] + region.get('evidence', [])))
write_new(ROOT / 'scripts/skull_region_recipes.json', dict(schema='source-mask-recipes-v1',
    resources=[ref(run + '/' + name) for name in ['head-glb-source.json', 'head-q-glb-source.json']], recipes=recipes))
write_new(ROOT / 'scripts/skull_region_admissions.json', dict(schema='explicit-mask-admissions-v1', decisions=decisions))
print('Migrated 11 existing annotations; 7 limited educational projections, 4 disabled drafts. No new anatomical admission.')

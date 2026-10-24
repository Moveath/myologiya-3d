"""Bounded new coarse attachment review, reusing saved geometry and contacts.

No ray scan, export, surface deformation, or production change. End caps are
diagnostic vertex summaries, not anatomical insertion masks.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
OUT = ROOT / sys.argv[1]
started = time.monotonic()
deadline = started + 55

def read(name):
    return json.loads((PRIOR / name).read_text(encoding='utf8'))

source = read('z-target-arrays-v2.json')
atlas = read('atlas-multifidus-context.json')
maps = read('z-multifidus-components-map.json')
fit = next(r for r in read('z-multifidus-registration.json') if r['kind'] == 'rigid')
M = np.array(fit['matrix_source_blender_to_atlas_three'])

def transformed(vertices):
    p = np.array(vertices)
    return (p @ M[:3, :3].T + M[:3, 3]) * 1000

bone_sets = {}
for label, rows in [('source', source), ('atlas', atlas)]:
    bones = []
    for row in rows:
        if label == 'source' and row['name'].startswith('Vertebra '):
            p = transformed(row['vertices'])
        elif label == 'atlas' and row['name'].startswith('b|'):
            p = np.array(row['vertices']) * 1000
        else:
            continue
        bones.append({'name': row['name'], 'p': p, 'tree': cKDTree(p)})
    bone_sets[label] = bones

def closest(p, bones):
    distances = []
    for b in bones:
        distance, index = b['tree'].query(p)
        v = b['p'][int(index)]
        lo, hi = b['p'].min(0), b['p'].max(0)
        distances.append({'bone': b['name'], 'distanceToVertexMM': float(distance),
            'vertexIndex': int(index), 'nearestVertexMM': v.tolist(),
            'relativeXYZInWholeBoneBounds': ((v-lo)/(hi-lo)).tolist()})
    return sorted(distances, key=lambda r: r['distanceToVertexMM'])[:3]

results = []
for side, suffix in [('right', 'r'), ('left', 'l')]:
    row = next(r for r in source if r['name'] == f'Multifidus thoracis muscle.{suffix}')
    component_map = next(r for r in maps if r['name'] == row['name'])
    points = transformed(row['vertices'])
    faces = np.array(row['faces'])
    records = []
    for component in component_map['components']:
        if time.monotonic() > deadline:
            raise TimeoutError('55 second diagnostic limit')
        ids = np.unique(faces[component['faceIds']])
        p = points[ids]
        lo, hi = p.min(0), p.max(0)
        # Same deterministic method on every authored connected component.
        # 5% quantile selects a cap for inspection, NOT an attachment definition.
        qlo, qhi = np.quantile(p[:, 1], [.05, .95])
        caudal = np.median(p[p[:, 1] <= qlo], axis=0)
        cranial = np.median(p[p[:, 1] >= qhi], axis=0)
        records.append({'component': component['id'], 'vertices': len(ids),
            'faces': len(component['faceIds']), 'heightMM': float(hi[1]-lo[1]),
            'boundsMM': [lo.tolist(), hi.tolist()],
            'cranialCapMM': cranial.tolist(), 'caudalCapMM': caudal.tolist(),
            'cranialMoreMedialMM': float(abs(caudal[0])-abs(cranial[0])),
            'ends': {key: {label: closest(value, bones) for label, bones in bone_sets.items()}
                for key, value in [('cranial', cranial), ('caudal', caudal)]}})
    prior_contacts = read(f'z-multifidus-contact-classification-{side}.json')
    contacts = []
    for contact in prior_contacts['boneLocations']:
        if contact['fit'] != 'rigid':
            continue
        p = np.array(contact['point']) * 1000
        contacts.append({**contact, 'pointMM': p.tolist(),
            'nearest': {label: closest(p, bones) for label, bones in bone_sets.items()}})
    results.append({'side': side, 'components': records, 'existingBoneContacts': contacts})

data = {'schemaVersion': 1, 'elapsedSeconds': time.monotonic()-started,
    'newMethod': 'Endpoint cap summaries of 21 existing connected components per side; nearest saved source/atlas vertebral vertices; interpretation of existing rigid-fit contact flags only.',
    'notPerformed': ['No new intersection scan', 'No new export', 'No repair', 'No anatomical surface segmentation'],
    'cautions': ['Nearest vertex is not nearest continuous surface.',
        'Whole-bone bounds and end-cap quantiles are diagnostics, not accepted attachment masks.',
        'Previously sampled contact flags do not prove absence of other contacts.'],
    'sides': results}
with (OUT / 'component-endpoint-review.json').open('x', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
for side in results:
    print(side['side'])
    for c in side['components']:
        a, b = c['ends']['caudal']['source'][0], c['ends']['cranial']['source'][0]
        print(c['component'], round(c['heightMM'],1), b['bone'], round(b['distanceToVertexMM'],1), '<-', a['bone'], round(a['distanceToVertexMM'],1), 'medial',round(c['cranialMoreMedialMM'],1))
print('elapsed', data['elapsedSeconds'])

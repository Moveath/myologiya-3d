"""Record the explicitly reviewed second batch (LOG-20261026-03); earlier admissions stay byte-identical.

Three kinds of educational admission, each tied to its own review evidence:
  bodyparts3d — 14 further BodyParts3D 3.0 heart parts (topography review);
  z-anatomy   — Z-Anatomy vessels and aortic valve cusps registered to the atlas (z-publish.json rule);
  face-mask   — face lists of published BodyParts3D meshes (heart chambers, pulmonary trunk, aortic parts).
Usage: python scripts/admit_cardiovascular_batch2.py BP3D_RUN Z_RUN
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bp3d_run, z_run = (Path(a).resolve() for a in sys.argv[1:3])
path = ROOT / 'scripts/cardiovascular_admissions.json'
admissions = json.loads(path.read_text(encoding='utf8'))
before = json.dumps(admissions, sort_keys=True)
rel = lambda p: p.relative_to(ROOT).as_posix()
added = {}

topography = json.loads((bp3d_run / 'batch2-topography.json').read_text(encoding='utf8'))
assert topography['passed'] == topography['total'] == 14
for row in topography['rows']:
    record = json.loads((ROOT / 'build_cardiovascular/bp3d-3.0-v1' / (row['id'] + '.json')).read_text(encoding='utf8'))
    entry = dict(status='educational_limited', kind='bodyparts3d', sha256=record['sha256'],
                 evidence=[rel(bp3d_run / 'batch2-topography.json'), rel(bp3d_run / (record['source']['fma'] + '-source.json'))],
                 basis='BP3D 3.0 source identity matched to the TA98 entity FMA identifier; unchanged axes/scale; topography against the heart wall, '
                       'parent vessels and valves (surface/wall/cavity rule); exact GLB triangle roundtrip.',
                 limitation='Показан исходный фрагмент BodyParts3D. Ход, ветвление и тип кровоснабжения на одном образце; границы и прикрепления не приняты.')
    if record['degenerate'] or record['duplicateFaces']:
        entry['technicalExceptions'] = dict(degenerateRetained=record['degenerate'], duplicateFacesRetained=record['duplicateFaces'],
                                            normalFallbackVertices=record['normalFallbackVertices'], decision='Source triangles retained.')
    added[row['id']] = entry

publish = json.loads((z_run / 'z-publish.json').read_text(encoding='utf8'))
z_evidence = [rel(z_run / name) for name in ('z-registration.json', 'z-vessel-review.json', 'z-publish.json')]
for card, row in publish['admitted'].items():
    target = ROOT / 'site' / row['file']
    assert hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256'], card
    limitation = ('Схематическая модель Z-Anatomy: ход и диаметр — по авторской кривой источника, перенесённой на кости атласа; '
                  'это не сегментация образца. Стыки с моделями BodyParts3D и соотношения с мышцами приблизительны.') if row['kind'] == 'vessel-curve' else \
                 ('Модель створок Z-Anatomy, совмещённая со стенкой сердца атласа. Форма створок и их соотношение с синусами аорты не приняты; не для морфометрии.')
    added[card] = dict(status='educational_limited', kind='z-anatomy', modelFile=row['file'], sha256=row['sha256'], evidence=z_evidence,
                       basis=f"Z-Anatomy object «{row['zObject']}», CC BY-SA 4.0; admission rule of z-publish.json (side, bone penetration, continuity).",
                       limitation=' '.join([limitation] + row['notes']))
mask_review = json.loads((z_run / 'z-mask-review.json').read_text(encoding='utf8'))
for card, mask in mask_review['masks'].items():
    target = ROOT / 'site' / mask['file']
    assert hashlib.sha256(target.read_bytes()).hexdigest() == mask['sha256'], card
    added[card] = dict(status='educational_limited', kind='face-mask', maskFile=mask['file'], sha256=mask['sha256'], segmentOf=mask['parent'],
                       parentSha256=mask['parentSha256'], evidence=[rel(z_run / 'z-registration.json'), rel(z_run / 'z-mask-review.json')],
                       basis=f"{mask['method']}; {mask['faceCount']} of {mask['parentFaces']} faces of {mask['parent']}.",
                       limitation=('Граница части приблизительна: грани у стыков с неоднозначной принадлежностью не включены. ' if mask['parent'] == 'cv_heart' else '') +
                                  ('Граница проведена по уровню нижнего края тела T12 атласа (аортальное отверстие диафрагмы); положение отверстия на образце не размечалось.'
                                   if 'aorta' in card else 'Ствол выделен по совмещённой модели Z-Anatomy до бифуркации; точная граница с ветвями не принята.'
                                   if card == 'cv_a_pulmonary_trunk' else 'Камера выделена по совмещённой разметке Z-Anatomy; перегородки отдельно не выделены.'))
assert not set(added) & set(admissions), sorted(set(added) & set(admissions))
admissions.update(added)
assert json.dumps({k: v for k, v in admissions.items() if k not in added}, sort_keys=True) == before
path.write_text(json.dumps(admissions, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(dict(added=len(added), byKind={k: sum(v['kind'] == k for v in added.values()) for k in ('bodyparts3d', 'z-anatomy', 'face-mask')},
                      total=len(admissions))))

"""Generate the complete skull TA98 catalogue with explicitly localized 3D markers.

The anatomical catalogue and geometric localization are separate validations.
Missing positions are never synthesized. Source edits belong in head_terms.py,
head_*_evidence.py and the reviewed input files read by head_localization.py,
not the generated site file.
"""
from pathlib import Path
import json
import math
from collections import Counter
from ta98 import T, BONE
from head_terms import BONES, BONE_CODES, DESCRIPTIONS, TERM_NOTES, BOOK_PAGES
from manifest_head import BONES as MODEL_BONES
from head_localization import positions as reviewed_positions, descriptions as reviewed_descriptions

ROOT = Path(__file__).resolve().parents[1]
positions = reviewed_positions()
feature_descriptions = {**DESCRIPTIONS, **reviewed_descriptions()}

# Attachments reuse the reviewed muscle-card facts. A single marker can only
# identify a representative point, not the complete area of an attachment.
ATTACHMENTS = {
    ('temporal','A02.1.06.065'):[('temporalis','o',None)],
    ('sphenoid','A02.1.05.027'):[('lateral_pterygoid','o','upper')],
    ('sphenoid','A02.1.05.043'):[('lateral_pterygoid','o','lower'),('medial_pterygoid','o',None)],
    ('palatine','A02.1.13.007'):[('medial_pterygoid','o',None)],
    ('maxilla','A02.1.12.016'):[('medial_pterygoid','o',None)],
    ('maxilla','A02.1.12.009'):[('levator_anguli_oris','o',None)],
    ('maxilla','A02.1.12.006'):[('levator_labii_superioris','o',None)],
    ('maxilla','A02.1.12.024'):[('levator_nasolabialis','o',None)],
    ('mandible','A02.1.15.026'):[('masseter','i',None)],
    ('mandible','A02.1.15.027'):[('medial_pterygoid','i',None)],
    ('mandible','A02.1.15.032'):[('temporalis','i',None)],
    ('mandible','A02.1.15.038'):[('lateral_pterygoid','i',None)],
}
records = []
for bone in MODEL_BONES:
    base = bone.removesuffix('_right').removesuffix('_left')
    side = 'left' if bone.endswith('_left') else 'right'
    for code in BONE[bone]:
        lat, ru, flag = T[code]
        info = feature_descriptions.get(code, {})
        if isinstance(info,str): info = {'x':info}
        rec = {'b':bone,'id':'head_'+bone+'_'+code.replace('.','_'), 't':'ta',
               'c':code,'ru':ru,'lat':lat.split(';')[0].strip(),
               'x':info.get('x', f'Образование из номенклатурного списка кости «{BONES[base]["ru"].lower()}». Подробное топографическое описание для этой карточки ещё не подготовлено.'),
               'm':[], 'g':BONES[base]['ru']}
        assert info.get('refs'), (code,'Missing reference record')
        rec['refs'] = info['refs']
        if info.get('note'): rec['x'] += ' ' + info['note']
        if flag == 'ta_parentheses': rec['taParen'] = 1
        if code in TERM_NOTES and TERM_NOTES[code] != info.get('note'):
            rec['x'] += ' ' + TERM_NOTES[code]
        position = positions.get((bone,code))
        if position:
            assert len(position['p']) == len(position['n']) == 3
            assert all(math.isfinite(v) for v in position['p']+position['n'])
            assert .8 < sum(v*v for v in position['n']) < 1.2
            rec.update(p=position['p'],n=position['n'],loc=position['localization'])
            rec['modelNote'] = position.get('modelNote') or 'Маркер на поверхности BodyParts3D показывает один участок образования. Он не обозначает всю его протяжённость; у отверстия маркер расположен на краю.'
            if position.get('refs'):
                existing = {r if isinstance(r, str) else r['url'] for r in rec['refs']}
                rec['refs'] = rec['refs'] + [r for r in position['refs'] if (r if isinstance(r, str) else r['url']) not in existing]
        else:
            rec['modelNote'] = 'Точное положение этого образования не подтверждено на исходной сетке BodyParts3D. Термин сохранён в полном списке TA98; 3D-точка не показана.'
        for muscle, role, part in ATTACHMENTS.get((base,code),[]):
            # On an unpaired bone the surface position determines the side.
            # An unlocalized catalogue entry refers to both sides.
            sides = [side] if bone.endswith(('_right','_left')) else (
                ['right' if position['p'][0] < 0 else 'left'] if position else ['right','left'])
            for attachment_side in sides:
                rec['m'].append([muscle+'_'+attachment_side,role]+([part] if part else []))
        if code == 'A02.1.05.043':
            rec['modelNote'] += ' Ссылки на мышцы относятся к пластинке в целом: латеральная крыловидная мышца начинается с её наружной стороны, медиальная — с внутренней. Один маркер не изображает обе области прикрепления.'
        records.append(rec)

for bone in MODEL_BONES:
    got = [r['c'] for r in records if r['b']==bone]
    assert Counter(got) == Counter(BONE[bone]), (bone,'TA98 coverage mismatch')
assert len({r['id'] for r in records})==len(records)
assert not(set(positions)-{(r['b'],r['c']) for r in records}), 'Position not in official per-bone list'
(ROOT/'site/pins-head.js').write_text('/* Generated by scripts/make_pins_head.py. */\nwindow.ATLAS.pins.push(...'+json.dumps(records,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
counts = {bone:{'terms':len(BONE[bone]),
                'markers':sum(r['b']==bone and 'p' in r for r in records),
                **{kind:sum(r['b']==bone and r.get('loc')==kind for r in records)
                   for kind in ('surface','projection','internal','variant')}} for bone in MODEL_BONES}
(ROOT/'verify/head-coverage.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(records),'TA98 entries;',sum('p' in r for r in records),'markers;',
      dict(Counter(r.get('loc','unlocated') for r in records)),len(MODEL_BONES),'bones checked')

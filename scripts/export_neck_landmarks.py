"""Reproduce reviewed neck picks using the local, orthographic review queue.

1) prepare_neck_landmark_review.py
2) Run tools/head-review.mjs with ATLAS_REVIEW_QUEUE=qneck,
   ATLAS_REVIEW_PORT=8775, and
   ATLAS_REVIEW_MODEL=../build_neck/landmark_review/bones.glb.
3) export_neck_landmarks.py queue; after the queue finishes, inspect the labelled
   PNG files; only then run export_neck_landmarks.py export.
The exported row confirms a selected surface patch, never a complete shape.
"""
from pathlib import Path
import hashlib
import json
import sys
from manifest_neck import BONES
from neck_landmark_selections import SELECTIONS
from neck_terms import description_for, BONE_CODES

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'qneck'
REVIEW = ROOT / 'build_neck/landmark_review'
MODE = sys.argv[1] if len(sys.argv)>1 else 'queue'
QUEUE.mkdir(exist_ok=True)
groups={}
for row in SELECTIONS:
    assert row['code'] in BONE_CODES[row['bone']], row
    groups.setdefault((row['bone'],row['view']),[]).append(row)

if MODE=='queue':
    for (bone, view), rows in groups.items():
        name=f'landmarks_{bone}_{view}'
        selections=[]
        for row in rows:
            selections.append(dict(code=row['code'],uv=row['uv'],secondary=False))
            for uv in row['other']:
                selections.append(dict(code=row['code'],uv=uv,secondary=True))
        code='(()=>{const s='+json.dumps(selections)+';const out=s.map(x=>({...x,...pick('+json.dumps(bone)+','+json.dumps(view)+',...x.uv)}));show('+json.dumps(bone)+','+json.dumps(view)+');pins(out.filter(x=>x.p).map(x=>({p:x.p,t:x.code+(x.secondary?" L":"")})));return out;})()'
        (QUEUE/f'{name}.job').write_text(code,encoding='utf8')
    print('Queued',len(groups),'labelled review views')
elif MODE=='export':
    rows=[]
    for row in SELECTIONS:
        bone,code,view=row['bone'],row['code'],row['view']
        name=f'landmarks_{bone}_{view}'
        result=json.loads((QUEUE/f'{name}.out').read_text(encoding='utf8'))
        picks=[p for p in result if p['code']==code]
        primary=next(p for p in picks if not p['secondary'])
        assert primary.get('p'), (bone,code,primary)
        fid=BONES[bone][0]
        is_rim='край' in row['meaning']
        note='Маркер обозначает выбранный участок: '+row['meaning']+'. '
        note+=('Точка стоит на костном крае, а не внутри просвета; форму и стенки всего отверстия она не подтверждает.' if is_rim else 'Он не задаёт полную границу или точные размеры образования.')
        if row['meaning'].startswith('прав'):
            note+=' Основная точка относится к правой стороне.'
        source=ROOT/f'stl_neck/{fid}.stl'
        evidence=dict(method='manual-visible-relief-review-and-orthographic-raycast',
                      view=view,uv=row['uv'],sourceFid=fid,
                      sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      source='scripts/neck_landmark_selections.py',
                      screenshot=f'build_neck/landmark_review/{name}.png',
                      review='Визуальный осмотр этой кости в нескольких ортографических ракурсах; выбор различимого участка с учётом описания источников. Луч записывает координату уже выбранного участка и сам по себе не подтверждает название.',
                      coordinateFrame='Three.js metres: [BP3D.x, BP3D.z, -BP3D.y] / 1000',
                      fullExtentVerified=False,independentExpertReview=False)
        record=dict(bone=bone,code=code,p=primary['p'],n=primary['n'],localization='surface',
                    modelNote=note,refs=description_for(bone,code)['refs'],evidence=evidence)
        secondary=[]
        for p in picks:
            if p['secondary']:
                assert p.get('p'),(bone,code,p)
                secondary.append(dict(side='left',p=p['p'],n=p['n'],view=view,uv=p['uv'],
                                      method='independent-screen-pick-on-the-same-bone; no reflection'))
        if secondary: record['secondaryMarkers']=secondary
        rows.append(record)
    (ROOT/'pins_neck').mkdir(exist_ok=True)
    (ROOT/'pins_neck/ta.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for bone,view in groups:
        name=f'landmarks_{bone}_{view}.png'
        (REVIEW/name).write_bytes((QUEUE/name).read_bytes())
    counts={b:sum(r['bone']==b for r in rows) for b in BONES}
    audit=dict(version=1,reviewed='2026-10-13',surfaceMarkers=len(rows),perBone=counts,
               secondaryMarkers=sum(len(r.get('secondaryMarkers',[])) for r in rows),
               confirmedFullGeometry=False,independentExpertReview=False,
               method='Separate multi-view visual inspection of 8 original BodyParts3D bone meshes; source screenshots and manual screen selections retained.',
               unlocalized=[dict(bone=b,code=c,reason='Нет принятой визуально проверенной координаты; запись сохраняется в каталоге без выдуманной точки.') for b, codes in BONE_CODES.items() for c in codes if not any(r['bone']==b and r['code']==c for r in rows)])
    (ROOT/'research/neck-landmark-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Exported',len(rows),'surface markers;',counts)
else:
    raise ValueError(MODE)

"""Reproduce and export manually reviewed thoracic surface picks.

Run prepare_thorax_landmark_review.py and tools/head-review.mjs with queue
qthorax, port 8775, model ../build_thorax/landmark_review/bones.glb.
Then this script queue, visually inspect the labelled PNGs, and finally export.
"""
from pathlib import Path
import hashlib
import json
import sys
from thorax_landmark_selections import SELECTIONS
from prepare_thorax_landmark_review import BONES, source_path

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'qthorax'
REVIEW=ROOT/'build_thorax/landmark_review'
MODE=sys.argv[1] if len(sys.argv)>1 else 'queue'
QUEUE.mkdir(exist_ok=True)
groups={}
for row in SELECTIONS:
    key=(row['bone'],json.dumps(row['view'],sort_keys=True))
    groups.setdefault(key,[]).append(row)

def name_for(bone,view):
    return 'landmarks_'+bone+'_'+(view if isinstance(view,str) else hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()[:8])

if MODE=='queue':
    for (bone,_), rows in groups.items():
        view=rows[0]['view'];name=name_for(bone,view)
        selections=[dict(code=r['code'],uv=r['uv']) for r in rows]
        code='(()=>{const s='+json.dumps(selections)+';const out=s.map(x=>({...x,...pick('+json.dumps(bone)+','+json.dumps(view)+',...x.uv)}));show('+json.dumps(bone)+','+json.dumps(view)+');pins(out.filter(x=>x.p).map(x=>({p:x.p,t:x.code})));return out;})()'
        (QUEUE/(name+'.job')).write_text(code,encoding='utf8')
    print('Queued',len(groups),'labelled views for',len(SELECTIONS),'points')
elif MODE=='export':
    from thorax_terms import BONE_CODES, description_for
    records=[]
    for row in SELECTIONS:
        bone,code,view=row['bone'],row['code'],row['view']
        assert code in BONE_CODES[bone],(bone,code)
        name=name_for(bone,view)
        output=json.loads((QUEUE/(name+'.out')).read_text(encoding='utf8'))
        point=next(r for r in output if r['code']==code)
        assert point.get('p'),(bone,code,point)
        isrim='край' in row['meaning']
        note='Маркер обозначает выбранный участок: '+row['meaning']+'. '
        note+=('Точка находится на видимом костном крае и не подтверждает все стенки и весь просвет отверстия.' if isrim else 'Он не задаёт полную границу, толщину или точные размеры образования.')
        if row['meaning'].startswith('прав'): note+=' Показана правая сторона.'
        hashes={fid:hashlib.sha256(source_path(fid).read_bytes()).hexdigest() for fid in BONES[bone]}
        evidence=dict(method='manual-visible-relief-review-and-orthographic-raycast',
                      view=view,uv=row['uv'],sourceFids=BONES[bone],sourceSha256=hashes,
                      source='scripts/thorax_landmark_selections.py',
                      screenshot=f'build_thorax/landmark_review/{name}.png',
                      review='Отдельный визуальный осмотр данной кости в нескольких ракурсах; сопоставление различимого участка с анатомическим описанием. Луч записывает координату уже выбранного участка и сам по себе не подтверждает название.',
                      coordinateFrame='Three.js metres: [BP3D.x, BP3D.z, -BP3D.y] / 1000',
                      fullExtentVerified=False,independentExpertReview=False)
        records.append(dict(bone=bone,code=code,p=point['p'],n=point['n'],localization='surface',
                            modelNote=note,refs=description_for(bone,code)['refs'],evidence=evidence))
        (REVIEW/(name+'.png')).write_bytes((QUEUE/(name+'.png')).read_bytes())
    assert len({(r['bone'],r['code']) for r in records})==len(records)
    (ROOT/'pins_thorax').mkdir(exist_ok=True)
    (ROOT/'pins_thorax/ta.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    counts={b:sum(r['bone']==b for r in records) for b in BONES}
    audit=dict(version=1,reviewed='2026-10-13',surfaceMarkers=len(records),perBone=counts,
               confirmedFullGeometry=False,independentExpertReview=False,
               method='Separate multi-view visual inspection of original BodyParts3D bone meshes; no mirrored coordinates or bounding-box-generated landmarks.',
               unlocalized=[dict(bone=b,code=c,reason='Нет принятой визуально проверенной координаты; термин остаётся в каталоге без выдуманной точки.') for b,codes in BONE_CODES.items() for c in codes if not any(r['bone']==b and r['code']==c for r in records)])
    (ROOT/'research/thorax-landmark-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Exported',len(records),'markers; unlocalized',len(audit['unlocalized']))
else: raise ValueError(MODE)

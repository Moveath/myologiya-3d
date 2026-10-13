"""Generate a complete textual origin/insertion register, without invented areas.

Run after make_head_data.py and make_pins_head.py. The markers are existing TA98
representative landmarks, not attachment outlines or independently segmented
entheses. General parent markers are never promoted to part-specific markers.
"""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from head_muscles import MUSCLE_TEMPLATES
from head_muscle_evidence import FIELDS
from manifest_head import MUSCLES

ROOT=Path(__file__).resolve().parents[1]
BP='https://dbarchive.biosciencedbc.jp/en/bodyparts3d/'

def side(key):
    return 'right' if key.endswith('_right') else 'left' if key.endswith('_left') else 'unpaired'

def load_pins():
    text=(ROOT/'site/pins-head.js').read_text(encoding='utf8')
    return json.loads(text.split('push(...',1)[1].rsplit(');',1)[0])

def generate():
    pins=load_pins()
    items=[]
    for base,m in MUSCLE_TEMPLATES.items():
        ids=[base] if base in ('orbicularis_oris','transversus_menti') else [base+'_right',base+'_left']
        for mid in ids:
            modeled_parts={p for _,p in MUSCLES.get(mid,[])}
            for part,p in [(None,m),*m.get('parts',{}).items()]:
                rec={'id':mid+(':'+part if part else ''),'muscleId':mid,'part':part,'kind':'part' if part else 'whole',
                     'ru':p['ru'],'lat':p['lat'],'ta98':p['code'],'side':side(mid),
                     'geometry':{'present':(part in modeled_parts if part else mid in MUSCLES),
                                 'source':'BodyParts3D 3.0' if mid in MUSCLES and (not part or part in modeled_parts) else None,
                                 'sourceUrl':BP if mid in MUSCLES and (not part or part in modeled_parts) else None,
                                 'sourceMeshes':[{'bodyPartsId':source_id,'part':source_part}
                                                 for source_id,source_part in MUSCLES.get(mid,[])
                                                 if part is None or part==source_part],
                                 'license':'CC BY-SA 2.1 Japan' if mid in MUSCLES and (not part or part in modeled_parts) else None,
                                 'independentAnatomicalShapeValidation':False},
                     'note':m.get('note',''),'partNote':p.get('x','') if part else '',
                     'completeAttachmentArea':False}
                for f,name in [('o','origin'),('i','insertion')]:
                    markers=[];parent_markers=[]
                    for pin in pins:
                        for link in pin.get('m',[]):
                            if link[:2] != [mid,f]:continue
                            linked_part=link[2] if len(link)>2 else None
                            marker={'id':pin['id'],'source':'BodyParts3D 3.0','sourceUrl':BP,
                                    'side':side(mid),'boneId':pin['b'],'ta98':pin['c'],
                                    'localization':pin['loc'],'status':'representative_point_only',
                                    'partial':True,'completeAttachmentArea':False,
                                    'linkedPart':linked_part,'modelNote':pin.get('modelNote','')}
                            if part is None or linked_part==part:
                                markers.append(marker)
                            elif linked_part is None:
                                # The parent point may help navigation but says nothing
                                # about how a specific part's fibres attach.
                                parent_markers.append(marker)
                    rec[name]={'text':p.get(f,m[f]),'scope':p['fieldScope'][f],
                               'status':p['fieldStatus'][f],'refs':deepcopy(p['fieldRefs'][f]),
                               'representativeMarkerIds':[v['id'] for v in markers],
                               'representativeMarkers':markers,'parentMuscleMarkers':parent_markers,
                               'completeAttachmentArea':False,
                               'geometryStatus':'representative_points_only' if markers else 'attachment_area_not_delimited'}
                items.append(rec)
    assert len({x['id'] for x in items})==78
    assert sum(x['kind']=='whole' for x in items)==52
    assert sum(x['kind']=='part' for x in items)==26
    for x in items:
        for f in ('origin','insertion'):
            assert x[f]['text'] and not x[f]['completeAttachmentArea']
            if x[f]['status']=='supported':
                assert len({r['independentSource'] for r in x[f]['refs']})>=2
    fields=[]
    for base,m in MUSCLE_TEMPLATES.items():
        for part,p in [(None,m),*m.get('parts',{}).items()]:
            for f in FIELDS:
                if part and f not in p:
                    assert p['fieldRefs'][f]==m['fieldRefs'][f]
                    assert p['fieldStatus'][f]==m['fieldStatus'][f]
                fields.append({'muscle':base,'part':part,'field':f,'text':p.get(f,m[f]),
                               'scope':p['fieldScope'][f],'status':p['fieldStatus'][f],
                               'refs':p['fieldRefs'][f]})
    counts={'wholeMuscleInstances':52,'partInstances':26,'attachmentFieldRecords':len(items)*2,
            'wholeMeshesPresent':sum(x['kind']=='whole' and x['geometry']['present'] for x in items),
            'partMeshesPresent':sum(x['kind']=='part' and x['geometry']['present'] for x in items),
            'partSpecificAttachmentFields':sum(x['kind']=='part' and x[f]['scope']=='specific' for x in items for f in ('origin','insertion')),
            'inheritedPartAttachmentFields':sum(x['kind']=='part' and x[f]['scope']=='whole_muscle' for x in items for f in ('origin','insertion')),
            'wholeMusclesWithRepresentativeMarkers':sum(x['kind']=='whole' and bool(x['origin']['representativeMarkers']+x['insertion']['representativeMarkers']) for x in items),
            'completeAttachmentAreas':0}
    payload={'schemaVersion':1,'generatedBy':'scripts/export_skull_muscle_attachments.py',
             'scope':'52 мимические и жевательные мышцы и 26 экземпляров их частей из текущего каталога головы.',
             'counts':counts,'completeAttachmentArea':False,
             'limitations':[
                 'Текстовые сведения не определяют измеренную границу прикрепления на 3D-модели.',
                 'Существующий маркер показывает один участок именованного костного образования. Он не является площадью начала или прикрепления мышцы.',
                 'Сведения с scope=whole_muscle относятся ко всей мышце; они не подтверждают отдельную часть.',
                 'Маркер всей мышцы в parentMuscleMarkers не считается проверенным маркером выбранной части.',
                 'Наличие исходной сетки и автоматические проверки не заменяют независимую анатомическую экспертизу формы и границ.',
             ],'items':items}
    (ROOT/'site/skull-muscle-attachments.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    review={'date':'2026-10-13','scope':'Проверка полей 27 шаблонов мышц и 14 типов частей; развёртка в 52 + 26 экземпляров.',
            'counts':counts,'templateFieldCounts':dict(Counter((r['scope']+':'+r['status']) for r in fields)),
            'sourceIndependence':'Группа independentSource объединяет одного автора/редакцию; несколько URL и языковые версии не считаются отдельными источниками. Ссылки подтверждают литературное описание, не независимую морфометрию опубликованных сеток.',
            'externalExpertReviewCompleted':False,'russianTerminologyHumanExpertReviewCompleted':False,
            'completeMuscleGeometryClaim':False,'completeAttachmentAreaClaim':False,
            'unconfirmedFields':[r for r in fields if r['status']=='unconfirmed'],
            'fields':fields,'attachmentRegistry':'site/skull-muscle-attachments.json',
            'geometrySourceFollowup':{
                'acceptedNewModels':0,
                'officialVisibleApeDownloads':'https://www.visibleapeproject.com/human-downloads',
                'checked':'2026-10-13: официальная страница Human Downloads вновь проверена; обе ссылки головы ведут на те же Sketchfab-модели. Альтернативного прямого файла автор здесь не предоставляет. Предыдущий 401 официального скачивания не обходился.',
                'remainingPerInstanceReport':'research/muscle-completion-review.json',
                'note':'19 отсутствующих поверхностей остаются конкретными входными данными, перечисленными в отчёте. Карточки и улучшенные ссылки их не заменяют.'}}
    (ROOT/'research/head-muscle-field-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(counts,ensure_ascii=False))

if __name__=='__main__':generate()

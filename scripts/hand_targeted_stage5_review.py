"""Addressed hand additions and a left catalogue, never reflected geometry."""
from copy import deepcopy
from hand_stage5_review import (CARPALS, METACARPALS, PHALANGES, SESAMOID_BONES,
    GRAY, SOB, NCBI, CARPAL, TA, ref as base_ref, extra, joint)

def ref(*args):
    result=base_ref(*args)
    result['checked']='2026-10-19'
    return result

REPORT = 'research/stage5-hand-targeted-report-2026-10-19.md'
TTU = ref('hand_ttu', 'Texas Tech — Bones of the Upper Limb',
    'https://anatomy.ttuhscep.edu/anatomytables/bones_upperlimb.html',
    'Phalanges: all three ranks have heads; only proximal/middle heads articulate with a next phalanx.', 'full_text')
TUFT = ref('hand_distal_head', 'Elsevier Complete Anatomy — Head of Distal Phalanx of Thumb',
    'https://www.elsevier.com/resources/anatomy/skeletal-system/appendicular-skeleton/head-of-distal-phalanx-of-thumb/18770',
    'Public description: non-articular head/tuft contains a palmar tuberosity. No licensed model obtained.', 'full_text')
CAP = ref('hand_capitate_32760605', 'Bain et al. (2020) — Capitate-shortening osteotomy',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC7395839/',
    'Anatomy / Osseous: head, neck, body, facet morphology; DOI10.1055/s-0040-1709669. Surgical dimensions not used.', 'full_text')
LUN = ref('hand_lunate_2380518', 'Viegas et al. (1990) — Medial (hamate) facet of the lunate',
    'https://pubmed.ncbi.nlm.nih.gov/2380518/', 'Abstract: types I/II; no frequency transferred to this specimen.', 'abstract')
VAR = ref('hand_variation_8515018', 'Viegas et al. (1993) — Wrist anatomy: incidence, distribution, and correlation of anatomic variations, tears, and arthrosis',
    'https://pubmed.ncbi.nlm.nih.gov/8515018/', 'EFetch abstract: fourth metacarpal facet of capitate is not universal; not independent of a review citing this study.', 'abstract')
LUN2 = ref('hand_lunate_16362229', 'Dharap et al. — The hamate facet of the lunate: a radiographic study in an Arab population from Bahrain',
    'https://pubmed.ncbi.nlm.nih.gov/16362229/', 'Abstract: independently observed types I/II; comment PMID17186313 noted, rates not used.', 'abstract')
SCAPH = ref('hand_scaphoid_waist', 'NCBI Bookshelf — Scaphoid Wrist Fracture',
    'https://www.ncbi.nlm.nih.gov/books/NBK536907/', 'Introduction: proximal/distal poles and intervening waist; indexed text, not a geometric boundary.', 'indexed_text')
FDS = ref('hand_fds_29020826', 'Nicholson et al. — Redefining Zone II: Anatomy of the Flexor Digitorum Superficialis Insertion',
    'https://journals.sagepub.com/doi/10.1177/1558944717735940',
    'Publisher abstract and EFetch metadata only; 2017 electronic / 2019 print. Full text unavailable; exact footprint not accepted.', 'abstract')
UAMS = ref('hand_fds_uams', 'UAMS — Muscles of the Upper Limb',
    'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-upper-limb/',
    'Flexor digitorum superficialis: shafts of middle phalanges 2–5; differs from Hand Bones overview.', 'full_text')

# The two opposed surfaces remain two own landmarks, never one shared surface.
FACETS = {
    'scaphoid': ['radius','lunate','capitate','trapezium','trapezoid'],
    'lunate': ['radius','scaphoid','capitate','triquetrum','hamate'],
    'triquetrum': ['lunate','hamate','articular_disc'],
    'trapezium': ['scaphoid','trapezoid','metacarpal_2'],
    'trapezoid': ['scaphoid','trapezium','capitate','metacarpal_2'],
    'capitate': ['scaphoid','lunate','trapezoid','hamate','metacarpal_2','metacarpal_3','metacarpal_4'],
    'hamate': ['lunate','triquetrum','capitate','metacarpal_4','metacarpal_5'],
}
NAMES = {
    'scaphoid':('Ладьевидная кость','os scaphoideum','ладьевидной костью'),
    'lunate':('Полулунная кость','os lunatum','полулунной костью'),
    'triquetrum':('Трёхгранная кость','os triquetrum','трёхгранной костью'),
    'pisiform':('Гороховидная кость','os pisiforme','гороховидной костью'),
    'trapezium':('Кость-трапеция','os trapezium','костью-трапецией'),
    'trapezoid':('Трапециевидная кость','os trapezoideum','трапециевидной костью'),
    'capitate':('Головчатая кость','os capitatum','головчатой костью'),
    'hamate':('Крючковидная кость','os hamatum','крючковидной костью'),
    'radius':('Лучевая кость','radius','лучевой костью'),
    'articular_disc':('Суставной диск','discus articularis','суставным диском'),
}
for i, roman in enumerate(('I','II','III','IV','V'),1):
    NAMES[f'metacarpal_{i}']=(roman+' пястная кость','os metacarpi '+roman,roman+' пястной костью')


def review(record):
    p = deepcopy(record)
    if p['id'] in {f'pd{i}_caput' for i in range(1,6)}:
        definition = ('Несуставной расширенный дистальный конец ногтевой фаланги (головка; tuft). '
            'Не несёт суставного блока для следующей фаланги. Ладонная бугристость — поверхность этой части, а не её синоним.')
        p.update(x=definition, anatomicalDefinition=definition, geometryKindReason=definition,
            nomenclatureReview='general_TA98_term_distal_nonarticular_head',
            refs=p['refs']+[TTU,TUFT], targetedHandReview=REPORT)
    if p['id'] in {f'pd{i}_tuberositas' for i in range(1,6)}:
        p.update(partOf=p['id'].replace('_tuberositas','_caput'), targetedHandReview=REPORT)
    if p['id'] in {f'pm{i}_basis' for i in range(2,6)}:
        # Do not recast a disputed attachment as an accepted site on another part.
        p['x'] = ('Основание средней фаланги. Дорсальное прикрепление разгибательного аппарата отличается '
            'от прикрепления поверхностного сгибателя к средней фаланге. Прежняя привязка FDS к карточке '
            'основания не подтверждает точное поле прикрепления; локализация требует проверки.')
        p.update(attachmentLocalizationStatus='requires_review', refs=p['refs']+[FDS,UAMS], targetedHandReview=REPORT)
    return p


def additional_records():
    for key,b,ru,definition,refs in [
        ('scaphoid_waist','scaphoid','Перешеек ладьевидной кости',
         'Промежуточная суженная часть между проксимальным и дистальным полюсами ладьевидной кости; не линия перелома и не фиксированная плоскость.',[SCAPH,CARPAL]),
        ('capitate_head','capitate','Головка головчатой кости',
         'Проксимальная округлая часть головчатой кости. Суставные поля для ладьевидной и полулунной костей не задают весь объём головки.',[GRAY,CAP]),
        ('capitate_neck','capitate','Шейка головчатой кости',
         'Суженная часть дистальнее головки, между головкой и телом головчатой кости. Фиксированная координата или плоскость границы не установлена.',[GRAY,CAP]),
    ]:
        yield extra(key,b,ru+' справа','volume',definition,refs,targetedHandReview=REPORT)
    for b,partners in FACETS.items():
        for partner in partners:
            pair=(b,partner)
            variant=pair in {('lunate','hamate'),('hamate','lunate'),('capitate','metacarpal_4')}
            refs=[GRAY,SOB,CARPAL]
            if partner.startswith('metacarpal_'):refs.append(NCBI)
            definition='Собственная суставная площадка для сочленения с '+NAMES[partner][2]+'. Противолежащая площадка принадлежит другому компоненту; её координаты и границы здесь не заданы.'
            fields=dict(articulatesWith=[] if partner=='articular_disc' else [partner],targetedHandReview=REPORT)
            if partner=='articular_disc':
                definition='Проксимальная суставная площадка трёхгранной кости для суставного диска. Диск не является локтевой костью; прямое костное сочленение с локтевой костью не добавляется.'
                fields['softTissueRequirements']=['суставной диск лучезапястного сустава']
            if variant:
                definition+=' Наличие у данного образца не установлено; площадка не обязательна у каждого человека.'
                fields.update(anatomicalVariant=True,specimenPresence='unverified')
                refs += [VAR,CAP] if b=='capitate' else [LUN,LUN2]
            yield extra(b+'_facet_'+partner,b,'Площадка для сочленения с '+NAMES[partner][2]+' справа','area',definition,refs,**fields)
    yield joint('midcarpal_joint','Среднезапястный сустав',
        ['scaphoid','lunate','triquetrum','trapezium','trapezoid','capitate','hamate'],
        'Сочленение между проксимальным и дистальным рядами запястья. Гороховидная кость относится к отдельному гороховидно-трёхгранному суставу.',[GRAY,SOB,NCBI])
    for i,bones in [(2,['trapezium','trapezoid','capitate','metacarpal_2']),
                     (3,['capitate','metacarpal_3']),(4,['hamate','metacarpal_4']),(5,['hamate','metacarpal_5'])]:
        p=joint(f'cmc{i}_joint',f'{i} запястно-пястный сустав',bones,
            'Сочленение основания пястной кости с соответствующими костями дистального ряда запястья; не межпястный промежуток.',[GRAY,SOB,NCBI])
        if i==4:
            p['relations'].append(dict(bone='capitate',role='adjacentContext',evidence='conditional_fourth_CMC'))
            p['x']+=' Участие головчатой кости вариабельно: она показана как контекст, её площадка на образце не принята.'
            p['refs'] += [VAR,CAP]
        yield p
    for i in range(2,5):
        yield joint(f'intermetacarpal_joint_{i}_{i+1}',f'Межпястный сустав {i}–{i+1}',[f'metacarpal_{i}',f'metacarpal_{i+1}'],
            'Сустав между боковыми площадками оснований соседних пястных костей. Не пространство между их телами; первая пястная кость в эту последовательность не включается.',[GRAY,SOB,NCBI])


LEFT_NOTE = ('Подтверждённой 3D-модели этой левой кости нет. Координаты, размеры и маски не назначены; '
             'правая геометрия не отражалась. Плечевая кость слева служит только для ориентации, не заменяет кисть.')
LEFT_BONES = {}
for b in CARPALS + METACARPALS + PHALANGES:
    if b in NAMES:
        ru,lat,_=NAMES[b]
        definition=('Одна из восьми костей левого запястья.' if b in CARPALS else 'Пястная кость левой кисти: основание, тело и головка; суставные площадки выделяются отдельно.')
    else:
        _,rank,num=b.split('_'); i=int(num); roman=('I','II','III','IV','V')[i-1]
        ru_rank,lat_rank={'prox':('Проксимальная','proximalis'),'mid':('Средняя','media'),'dist':('Дистальная','distalis')}[rank]
        ru=f'{ru_rank} фаланга {roman} пальца'; lat=f'phalanx {lat_rank} digiti {roman}'
        definition='Фаланга левой кисти. У I пальца две фаланги, у II–V три. Части и поверхности не являются самостоятельными костями.'
    LEFT_BONES[b+'_left']=dict(ru=ru+' слева',lat=lat,g='b_carpus' if b in CARPALS else 'b_meta' if b in METACARPALS else 'b_phal',
        sub='hand',sec='arm',side='left',noModel=True,contextTargets=['humerus_left'],x=definition,note=LEFT_NOTE,
        refs=deepcopy([GRAY,SOB,NCBI,base_ref('ta98_hand','FIPAT / IFAA — TA98',TA,'A02.4.08–10: hand bones; laterality is instance metadata.','official_list')]))
for b,card in SESAMOID_BONES.items():
    p=deepcopy(card);p.update(ru=p['ru'].replace('справа','слева'),en=p['en'].replace('right','left'),side='left',
        contextTargets=['humerus_left'],note=LEFT_NOTE)
    LEFT_BONES[b.replace('_right','_left')]=p


def left_records(right_records):
    """Only reviewed anatomical definitions; every geometric and muscle link discarded."""
    owners=set(CARPALS+METACARPALS+PHALANGES)
    rows=[p for p in right_records if (p['b'] in owners or p['id']=='extra_hand_radiocarpal_joint') and p['t'] in ('ta','additional')]
    ids={p['id']:'left_hand_'+p['id'] for p in rows}
    bones={b:b+'_left' for b in owners|{'radius','ulna'}}
    bones.update({b:b.replace('_right','_left') for b in SESAMOID_BONES})
    for record in rows:
        p=deepcopy(record)
        p.update(id=ids[p['id']],b=bones[p['b']],side='left',p=None,n=None,m=[],
            templateRecord=record['id'],modelNote=LEFT_NOTE,targetedHandReview=REPORT,
            geometryReview=dict(coordinateAcceptance=False,extentAcceptance=False,report=REPORT),
            geometryRequirements=dict(status='missing_model',neededEvidence=LEFT_NOTE))
        for key in ('ru','x','note','anatomicalDefinition','geometryKindReason'):
            if key in p:p[key]=p[key].replace('справа','слева')
        if not p['ru'].endswith('слева'):p['ru']+=' слева'
        for key in ('sh','catalogueBones','articulatesWith'):
            if key in p:p[key]=[bones[b] for b in p[key]]
        for r in p.get('relations',[]):r['bone']=bones[r['bone']]
        if p.get('partOf'):p['partOf']=ids[p['partOf']]
        if 'relatedLandmarks' in p:p['relatedLandmarks']=[ids[i] for i in p['relatedLandmarks'] if i in ids]
        if 'softTissueComponents' in p:
            p.pop('softTissueComponents');p['softTissueRequirements']=['левый удерживатель сгибателей; модель не подтверждена']
        p.pop('anchorStatus',None)
        yield p

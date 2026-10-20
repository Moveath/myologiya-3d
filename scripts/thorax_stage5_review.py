"""Stage 5, thoracic vertebral batch. No coordinates or geometry are authored."""
from copy import deepcopy
from thorax_terms import T, GRAY_T, neck

REPORT = 'research/stage5-thorax-report-2026-10-18.md'
# Explicit anatomical entities, not a name classifier. Ribs/sternum are the next batch.
DEFINITIONS = {
 'A02.2.01.002': ('volume', 'Тело — опорная костная часть, а не одна из её поверхностей.'),
 'A02.2.01.003': ('area', 'Верхняя и нижняя площадки тела обращены к дискам; нужны две отдельные площади.'),
 'A02.2.01.004': ('volume', 'Краевые зоны окостенения тела; их возрастные границы не устанавливаются по наружному силуэту.'),
 'A02.2.01.005': ('volume', 'Дуга включает ножки и пластинки и имеет толщину.'),
 'A02.2.01.006': ('volume', 'Ножки — парные костные мосты между телом и задними элементами дуги.'),
 'A02.2.01.007': ('volume', 'Пластинки — парные костные части задней дуги, а не только её наружная поверхность.'),
 'A02.2.01.009': ('space', 'Верхняя вырезка ножки — открытая выемка, участвующая в нижней границе межпозвоночного отверстия.'),
 'A02.2.01.010': ('space', 'Нижняя вырезка ножки участвует в верхней границе отверстия с нижележащим позвонком.'),
 'A02.2.01.011': ('space', 'Просвет внутри костного кольца; поверхностный маркер не описывает его сечение или объём.'),
 'A02.2.01.012': ('volume', 'Остистый отросток — костный выступ от основания до конца, не только верхушка.'),
 'A02.2.01.013': ('volume', 'Поперечные отростки — парные костные выступы; их площадки и бугорки рассматриваются отдельно.'),
 'A02.2.01.014': ('volume', 'Верхние суставные отростки — костные части, несущие площадки, но не весь сустав.'),
 'A02.2.01.015': ('area', 'Верхняя суставная поверхность — контактная площадь собственного отростка.'),
 'A02.2.01.016': ('volume', 'Нижние суставные отростки — костные части, а не соответствующие суставные щели.'),
 'A02.2.01.017': ('area', 'Нижняя суставная поверхность — собственная площадка для верхней площадки нижележащего позвонка.'),
 'A02.2.03.002': ('area', 'Суставная площадка для головки ребра; целая ямка или полуямка согласно уровню и варианту.'),
 'A02.2.03.003': ('area', 'Нижняя реберная площадка тела; наличие на T9 вариабельно.'),
 'A02.2.03.004': ('area', 'Площадка для бугорка ребра, а не весь поперечный отросток или сустав.'),
 'A02.2.03.005': ('volume', 'Возвышение бокового края верхней поверхности тела T1; размеры на образце не приняты.'),
}
PAIRED = {f'A02.2.01.{n:03}' for n in (6,7,9,10,13,14,15,16,17)} | {f'A02.2.03.{n:03}' for n in (2,3,4,5)}

def source(id, title, url, locator, group, **extra):
    return dict(id=id,title=title,url=url,locator=locator,authorGroup=group,checked='2026-10-18',kind='anatomical',**extra)

FORAMEN_REFS = [
 source('thorax_gray_foramen','Gray / Lewis (1918)',neck.GRAY_GENERAL['url'],'PDF p.25: adjacent vertebral notches form intervertebral foramina.','gray_lewis_1918'),
 source('thorax_gkasdaris_2016','Gkasdaris G, Tripsianis G, Kotopoulos K, Kapetanakis S (2016). Clinical anatomy and significance of the thoracic intervertebral foramen: A cadaveric study and review of the literature.',
        'https://pubmed.ncbi.nlm.nih.gov/27891032/','Abstract and PMC5111324 indexed Introduction / Fig.2: adjacent vertebral notches, bodies, disc and facet capsule contribute boundaries; no dimensions transferred.',
        'gkasdaris_2016',pmid='27891032',doi='10.4103/0974-8237.193266',access='abstract_and_indexed_full_text_excerpt'),
]
TRANSITION_REFS = [FORAMEN_REFS[0],source('thorax_neck_foramen','Kim KT, Kim YB (2010). Cervical Radiculopathy due to Cervical Degenerative Diseases: Anatomy, Diagnosis and Treatment',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3053539/','ANATOMY, Fig.1: subaxial cervical intervertebral foramen; no dimensions or treatment claims.',
 'kim_kim_2010',pmid='21430971',doi='10.3340/jkns.2010.48.6.473')]
T12_REFS = [source('thorax_gray_t12','Gray / Lewis (1918)',GRAY_T['url'],'PDF p.35, Twelfth Thoracic Vertebra: three elevations on each transverse process.','gray_lewis_1918'),
 source('thorax_elsevier_t12','Elsevier Complete Anatomy — Twelfth Thoracic Vertebra',
 'https://www.elsevier.com/resources/anatomy/skeletal-system/axial-skeleton/twelfth-thoracic-vertebra/17444',
 'Key Features & Anatomical Relations: superior, inferior and lateral tubercles; descriptive catalogue only.','elsevier_complete_anatomy')]

def requirement(record):
    kind=record['geometryKind']
    if record.get('concept')=='intervertebral-foramen':
        text='Нужны согласованные соседние кости, диск и разметка костных и мягкотканных границ просвета на том же образце; отдельно справа и слева. Координаты вырезок не являются центрами отверстия.'
    elif record.get('c')=='A02.2.01.004':
        text='Нужны возраст/стадия сращения и изображения или сегментация зон окостенения этого образца; наружная сетка взрослого тела не задаёт эпифиз.'
    else:
        text={'area':'Нужна анатомически принятая маска всей площадки на этой сетке.',
              'volume':'Нужно выделить костную часть и принять её границы на этой сетке.',
              'space':'Нужны принятые границы выемки или просвета; точка на его краю не задаёт всё пространство.'}[kind]
        if record.get('anatomicalMultiplicity') in ('paired','superior_inferior'):
            text+=' Каждую сторону или поверхность проверять независимо; один маркер не подтверждает обе.'
    record['geometryRequirements']=dict(status='unverified_extent',coordinateReuse=False,neededEvidence=text,source=REPORT)
    record['modelNote']+=' '+text
    return record

def review(record):
    if not record['b'].startswith('thoracic_'): return record
    kind,reason=DEFINITIONS[record['c']]
    record.update(geometryKind=kind,geometryKindReason=reason,
        geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
        anatomicalMultiplicity='paired' if record['c'] in PAIRED else ('superior_inferior' if record['c'] in ('A02.2.01.003','A02.2.01.004') else 'single'))
    if record['b']=='thoracic_12' and record['c']=='A02.2.01.013':
        record['relatedLandmarks']=[f'extra_thoracic_12_{part}_tubercle_{side}' for part in ('superior','inferior','lateral') for side in ('right','left')]
    return requirement(record)

def additional_records():
    for part,label in [('superior','Верхний'),('inferior','Нижний'),('lateral','Латеральный')]:
        for side,side_ru in [('right','справа'),('left','слева')]:
            parent='thorax_thoracic_12_A02_2_01_013'
            yield requirement(dict(id=f'extra_thoracic_12_{part}_tubercle_{side}',b='thoracic_12',t='additional',lat='',
                ru=f'{label} бугорок поперечного отростка T12 {side_ru}',side=side,m=[],g='Дополнительные образования',
                x='Одна из трёх описываемых костных возвышенностей в области поперечного отростка T12. Это часть позвонка, а не отдельная кость или реберная суставная площадка.',
                refs=deepcopy(T12_REFS),partOf=parent,relatedLandmarks=[parent],geometryKind='volume',educationAvailable=False,
                nomenclatureStatus='outside_own_TA98_list',geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
                modelNote='Описательное название; отдельный код и официальная латинская форма TA98 не присвоены. Наличие и точные границы на данном образце не приняты; координаты не созданы.'))

def shared_records():
    levels=[('cervical_7','thoracic_1','C7–T1','c7_t1')]+[(f'thoracic_{i}',f'thoracic_{i+1}',f'T{i}–T{i+1}',f't{i}_t{i+1}') for i in range(1,12)]
    for upper,lower,level,key in levels:
        refs=TRANSITION_REFS if upper=='cervical_7' else FORAMEN_REFS
        for side,label in [('right','справа'),('left','слева')]:
            yield requirement(dict(id=f'shared_thorax_intervertebral_{key}_{side}',b=lower if upper=='cervical_7' else upper,
                t='ta',c='A02.2.01.008',lat=T['A02.2.01.008'][0],ru=f'Межпозвоночное отверстие {level} {label}',
                side=side,level=level,concept='intervertebral-foramen',m=[],g='Общие образования грудного отдела',
                x='Пространство между соседними позвонками. Кости вносят вклад в границы; диск и капсула сустава также участвуют, поэтому это не отверстие одной кости и не самостоятельная кость.',
                relations=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in refs]) for b in (upper,lower)],
                relatedLandmarks=[('neck_' if upper=='cervical_7' else 'thorax_')+upper+'_A02_2_01_010','thorax_'+lower+'_A02_2_01_009'],
                refs=deepcopy(refs),catalogueBones=[],anchors=[],geometryKind='space',educationAvailable=False,
                geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
                modelNote='Подтверждён состав костных участников, а не полный контур отверстия. Точка и размеры не назначены.'))

"""Reviewed neck osteology. No coordinates, mirrored points or mesh changes."""
from copy import deepcopy
from neck_terms import GRAY_CERVICAL, GRAY_HYOID, GRAY_GENERAL, T

REPORT = 'research/stage5-neck-report-2026-10-17.md'

# Explicit definitions of the anatomical entities in neck_terms, not a lexical
# classifier. Extent/shape acceptance is independent of representation choice.
GENERAL = {
 2:('volume','Тело — костная опорная часть с толщиной, не одна из его поверхностей.'),
 3:('area','Межпозвоночная поверхность — контактная площадь тела; у C2 здесь только нижняя.'),
 4:('volume','Эпифиз — возрастная область окостенения по периферии тела, а не произвольная линия края.'),
 5:('volume','Дуга — костный комплекс ножек и пластинок, ограничивающий отверстие сзади.'),
 6:('volume','Ножка — короткий костный мост от тела к задним отделам дуги.'),
 7:('volume','Пластинка — костная часть задней дуги с толщиной; не только её наружная поверхность.'),
 9:('space','Верхняя вырезка — открытая выемка края ножки; не всё межпозвоночное отверстие.'),
 10:('space','Нижняя вырезка — открытая выемка; у C1 рассматривается на задней дуге.'),
 11:('space','Позвоночное отверстие — просвет внутри костного кольца; точка на краю не определяет просвет.'),
 12:('volume','Остистый отросток — костный выступ дуги, включая его основание и конец.'),
 13:('volume','Поперечный отросток — выступающая костная часть, а не точка на её конце.'),
 14:('volume','Верхний суставной отросток — костная часть; суставная площадка выделена отдельно.'),
 15:('area','Верхняя суставная поверхность — площадка сочленения; не весь сустав и не соседняя кость.'),
 16:('volume','Нижний суставной отросток — костная часть; суставная площадка выделена отдельно.'),
 17:('area','Нижняя суставная поверхность — площадка сочленения; её границы требуют разметки.'),
}
REGIONAL = {
 2:('volume','Крючок — костное возвышение верхнелатерального края тела C3–C7.'),
 3:('space','Поперечное отверстие — проход в поперечном отростке; маркер на ободке не является центром канала.'),
 4:('volume','Передний бугорок — костное возвышение поперечного отростка; выраженность на C7 вариабельна.'),
 5:('volume','Сонный бугорок — передний бугорок C6 под специальным названием, не дополнительная независимая структура.'),
 6:('volume','Задний бугорок — костный выступ задней части поперечного отростка.'),
 7:('line','Борозда задаёт ход вдоль верхней стороны поперечного отростка; ширина и дно требуют отдельной разметки.'),
 102:('volume','Латеральная масса — объёмная опорная часть между дугами C1.'),
 103:('area','Верхняя площадка латеральной массы сочленяется с затылочным мыщелком; принадлежит C1.'),
 104:('area','Нижняя площадка латеральной массы обращена к C2; принадлежит C1.'),
 105:('volume','Передняя дуга — костная часть кольца C1, а не линия его переднего края.'),
 106:('area','Ямка зуба — суставная площадка сзади передней дуги, не сквозное отверстие.'),
 107:('volume','Передний бугорок C1 — срединное возвышение передней дуги.'),
 108:('volume','Задняя дуга — костная часть кольца C1 с толщиной.'),
 109:('line','Борозда ведёт позвоночную артерию по верхней стороне задней дуги; её ход не равен одной точке.'),
 110:('space','Вариабельный проход над бороздой при костном мостике; наличие на данном образце не установлено.'),
 111:('volume','Задний бугорок C1 — срединное костное возвышение задней дуги.'),
 202:('volume','Зуб — костный отросток C2; его поверхности и верхушка имеют отдельные записи.'),
 203:('point','Верхушка обозначает верхний конец зуба; точность конкретного координатного маркера проверяется отдельно.'),
 204:('area','Передняя площадка зуба сочленяется с ямкой зуба C1; это собственная поверхность C2.'),
 205:('area','Задняя площадка зуба обращена к поперечной связке C1; не общая костная поверхность C1–C2.'),
}
HYOID = {
 2:('volume','Тело — средняя костная часть подъязычной кости, имеющая отдельные поверхности.'),
 3:('volume','Малый рог — небольшой костный выступ; правая и левая стороны не подтверждаются одной точкой.'),
 4:('volume','Большой рог — протяжённая костная часть; маркер на ней не задаёт весь объём.'),
}
KINDS = {**{f'A02.2.01.{n:03}':v for n,v in GENERAL.items()},
         **{f'A02.2.02.{n:03}':v for n,v in REGIONAL.items()},
         **{f'A02.1.16.{n:03}':v for n,v in HYOID.items()}}
PAIRED = {f'A02.2.01.{n:03}' for n in (6,7,9,10,13,14,15,16,17)} | {
 f'A02.2.02.{n:03}' for n in (2,3,4,5,6,7,102,103,104,109,110)} | {'A02.1.16.003','A02.1.16.004'}

def review(record):
    code, bone = record['c'], record['b']
    kind, reason = KINDS[code]
    record.update(geometryKind=kind, geometryKindReason=reason,
        geometryReview=dict(status='representation_reviewed',source=REPORT,
                            coordinateAcceptance=False,extentAcceptance=False))
    record['anatomicalMultiplicity'] = 'paired' if code in PAIRED else ('superior_inferior' if code=='A02.2.01.003' and bone!='axis' else 'single')
    if code in PAIRED:
        record['modelNote'] += ' Запись охватывает парное образование; одна точка не подтверждает обе стороны. Вторичные маркеры, если есть, проверяются независимо.'
    if bone=='cervical_6' and code in ('A02.2.02.004','A02.2.02.005'):
        record['concept']='c6-anterior-carotid-tubercle'
        other='A02.2.02.005' if code.endswith('.004') else 'A02.2.02.004'
        record['relatedLandmarks']=['neck_cervical_6_'+other.replace('.','_')]
        record['x'] += ' На C6 передний и сонный бугорок обозначают одно образование; два кода TA98 сохранены как терминологические представления, а не как две независимые структуры.'
    return record

def source(key,title,url,locator,group,**extra):
    return dict(id=key,title=title,url=url,locator=locator,authorGroup=group,
                checked='2026-10-17',kind='anatomical',**extra)

ATLAS_REFS = [
 source('neck_gray_atlas', 'Gray / Lewis (1918)', GRAY_CERVICAL['url'],
        'PDF p.29: medial tubercle below each superior facet for transverse atlantal ligament.', 'gray_lewis_1918'),
 source('neck_tubbs_2002', 'Tubbs RS, Wellons JC III, Banks J, Blount JP, Oakes WJ (2002). Quantitative anatomy of the transverse ligament tubercles.',
        'https://pubmed.ncbi.nlm.nih.gov/12408389/', 'Abstract: Object and Methods; medial atlantal tubercles and transverse ligament. No sample measurements transferred.',
        'tubbs_2002',pmid='12408389',doi='10.3171/spi.2002.97.3.0343',access='abstract_and_verified_efetch_metadata'),
]
HYOID_REFS = [
 source('neck_gray_hyoid','Gray / Lewis (1918)',GRAY_HYOID['url'],'PDF pp.148–149: Body, anterior and posterior surfaces.','gray_lewis_1918'),
 source('neck_elsevier_hyoid','Elsevier Complete Anatomy — Anterior Surface of Body of Hyoid Bone',
        'https://www.elsevier.com/resources/anatomy/skeletal-system/axial-skeleton/anterior-surface-of-body-of-hyoid-bone/22155',
        'Description: two body surfaces, anterior and posterior. No proprietary mesh or image copied.','elsevier_complete_anatomy'),
]
FORAMEN_REFS = [
 source('neck_kim_foramina','Kim KT, Kim YB (2010). Cervical Radiculopathy due to Cervical Degenerative Diseases: Anatomy, Diagnosis and Treatment',
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC3053539/',
        'ANATOMY: cervical foramen boundaries, Fig.1. Anatomical boundaries only; no treatment recommendation or patient dimensions.',
        'kim_kim_2010',pmid='21430971',doi='10.3340/jkns.2010.48.6.473',access='full_text'),
 source('neck_gray_foramina','Gray / Lewis (1918)',GRAY_GENERAL['url'],'PDF p.25: contiguous vertebral notches form paired intervertebral foramina.','gray_lewis_1918'),
 source('neck_wsu_foramina','Washington State University, Elson S. Floyd College of Medicine — Lab 28',
        'https://learning.medicine.wsu.edu/wp-content/uploads/sites/4/2023/12/PDF-Lab-28.pdf',
        'p.2, General Features of Cervical Vertebrae: intervertebral foramina when adjacent vertebrae articulate. Limited to this statement, not simplified C7/arterial claims.','wsu_anatomy'),
]

def additional_records():
    for side,label in [('right','справа'),('left','слева')]:
        yield dict(id='extra_atlas_transverse_ligament_tubercle_'+side,b='atlas',t='additional',lat='',
            ru='Медиальный бугорок латеральной массы атланта '+label,
            x='Бугорок на медиальной стороне латеральной массы для поперечной связки атланта; не передний и не задний срединный бугорок дуги.',
            side=side,m=[],g='Дополнительные образования',geometryKind='volume',refs=deepcopy(ATLAS_REFS),
            relatedLandmarks=['neck_atlas_A02_2_02_102'],partOf='neck_atlas_A02_2_02_102',
            educationAvailable=False,nomenclatureStatus='outside_own_TA98_list',
            geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
            modelNote='Положение на данной сетке не проверено; границы не размечены, отдельный маркер не создан. Это описательное название; отдельный код и официальная латинская форма TA98 не присвоены.')
    for key,label in [('anterior','Передняя'),('posterior','Задняя')]:
        yield dict(id='extra_hyoid_body_surface_'+key,b='hyoid',t='additional',lat='',ru=label+' поверхность тела подъязычной кости',
            x=label+' сторона тела подъязычной кости; требуется разметка площади, а не копирование координаты карточки всего тела.',
            m=[],g='Дополнительные образования',geometryKind='area',refs=deepcopy(HYOID_REFS),
            relatedLandmarks=['neck_hyoid_A02_1_16_002'],partOf='neck_hyoid_A02_1_16_002',
            educationAvailable=False,nomenclatureStatus='outside_own_TA98_list',
            geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
            modelNote='Положение на данной сетке не проверено; границы не размечены, координаты и поверхность не созданы. Отдельный код TA98 не присвоен.')

def shared_records():
    # Only the five fully in-scope subaxial levels. C1–C2 and C7–T1 require
    # separate review; a notch marker is never re-used as a foramen centre.
    for upper in range(2,7):
        bones=['axis' if upper==2 else f'cervical_{upper}',f'cervical_{upper+1}']
        for side,label in [('right','справа'),('left','слева')]:
            yield dict(id=f'shared_neck_intervertebral_c{upper}_c{upper+1}_{side}',
                b=bones[0],t='ta',c='A02.2.01.008',lat=T['A02.2.01.008'][0],
                ru=f'Межпозвоночное отверстие C{upper}–C{upper+1} {label}',side=side,
                concept='intervertebral-foramen',level=f'C{upper}–C{upper+1}',m=[],g='Общие образования шеи',
                x='Парное пространство между соседними позвонками. Указанные кости вносят вклад в костные границы; связь не означает, что вся стенка состоит только из костей. Полный контур, мягкотканные границы и размеры на этом образце не размечены.',
                relations=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in FORAMEN_REFS]) for b in bones],
                refs=deepcopy(FORAMEN_REFS),catalogueBones=[],anchors=[],geometryKind='space',educationAvailable=False,
                geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
                modelNote='Связь костей подтверждена. Точное положение на сетке не проверено; контур не размечен. Координаты не созданы и не перенесены с позвоночных вырезок.')

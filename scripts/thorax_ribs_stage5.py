"""Reviewed rib/sternal entities. No coordinate, normal or mesh is authored here."""
from copy import deepcopy
from thorax_terms import T, GRAY_R, GRAY_S, GRAY_W, AS_R, AS_S, AS_W, OPEN_CAGE, BUCHANAN, COSTAL_PATEL, COSTAL_RISK
from thorax_stage5_review import source

REPORT = 'research/stage5-thorax-batch2-report-2026-10-18.md'
ACADEMY = source('rib_crest_academy', 'Académie nationale de médecine — crête du corps de la côte (2015)',
    'https://www.academie-medecine.fr/le-dictionnaire/index.php?page=119&q=St',
    'Entry crête du corps de la côte: inferior body border / inferolateral lip. Does not establish level-specific extent on this specimen.', 'academie_medecine')
ELSEVIER = source('sternum_elsevier', 'Elsevier Complete Anatomy — Sternum',
    'https://www.elsevier.com/resources/anatomy/skeletal-system/axial-skeleton/sternum/16892',
    'Key Features, Variations and Surface Anatomy; no dimensions or population averages used.', 'elsevier_complete_anatomy')
MDCT = source('sternum_duraikannu_2016', 'Duraikannu C, Noronha OV, Sundarrajan P (2016). MDCT evaluation of sternal variations: Pictorial essay.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC4931775/', 'Sternal foramen; Variations of xiphoid process, Fig.18; examples are not this specimen.',
    'duraikannu_2016', pmid='27413263', doi='10.4103/0971-3026.184407', access='full_text')
INTERCOSTAL = source('intercostal_kumar_2013', 'Kumar N, Guru A, Patil J, Ravindra S, Badagabettu SN (2013). Additional circular intercostal space created by bifurcation of the left 3rd rib and its costal cartilage: a case report.',
    'https://pubmed.ncbi.nlm.nih.gov/23298541/', 'Abstract Introduction: eleven normal pairs between adjacent ribs. The additional case space is not modelled.',
    'kumar_2013', pmid='23298541', doi='10.1186/1752-1947-7-6', access='abstract')
PUBLISHER = source('thorax_elsevier_chapter', 'Elsevier publisher sample, Human Anatomy, Chapter 3: Thorax',
    'https://booksite.elsevier.com/samplechapters/9780443103735/9780443103735.pdf',
    'Printed pp.51–52, Fig.3.2: II and VII cartilage junctions; intercostal spaces. Bibliographic author/edition not inferred from filename.', 'elsevier_sample_chapter')

# Individual anatomical decisions; the generator applies them only to existing applicability rows.
RIB_KINDS = {
 2: ('volume', 'Костная головка целиком, а не только покрывающая её суставная площадка.'),
 3: ('area', 'Контактная поверхность головки; её число и разделение зависят от уровня и варианта.'),
 4: ('line', 'Межсуставной гребень разделяет площадки головки; требуется трассировка линии, а не её случайный центр.'),
 5: ('volume', 'Шейка — костный участок между головкой и телом, имеющий толщину.'),
 6: ('line', 'Гребень верхнего края шейки протяжён; он не является гребнем головки или тела.'),
 7: ('volume', 'Тело — протяжённая костная часть, включающая поверхности и края.'),
 8: ('volume', 'Бугорок включает суставную и несуставную части; одна площадка не представляет весь выступ.'),
 9: ('area', 'Собственная площадка бугорка ребра; не весь рёберно-поперечный сустав.'),
 10: ('area', 'Здесь каталог описывает область изгиба тела. Линия рельефа в этой области не заменяет весь изгиб.'),
 11: ('area', 'Борозда имеет дно, ширину и края; её поверхностная маска предпочтительнее единственной точки или оси.'),
 12: ('line', 'Линейное представление гребня тела обосновано определением костного края в Académie de médecine и описанием нижнего края у Gray. Точная трасса, выраженность и применимость к каждому образцу остаются непроверенными.'),
 15: ('volume', 'Лестничный бугорок — костный выступ I ребра между сосудистыми бороздами.'),
 16: ('area', 'Сосудистая борозда I ребра — участок поверхности, а не сам сосуд или его просвет.'),
 17: ('area', 'Венозная борозда I ребра — участок поверхности впереди лестничного бугорка.'),
 19: ('area', 'Бугристость II ребра представляет шероховатую область поверхности; точка не задаёт её площадь.'),
}
STERNUM_KINDS = {
 2: ('volume', 'Рукоятка — целая костная часть.'),
 3: ('area', 'Ключичная вырезка рассматривается как суставная площадка рукоятки; обе стороны требуют отдельных масок.'),
 4: ('space', 'Открытая срединная выемка верхнего края рукоятки, а не отверстие через кость.'),
 5: ('line', 'Поперечный перегиб у перехода рукоятки в тело; не вся суставная щель.'),
 6: ('volume', 'Тело грудины включает толщину и обе поверхности.'),
 7: ('volume', 'Мечевидный отросток — целая часть с вариабельной формой и окостенением.'),
 8: ('area', 'Набор контактных участков для рёберных хрящей; нужны отдельные уровни и стороны.'),
 9: ('volume', 'Добавочные надгрудинные косточки — вариант; объёмы не заявлены существующими в GLB.'),
}

def own(b, code):
    return 'thorax_'+b+'_'+code.replace('.', '_')

def sterm(n):
    return own('sternum', f'A02.3.03.{n:03}')

def protect(p):
    needed = {'volume':'Нужна принятая сегментация костной части на этом образце.',
              'area':'Нужна принятая маска всей поверхности на исходном меше.',
              'line':'Нужна анатомически проверенная трасса линии на исходном меше.',
              'space':'Нужны проверенные границы пространства, включая некостные участки.'}[p['geometryKind']]
    if p.get('anatomicalMultiplicity') not in (None, 'single'):
        needed += ' Каждый уровень и сторону проверять независимо; исходный маркер не подтверждает все компоненты.'
    if p.get('inc'):
        needed += ' Сначала подтвердить наличие варианта на этом образце.'
    p['geometryReview'] = dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False)
    p['geometryRequirements'] = dict(status='unverified_extent',coordinateReuse=False,neededEvidence=needed,source=REPORT)
    p['modelNote'] = p.get('modelNote','Координата и отдельная геометрия не назначены.')+' '+needed
    return p

def review(p):
    b,c=p['b'],p['c']; n=int(c.rsplit('.',1)[1])
    if not (b.startswith('rib_') or b=='sternum'): return p
    kind,reason=(RIB_KINDS if b.startswith('rib_') else STERNUM_KINDS)[n]
    p.update(geometryKind=kind,geometryKindReason=reason,anatomicalMultiplicity='single')
    if b.startswith('rib_'):
        level=int(b.split('_')[1]); p['side']=b.split('_')[2]
        parent={3:2,4:2,6:5,9:8,10:7,11:7,12:7,15:7,16:7,17:7,19:7}.get(n)
        if parent: p['partOf']=own(b,f'A02.3.02.{parent:03}')
        if n==12:
            p['geometryTypeRefs']=deepcopy([ACADEMY,GRAY_R])
            p['refs']=deepcopy([*p['refs'],ACADEMY])
            p['geometryTypeConfidence']='moderate'; p['unresolvedFields']=['topography','specimen_extent']
            p['unresolvedFields'] += ['specimen_presence','level_applicability']
            p['applicabilityReview'] = dict(source='research/stage5-thorax-targeted-report-2026-10-18.md',
                level=level, side=p['side'], specimenPresence='unconfirmed', variantClassification='not_established')
            p['x'] += ' Наличие и выраженность гребня на этом экземпляре не подтверждены. Неопределённость не означает установленный анатомический вариант.'
            if level >= 11:
                p['x'] += ' Для XI–XII ребра нельзя переносить типовую трассу нижнего края с выраженной бороздой: нужны отдельные источники и разметка этого уровня.'
            # Existing incomplete anatomyVerification/evidenceScope and lack of coordinates are preserved.
        if n==3:
            levels=[level] if level in (1,10,11,12) else [level-1,level]
            p['relatedLandmarks']=[own(f'thoracic_{v}', 'A02.2.03.003' if v<level else 'A02.2.03.002') for v in levels]
            p['x']+=' Площадки принадлежат ребру; связанные ямки позвонков — противоположные поверхности, а не дубликаты этого ориентира.'
            if level==10:
                p['x']+=' В типичном описании — T10; вариант участия T9 проверяется отдельно и автоматически не связывается.'
                p['refs']=deepcopy([GRAY_R,BUCHANAN])
            elif level in (1,11,12): p['x']+=f' Соответствующий уровень — T{level}.'
            else: p['x']+=f' Соответствующие уровни — T{level-1} и T{level}; межпозвоночный диск не является костной площадкой.'
        if n==9:
            p['relatedLandmarks']=[own(f'thoracic_{level}','A02.2.03.004')]
            if level==10:
                p['inc']=1; p['refs']=deepcopy([GRAY_R,BUCHANAN])
                p['x']+=' Для X ребра выраженность рёберно-поперечного сочленения вариабельна; наличие на этом экземпляре не принято.'
        if n==8: p['x']+=' Суставная площадка и несуставной участок различаются; исходный маркер не описывает обе части.'
    else:
        if n in (3,4): p['partOf']=sterm(2)
        if n in (3,8,9): p['anatomicalMultiplicity']='paired' if n==3 else ('levels_and_sides' if n==8 else 'variable')
        if n==5: p['relatedLandmarks']=[sterm(2),sterm(6)]
        if n==3: p['relatedLandmarks']=[f'extra_sternum_clavicular_notch_{s}' for s in ('right','left')]
        if n==8: p['relatedLandmarks']=[f'extra_sternum_costal_notch_{i}_{s}' for i in range(1,8) for s in ('right','left')]
        if n in (2,6,7):
            p.setdefault('relatedLandmarks',[]).extend([f'extra_sternum_{n}_{v}_surface' for v in ('anterior','posterior')])
        if n==6: p['relatedLandmarks'].append('extra_sternum_foramen_variant')
        if n==7: p['relatedLandmarks'].append('extra_sternum_bifid_xiphoid_variant')
    if p.get('partOf'): p.setdefault('relatedLandmarks',[]).insert(0,p['partOf'])
    return protect(p)

def card(id,ru,kind,x,refs,**fields):
    return protect(dict(id=id,b='sternum',t='additional',ru=ru,lat='',x=x,m=[],geometryKind=kind,
        geometryKindReason='Предметное решение по указанным источникам; геометрия образца не принята.',
        refs=deepcopy(refs),educationAvailable=False,**fields))

def additional_records():
    for side,label in [('right','справа'),('left','слева')]:
        yield card(f'extra_sternum_clavicular_notch_{side}',f'Ключичная вырезка {label}','area',
            'Сторонний экземпляр парной суставной площадки рукоятки; исходная общая карточка сохранена как родитель.',
            [GRAY_S,AS_S],partOf=sterm(3),side=side,relatedLandmarks=[sterm(3),sterm(2)])
        for level in range(1,8):
            parts=[2] if level==1 else [2,6] if level==2 else [6,7] if level==7 else [6]
            where={1:'на рукоятке',2:'у перехода рукоятки в тело',7:'у перехода тела в мечевидный отросток'}.get(level,'на теле грудины')
            yield card(f'extra_sternum_costal_notch_{level}_{side}',f'Вырезка для {level}-го рёберного хряща {label}',
                'area',f'Контактный участок {where}. Соединяется с хрящом; костное ребро не подменяет хрящевой вклад.',
                [GRAY_S,PUBLISHER],partOf=sterm(8),side=side,level=level,
                relatedLandmarks=[sterm(8)]+[sterm(n) for n in parts],sternalParts=[sterm(n) for n in parts])
    for n,label in [(2,'рукоятки'),(6,'тела грудины'),(7,'мечевидного отростка')]:
        for view,ru in [('anterior','Передняя'),('posterior','Задняя')]:
            yield card(f'extra_sternum_{n}_{view}_surface',f'{ru} поверхность {label}','area',
                'Поверхность части, а не отдельная кость. Маска и границы на модели требуют проверки.',
                [GRAY_S,ELSEVIER],partOf=sterm(n),relatedLandmarks=[sterm(n)])
    yield card('extra_sternum_foramen_variant','Отверстие тела грудины — вариант','space',
        'Непостоянное отверстие тела грудины. Наличие в этой модели не установлено; не является обязательным ориентиром.',
        [MDCT,GRAY_S],inc=1,partOf=sterm(6),relatedLandmarks=[sterm(6)])
    yield card('extra_sternum_bifid_xiphoid_variant','Раздвоенный мечевидный отросток — вариант','volume',
        'Вариант формы конца мечевидного отростка. Не дополнительная кость и не подтверждённая форма этого GLB.',
        [MDCT,ELSEVIER],inc=1,partOf=sterm(7),relatedLandmarks=[sterm(7)])

def shared(id,ru,code,bones,x,refs,**fields):
    # The wholeTerms entry remains a generic reference, not a duplicate positioned instance.
    refs=[{**r,'id':r.get('id',f'rib_shared_{i}'),'authorGroup':r.get('authorGroup','gray_lewis_1918' if 'Gray' in r['title'] else 'anatomy_standard')} for i,r in enumerate(refs)]
    record = protect(dict(id=id,b=bones[0],t='ta',c=code,ru=ru,lat=T[code][0],x=x,m=[],
        relations=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in refs]) for b in bones],
        catalogueBones=[],anchors=[],refs=deepcopy(refs),geometryKind='space',educationAvailable=False,**fields))
    record['x'] += ' Контекстные BP24/BP28 не покрывают полный набор рёберных хрящей. Хрящевой край этого образца не подтверждён; типовая схема не является его разметкой.'
    if fields.get('concept') == 'thoracic-outlet':
        record['x'] += ' Состав рёберной дуги и соединения нижних хрящей вариабельны; не соединяйте автоматически участки VII–X.'
        record['refs'] += deepcopy([COSTAL_PATEL,COSTAL_RISK])
    return record

def shared_records():
    for level in range(1,12):
        for side,label in [('right','справа'),('left','слева')]:
            yield shared(f'shared_thorax_intercostal_{level}_{side}',f'{level}-е межреберье {label}',
                'A02.3.04.007',[f'rib_{level}_{side}',f'rib_{level+1}_{side}'],
                f'Пространство между рёбрами {level} и {level+1}. В передних отделах учитываются хрящи, а также мягкие ткани грудной стенки; костные связи описывают только часть границ.',
                [INTERCOSTAL,PUBLISHER],side=side,level=level,concept='intercostal-space',
                missingParticipants=['Раздельно размеченные рёберные хрящи и мягкотканные границы этого образца.'])
    yield shared('shared_thorax_superior_aperture','Верхняя апертура грудной клетки','A02.3.04.003',
        ['thoracic_1','rib_1_right','rib_1_left','sternum'],
        'Костные участники границы: T1, первые рёбра, верхний край рукоятки. Первые рёберные хрящи также участвуют, но не заменены костными связями.',
        [GRAY_W,AS_W],concept='thoracic-inlet',relatedLandmarks=[sterm(2)],
        missingParticipants=['Хрящи I рёбер: в проекте только агрегаты, без принятой разметки вклада.'])
    yield shared('shared_thorax_inferior_aperture','Нижняя апертура грудной клетки','A02.3.04.004',
        ['thoracic_12','rib_11_right','rib_11_left','rib_12_right','rib_12_left','sternum'],
        'Граница включает T12, XI–XII рёбра, рёберные дуги и мечевидный отросток. Связи относятся только к костным участникам; диафрагма закрывает отверстие, но не подменяет его костно-хрящевой край.',
        [GRAY_W,AS_W],concept='thoracic-outlet',relatedLandmarks=[sterm(7)],
        missingParticipants=['Индивидуально идентифицированные хрящевые участки рёберных дуг и принятая граница апертуры.'])

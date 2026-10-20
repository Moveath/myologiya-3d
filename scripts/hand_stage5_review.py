"""Right hand: explicit anatomical families; no generated positions or meshes."""
from copy import deepcopy
from arm_forearm_stage5_review import ref, TA

REPORT = 'research/stage5-hand-report-2026-10-19.md'
CARPALS = ['scaphoid','lunate','triquetrum','pisiform','trapezium','trapezoid','capitate','hamate']
METACARPALS = [f'metacarpal_{i}' for i in range(1,6)]
PHALANGES = ([f'phalanx_prox_{i}' for i in range(1,6)] +
             [f'phalanx_mid_{i}' for i in range(2,6)] + [f'phalanx_dist_{i}' for i in range(1,6)])
OWNERS = set(CARPALS + METACARPALS + PHALANGES + ['flexor_retinaculum'])
GRAY = ref('hand_gray1918','Gray (1918) — Hand bones',
    'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf',
    'PDF pp.209–225: carpus, metacarpus, phalanges; p.302: sesamoids. Historical synonyms mapped to TA98.', 'full_text')
SOB = ref('hand_sobotta1914','Sobotta / McMurrich (1914), vol. I',
    'https://archive.org/download/atlastextbookofh01sobouoft/atlastextbookofh01sobouoft_djvu.txt',
    'Printed pp.90–93: carpal arch, articular surfaces, metacarpals, phalanges, sesamoids; pp.125–129: hand joints.', 'full_text')
NCBI = ref('hand_bones','Arias, Black, Varacallo — Hand Bones (2023)',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK547684/',
    'Structure and Function: 27 bones, CMC/MCP/IP articulations. Conflicting statement about four constant sesamoids NOT adopted.', 'full_text')
CARPAL = ref('carpal_bones','Tang, Varacallo — Hand Carpal Bones (2022)',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK535382/',
    'Structure and Function: rows, pisotriquetral surface, trapezium saddle, transverse carpal arch.', 'full_text')
RET = ref('retinaculum','NCBI Bookshelf — Wrist Flexor Retinaculum',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK545198/',
    'Structure and Function: fibro-osseous tunnel; four bony attachments and fibrous roof.', 'full_text')
WRIST = ref('radiocarpal_joint','Helms, Maldonado, Burns — Hand Radiocarpal Joint (2023)',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK539744/',
    'Structure and Function: radius, scaphoid, lunate, triquetrum; articular disc and indirect ulnar-side articulation.', 'full_text')
CENTRALE = ref('centrale_24511506','Hong, Park, Nam (2014) — Bipartite os Centrale Carpi',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC3915168/',
    'Opening paragraph; CT and operative findings. PMID24511506; DOI10.5999/aps.2014.41.1.98. Case establishes an accessory bone, not a population frequency.', 'full_text')
CHEN = ref('sesamoid_chen2015','Chen et al. (2015) — sesamoid bones of the hand',
    'https://e-century.us/files/ijcem/8/7/ijcem0009673.pdf',
    'PMID26380010; approved scope B2/B3, V1–V5; qualitative presence only, not conflicting percentages.', 'full_text')
CIVAN = ref('sesamoid_civan2020','Civan et al. (2020) — sesamoid bones of the hand',
    'https://www.jointdrs.org/full-text/432',
    'PMID32160497; DOI10.5606/ehc.2020.70955; MCP I radial/ulnar pair and variable other sites.', 'full_text')
THUMB = ref('thumb_mcp2023','Knisely, Noland, Melville (2023) — Ultrasound versus MRI of thumb MCP',
    'https://jultrason.pl/assets/pdf/artykuly/5-jou-2023-0030.pdf',
    'p.e216, Sesamoids: pair in volar plate; radial and ulnar identity. DOI10.15557/JoU.2023.0030.', 'full_text')
NOTE = 'Положение и протяжённость на данном образце не приняты анатомически. Нужна разметка соответствующей поверхности, траектории или объёма с независимой анатомической проверкой.'


def limits(p):
    p.update(side='right', educationAvailable=False,
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT),
        geometryRequirements=dict(status='unverified_extent', neededEvidence=NOTE),
        handReview=dict(source=REPORT, scope='catalogue_and_representation', geometryAccepted=False))
    p['modelNote'] = ('Исходная координата сохранена; близость к мешу не подтверждает локализацию. ' if p.get('p') else 'Координат нет. ') + NOTE
    return p


def review(record):
    if record['b'] not in OWNERS: return record
    p = deepcopy(record); pid = p['id']; b = p['b']; refs = [GRAY, SOB]
    # Families are selected by known anatomical entity, not a keyword classifier.
    if b in METACARPALS and pid.endswith(('_basis','_corpus','_caput')):
        part = pid.rsplit('_',1)[1]
        kind = 'volume'
        definition = {'basis':'Проксимальная часть пястной кости; её суставные площадки следует выделять отдельно от всего основания.',
            'corpus':'Протяжённое тело пястной кости, а не точка на его середине.',
            'caput':'Дистальная головка пястной кости; суставная поверхность для проксимальной фаланги составляет только часть головки.'}[part]
    elif b in PHALANGES:
        part = pid.rsplit('_',1)[1]; distal = b.startswith('phalanx_dist_')
        kind = 'area' if part in ('trochlea','tuberositas') else 'volume'
        definition = {'basis':'Проксимальное основание фаланги. Вогнутая суставная площадка основания отличается от полного объёма этой части.',
            'corpus':'Тело фаланги между основанием и дистальным концом. Ладонная и дорсальная поверхности требуют отдельных масок.',
            'caput':'Дистальный конец фаланги; у проксимальной и средней фаланг несёт суставной блок.',
            'trochlea':'Блоковидная суставная поверхность дистального конца проксимальной или средней фаланги; не вся головка.',
            'tuberositas':'Шероховатая подковообразная ладонная область концевого расширения дистальной фаланги; не межфаланговая суставная площадка.'}[part]
        if distal and part == 'caput':
            definition = 'Термин исходного каталога для несуставного дистального конца. Дистальная фаланга не образует здесь следующего межфалангового сустава. Применимость общего термина caput требует номенклатурного уточнения; отдельная новая «головка» не добавлена.'
            p['nomenclatureReview'] = 'general_TA98_term_applicability_requires_review'
        if part == 'trochlea': p['partOf'] = pid.replace('_trochlea','_caput')
        if b.startswith('phalanx_mid_') and part == 'basis':
            p['note'] = 'Точная область прикрепления поверхностного сгибателя требует сверки: университетская таблица UAMS указывает тело средней фаланги, обзор Hand Bones — основание. Исходные связи не приняты как разметка прикрепления; CAT-HAND-DETAIL.'
    else:
        kind, definition = {
            'scaph_tuberculum':('volume','Ладонное костное возвышение ладьевидной кости, одна из лучевых опор удерживателя сгибателей.'),
            'trapz_tuberculum':('volume','Ладонное возвышение кости-трапеции; отличается от соседней борозды сухожилия лучевого сгибателя запястья.'),
            'ham_hamulus':('volume','Костный крючок ладонной стороны крючковидной кости; часть локтевой опоры удерживателя сгибателей.'),
            'mc3_processus_styloideus':('volume','Выступ дорсолучевой части основания III пястной кости; не шиловидный отросток лучевой кости.'),
            'carp_sulcus_carpi':('area','Ладонная вогнутость костной дуги запястья. Это костное ложе; замкнутый запястный канал дополнительно ограничен удерживателем сгибателей.'),
            'carp_os_centrale':('volume','Вариабельная самостоятельная добавочная кость между ладьевидной, головчатой и трапециевидной костями. Не образована слиянием восьми костей запястья и не является обязательным сесамоидом.'),
            'pisiform_apex':('area','Область мышечных прикреплений на гороховидной кости; не отдельная кость и не один подтверждённый апикальный пункт.'),
            'att_trapezoid_palmar':('area','Область прикрепления на ладонной поверхности трапециевидной кости. Сохранённый маркер не задаёт границы прикрепления.'),
            'att_capitate_palmar':('area','Область прикреплений на ладонной поверхности головчатой кости; не вся поверхность и не единая точка нескольких мышц.'),
            'retinaculum_mid':('area','Фиброзная пластинка, перекрывающая костную борозду запястья с ладонной стороны; крыша канала, не костная поверхность и не весь канал.'),
        }[pid]
    p.update(geometryKind=kind, geometryKindReason=definition, anatomicalDefinition=definition)
    if p['t'] == 'ta': refs.append(ref('ta98','FIPAT / IFAA — TA98',TA,p['c'],'official_list'))
    if pid == 'carp_os_centrale':
        p.pop('sh',None)
        p.update(x=definition, anatomicalVariant=True, specimenPresence='unverified', anchorStatus='unverified',
            anatomicalEntity='accessory_bone_variant', catalogueBones=[],
            relations=[dict(bone=k,role='adjacentContext',evidence='hand_centrale') for k in ('scaphoid','trapezoid','capitate')])
        refs += [CENTRALE]
    if pid == 'carp_sulcus_carpi':
        p.pop('sh',None)
        p.update(x=definition, catalogueBones=[], anatomicalEntity='bony_groove',
            relations=[dict(bone=k,role='boundaryContribution',evidence='hand_carpal_arch') for k in CARPALS],
            relatedLandmarks=['extra_hand_carpal_tunnel','retinaculum_mid'])
        refs += [CARPAL,RET]
    if pid == 'retinaculum_mid':
        p.update(anatomicalEntity='fibrous_retinaculum',relatedLandmarks=['carp_sulcus_carpi','extra_hand_carpal_tunnel'])
        refs += [RET]
    p['refs'] = deepcopy(p.get('refs',[])) + deepcopy(refs)
    return limits(p)


SESAMOID_BONES = {}
for component, ru, scope in [('radial','Лучевая','B2'),('ulnar','Локтевая','B3')]:
    SESAMOID_BONES['sesamoid_mcp1_'+component+'_right'] = dict(
        ru=ru+' сесамовидная кость большого пальца кисти справа',
        searchAliases=[ru+' сесамовидная кость I пястно-фалангового сустава',
                       'сесамоид большого пальца', 'большой палец'],
        catalogueRole='typical_thumb_sesamoid',
        lat='ossa sesamoidea', en=component+' sesamoid of the right thumb MCP joint',
        g='b_hand_sesamoids',sub='hand',sec='arm',side='right',noModel=True,
        collectiveCode='A02.4.11.001',scopeId=scope,
        contextTargets=['metacarpal_1','phalanx_prox_1'],
        nomenclatureStatus='descriptive_individual_name_collective_TA98_term',
        termScopeNote='Латынь и код TA98 относятся к группе сесамовидных костей, не к отдельному официально кодированному лучевому/локтевому экземпляру. Русское название описательное.',
        x=ru+' кость типичной пары на ладонной стороне I пястно-фалангового сустава. Эти кости включены в комплекс ладонной пластинки. Наличие пары в типичном учебном каталоге не доказывает её форму на данном образце.',
        note='Именованной и анатомически подтверждённой модели нет. Правая сторона указана по учебному объёму; координаты и зеркальная реконструкция не создавались. Возможна многокомпонентность сесамоида; это не автоматически перелом или дополнительная обязательная кость.',
        refs=deepcopy([CHEN,CIVAN,THUMB,ref('ta98_sesamoids','FIPAT / IFAA — TA98',TA,'A02.4.11.001: collective entry only','official_list')]))

BONE_PATCHES = {b:dict(side='right') for b in OWNERS}


def extra(key,b,ru,kind,definition,refs=None,**fields):
    return limits(dict(id='extra_hand_'+key,b=b,t='additional',ru=ru,lat='',x=definition,
        anatomicalDefinition=definition,geometryKind=kind,geometryKindReason=definition,
        p=None,n=None,m=[],g='Дополнительные образования',
        nomenclatureStatus='descriptive_term_without_assigned_TA98_code',
        refs=deepcopy(refs or [GRAY,SOB,NCBI]),**fields))


def joint(key,ru,bones,definition,refs=None):
    return extra(key,bones[0],ru+' справа','space',definition,refs,
        anatomicalEntity='joint',catalogueBones=[],
        relations=[dict(bone=b,role='component',evidence='hand_joint_'+key) for b in bones])


def additional_records():
    yield extra('carpal_tunnel','capitate','Запястный канал справа','space',
        'Костно-фиброзное пространство между вогнутостью запястья и удерживателем сгибателей. Костные меши не определяют положение и толщину фиброзной крыши или содержимого канала.',[CARPAL,RET,SOB],
        anatomicalEntity='fibro_osseous_tunnel',catalogueBones=[],
        relations=[dict(bone=b,role='boundaryContribution',evidence='carpal_arch') for b in CARPALS],
        softTissueComponents=['flexor_retinaculum'],relatedLandmarks=['carp_sulcus_carpi','retinaculum_mid'])
    yield extra('trapezium_fcr_groove','trapezium','Борозда сухожилия лучевого сгибателя запястья справа','line',
        'Продольная борозда ладонной поверхности кости-трапеции рядом с её бугорком. Требуется трасса борозды; её канал не следует смешивать с общим запястным каналом.',[GRAY,SOB],relatedLandmarks=['trapz_tuberculum'])
    for b,partner,ru in [('pisiform','triquetrum','Суставная поверхность гороховидной кости'),
                         ('triquetrum','pisiform','Суставная поверхность для гороховидной кости'),
                         ('trapezium','metacarpal_1','Седловидная поверхность кости-трапеции для I пястной кости'),
                         ('metacarpal_1','trapezium','Суставная поверхность основания I пястной кости')]:
        yield extra(b+'_facet_'+partner,b,ru+' справа','area',
            'Собственная суставная площадка кости для указанного партнёра; две противолежащие площадки не сливаются в один костный ориентир.',[GRAY,SOB,CARPAL],
            articulatesWith=[partner],relatedLandmarks=['extra_hand_'+('pisotriquetral_joint' if b in ('pisiform','triquetrum') else 'cmc1_joint')])
    yield joint('radiocarpal_joint','Лучезапястный сустав',['radius','scaphoid','lunate','triquetrum'],
        'Проксимальная сторона образована дистальным концом лучевой кости и суставным диском, дистальная — ладьевидной, полулунной и трёхгранной костями. Локтевая кость не имеет здесь прямой костной площадки для запястья. Суставной диск не представлен подтверждённой разметкой.',[SOB,WRIST])
    yield joint('pisotriquetral_joint','Гороховидно-трёхгранный сустав',['pisiform','triquetrum'],
        'Самостоятельное сочленение дорсальной площадки гороховидной кости с ладонной площадкой трёхгранной; это сустав, а не ещё одна общая костная поверхность.',[GRAY,SOB,CARPAL])
    yield joint('cmc1_joint','I запястно-пястный сустав',['trapezium','metacarpal_1'],
        'Седловидное сочленение кости-трапеции с основанием I пястной кости. Не включает трапециевидную кость только из-за близости.')
    for i in range(1,6):
        bones=[f'metacarpal_{i}',f'phalanx_prox_{i}']
        if i==1: bones += list(SESAMOID_BONES)
        yield joint(f'mcp{i}_joint',f'{i} пястно-фаланговый сустав',bones,
            'Сочленение головки пястной кости с основанием проксимальной фаланги.'+
            (' В комплекс ладонной пластинки большого пальца включены две типичные сесамовидные кости; их модели отсутствуют.' if i==1 else ' Вариабельные сесамоиды не заявлены обязательными компонентами.'),
            [GRAY,SOB,NCBI,THUMB] if i==1 else None)
        pairs=[('ip',f'phalanx_prox_{i}',f'phalanx_dist_{i}','Межфаланговый сустав большого пальца')] if i==1 else [
            ('pip',f'phalanx_prox_{i}',f'phalanx_mid_{i}',f'Проксимальный межфаланговый сустав {i} пальца'),
            ('dip',f'phalanx_mid_{i}',f'phalanx_dist_{i}',f'Дистальный межфаланговый сустав {i} пальца')]
        for prefix,a,b,ru in pairs:
            yield joint(f'{prefix}{i}_joint',ru,[a,b],
                'Сустав между головкой более проксимальной фаланги и основанием следующей. У большого пальца нет средней фаланги; кончик дистальной фаланги не образует следующего сустава.')
    for i in range(1,5):
        yield extra(f'intermetacarpal_space_{i}',f'metacarpal_{i}',f'{i} межпястный промежуток справа','space',
            'Промежуток между соседними пястными костями; не синовиальный межпястный сустав и не отдельная кость. Мягкотканное содержимое и полные границы не размечены.',[GRAY,SOB],
            anatomicalEntity='interosseous_space',catalogueBones=[],
            relations=[dict(bone=f'metacarpal_{j}',role='boundaryContribution',evidence='metacarpal_interosseous_spaces') for j in (i,i+1)])
    for scope,key,bones,label in [('V1','mcp2',['metacarpal_2','phalanx_prox_2'],'II пястно-фалангового сустава'),
        ('V2','mcp5',['metacarpal_5','phalanx_prox_5'],'V пястно-фалангового сустава'),
        ('V3','ip1',['phalanx_prox_1','phalanx_dist_1'],'межфалангового сустава большого пальца'),
        ('V4','mcp3',['metacarpal_3','phalanx_prox_3'],'III пястно-фалангового сустава'),
        ('V5','mcp4',['metacarpal_4','phalanx_prox_4'],'IV пястно-фалангового сустава')]:
        yield extra('variant_sesamoid_'+key,bones[0],'Вариабельные сесамовидные кости '+label+' справа','volume',
            'Категория индивидуального варианта, не обязательная кость типичного скелета. Наличие, число и положение у данного образца не установлены; отдельная модель и координаты не добавлены.',[CHEN,CIVAN],
            anatomicalEntity='sesamoid_variant',anatomicalVariant=True,specimenPresence='unverified',scopeId=scope,catalogueBones=[],
            relations=[dict(bone=b,role='adjacentContext',evidence='sesamoid_scope_'+scope) for b in bones])

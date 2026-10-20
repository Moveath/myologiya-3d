"""Addressed arm/forearm catalogue review. Never creates or mirrors coordinates."""
from copy import deepcopy
from upper_girdle_stage5_review import GRAY, SOBOTTA, TA

REPORT = 'research/stage5-arm-forearm-report-2026-10-18.md'
OWNERS = {'humerus', 'humerus_left', 'radius', 'ulna', 'interosseous_membrane'}
TA_JOINTS = 'https://ifaa.unifr.ch/Public/EntryPage/TAH1434%20Part98A3%20EN.htm'

def ref(key, title, url, locator, access='full_text'):
    return dict(id='arm_forearm_'+key, title=title, url=url, locator=locator,
                access=access, checked='2026-10-18')

GRAY_REF = ref('gray', 'Gray / Lewis (1918) — Humerus; Ulna; Radius', GRAY,
    'PDF pp.188–211 (one-based): Humerus, Ulna, Radius; explicit entity subsections. Historical public-domain text.')
SOB_REF = ref('sobotta', 'Sobotta / McMurrich (1914), Vol. I', SOBOTTA,
    'Printed pp.85–89, Figs.113–125; pp.121–124, shoulder, elbow and radioulnar joints. OCR text; no claim of modern atlas access.')
HUM_NCBI = ref('humerus', 'Anatomy, Shoulder and Upper Limb, Humerus — StatPearls',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK534821/', 'Introduction; Structure and Function: joint participants only. Erroneous flexion statement for olecranon fossa is not adopted.')
PRUJ = ref('pruj', 'Williams, Varacallo (2023) — Proximal Radio-Ulnar Joint',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK551614/', 'Introduction; Structure and Function; Muscles.')
DRUJ = ref('druj', 'Arias, Varacallo (2025) — Distal Radio-Ulnar Joint',
    'https://www.ncbi.nlm.nih.gov/sites/books/NBK547720/', 'Structure and Function / Osteology; TFCC. No specimen dimensions adopted.')
LD = ref('latissimus', 'UAMS — Muscles of the Upper Limb',
    'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-upper-limb/',
    'Latissimus dorsi: insertion, floor of intertubercular groove; brachialis, supinator, pronator quadratus rows.')
VARIANTS = [ref('natsis', 'Natsis (2008) — Supracondylar process of the humerus: study on 375 Caucasian subjects in Cologne, Germany.',
    'https://pubmed.ncbi.nlm.nih.gov/18266286/', 'Abstract; PMID 18266286; DOI 10.1002/ca.20601. Population results do not establish presence in these meshes.', 'indexed_abstract'),
    ref('aydinlioglu', 'Aydinlioglu, Gumrukcuoglu, Koyun (2010) — The prevalence of supracondyloid process in the living: a radiographic study.',
        'https://pubmed.ncbi.nlm.nih.gov/21473404/', 'Abstract; PMID 21473404. Independent radiographic series; bilateral variation, no mirror inference.', 'indexed_abstract')]

# Each number is the final component of an existing TA98 code. These are
# explicit decisions about an anatomical entity, not keyword inference.
HUMERUS = {
 2: ('volume', 'Проксимальная головка, обращённая медиально, вверх и несколько назад; её суставная поверхность обращена к суставной впадине лопатки. Головка целиком и покрывающая её поверхность — разные объекты разметки.'),
 3: ('line', 'Граница головки плечевой кости у основания её суставной поверхности; кольцевой путь, а не одна точка.'),
 4: ('volume', 'Суженный участок плечевой кости дистальнее бугорков; не совпадает с границей суставной поверхности головки.'),
 5: ('volume', 'Латеральное возвышение проксимального конца с площадками прикрепления мышц вращательной манжеты. Весь бугорок не равен одной площадке.'),
 6: ('volume', 'Переднее возвышение проксимального конца, направленное также медиально; отдельно от большого бугорка и межбугорковой борозды.'),
 7: ('line', 'Продольная борозда между бугорками и их гребнями. По ней проходит сухожилие длинной головки двуглавой мышцы; типичное прикрепление широчайшей мышцы относится к дну борозды. Линия обозначает путь, но не принятую ширину или площадь прикрепления.'),
 8: ('line', 'Продолжение большого бугорка вниз, латеральная губа межбугорковой борозды; не весь передний край тела.'),
 9: ('line', 'Продолжение малого бугорка вниз, медиальная губа межбугорковой борозды; место прикрепления большой круглой мышцы. Типичное прикрепление широчайшей мышцы к дну борозды показано у самой борозды.'),
 10: ('volume', 'Тело между проксимальным и дистальным концами. В описательной остеологии различают три поверхности и три края: передний, медиальный и латеральный; передний край разделяет две передние поверхности.'),
 11: ('area', 'Переднемедиальное поле тела между передним и медиальным краями; его верхний участок включает продолжение дна межбугорковой борозды.'),
 12: ('area', 'Переднелатеральное поле тела между передним и латеральным краями, включая область дельтовидной бугристости.'),
 13: ('area', 'Задняя поверхность тела между медиальным и латеральным краями; борозда лучевого нерва пересекает её косо.'),
 14: ('line', 'Косой путь борозды на задней поверхности тела для лучевого нерва и сопровождающих сосудов. Одна сохранённая точка не задаёт весь путь.'),
 15: ('line', 'Медиальная граница тела, отделяющая переднемедиальную поверхность от задней.'),
 16: ('line', 'Дистальный гребень медиального края, направленный к медиальному надмыщелку.'),
 17: ('volume', 'Непостоянный надмыщелковый отросток переднемедиальной стороны дистального отдела плечевой кости. Не обязательная структура типичного скелета; наличие справа и слева у данного образца отдельно не подтверждено. Частоты и расстояния из исследований не задают координату модели.'),
 18: ('line', 'Латеральная граница тела между переднелатеральной и задней поверхностями.'),
 19: ('line', 'Дистальный гребень латерального края, направленный к латеральному надмыщелку.'),
 20: ('area', 'Шероховатая область прикрепления дельтовидной мышцы на латеральной стороне тела. Здесь требуется маска всей бугристости, а не только её вершина.'),
 21: ('volume', 'Расширенная дистальная суставная часть плечевой кости, включающая головку мыщелка и блок; не синоним одного из надмыщелков.'),
 22: ('volume', 'Латеральная округлая суставная часть мыщелка для суставной ямки головки лучевой кости. Отличается от проксимальной головки плечевой кости.'),
 23: ('volume', 'Медиальная блоковидная суставная часть мыщелка, соответствующая блоковидной вырезке локтевой кости.'),
 24: ('area', 'Углублённая поверхность сзади над блоком; принимает локтевой отросток при разгибании. Это ямка, а не постоянное сквозное отверстие.'),
 25: ('area', 'Углублённая поверхность спереди над блоком для венечного отростка при сгибании.'),
 26: ('area', 'Углублённая поверхность спереди над головкой мыщелка для края головки лучевой кости при сгибании.'),
 27: ('volume', 'Медиальное внесуставное возвышение дистального конца; не головка мыщелка и не общий локтевой сустав.'),
 28: ('line', 'Борозда позади медиального надмыщелка, по которой проходит локтевой нерв. Контур и глубина отдельно не размечены.'),
 29: ('volume', 'Латеральное внесуставное возвышение дистального конца, отличное от суставной головки мыщелка.'),
}
RADIUS = {
 2: ('volume', 'Дисковидная проксимальная головка; верхняя суставная ямка и боковая суставная окружность представлены отдельно.'),
 3: ('area', 'Вогнутая суставная площадка верхней стороны головки для головки мыщелка плечевой кости.'),
 4: ('area', 'Суставная поверхность по окружности головки, участвующая в проксимальном лучелоктевом суставе; кольцевая связка не является частью костного меша.'),
 5: ('volume', 'Суженный участок непосредственно дистальнее головки, проксимальнее бугристости.'),
 6: ('volume', 'Тело лучевой кости, изогнутое латерально; имеет переднюю, заднюю и латеральную поверхности и три края.'),
 7: ('area', 'Область бугристости у проксимального конца ниже шейки, с шероховатым полем прикрепления сухожилия двуглавой мышцы и гладким участком для сумки.'),
 8: ('area', 'Передняя поверхность тела между передним и межкостным краями. Площадь поверхности и отдельные мышечные прикрепления требуют раздельной разметки.'),
 9: ('area', 'Задняя поверхность тела между задним и межкостным краями; не борозды сухожилий на дистальном конце.'),
 10: ('area', 'Латеральная поверхность тела между передним и задним краями; содержит область прикрепления круглого пронатора.'),
 11: ('area', 'Шероховатая область средней части латеральной поверхности для круглого пронатора; часть латеральной поверхности, не самостоятельная кость.'),
 12: ('line', 'Медиальный край лучевой кости, обращённый к локтевой; место прикрепления межкостной перепонки, но не вся перепонка.'),
 13: ('line', 'Граница передней и латеральной поверхностей; выраженность меняется вдоль тела.'),
 14: ('line', 'Граница задней и латеральной поверхностей; полный путь не задаётся одним маркером.'),
 15: ('volume', 'Выступ латеральной стороны дистального конца лучевой кости; отдельная костная часть, не точка запястного сустава.'),
 16: ('line', 'Продольный гребень над шиловидным отростком на латеральной стороне; связан с областью прикрепления плечелучевой мышцы.'),
 17: ('volume', 'Дорсальное возвышение дистального конца, бугорок Листера; ориентир хода сухожилия длинного разгибателя большого пальца.'),
 18: ('line', 'Несколько путей сухожильных борозд дорсальной стороны дистального конца. Требуются отдельные трассы и границы, а не одна выдуманная линия по центру кости.'),
 19: ('area', 'Вогнутая суставная площадка медиальной стороны дистального конца для суставной окружности головки локтевой кости.'),
 20: ('area', 'Дистальная суставная поверхность лучевой кости с площадками для ладьевидной и полулунной костей. Суставной диск дополняет проксимальную сторону лучезапястного сустава со стороны локтевой кости; он не превращает эту костную поверхность в отдельную площадку для трёхгранной кости.'),
}
ULNA = {
 2: ('volume', 'Крупный задний отросток проксимального конца, образующий верхнюю часть блоковидной вырезки; при разгибании входит в ямку локтевого отростка плечевой кости.'),
 3: ('volume', 'Передний отросток проксимального конца, ограничивающий блоковидную вырезку снизу.'),
 4: ('area', 'Шероховатая область на передней стороне ниже венечного отростка, связанная с прикреплением плечевой мышцы.'),
 5: ('area', 'Суставная вырезка латеральной стороны проксимального конца для окружности головки лучевой кости; рассматривается её вогнутая суставная поверхность.'),
 6: ('area', 'Вогнутая суставная поверхность между локтевым и венечным отростками для блока плечевой кости; не сквозной канал.'),
 7: ('volume', 'Тело локтевой кости, сужающееся дистально; три поверхности и три края.'),
 8: ('area', 'Передняя поверхность тела между передним и межкостным краями; дистальное поле квадратного пронатора — только часть этой поверхности.'),
 9: ('area', 'Задняя поверхность тела между задним и межкостным краями.'),
 10: ('area', 'Медиальная поверхность тела между передним и задним краями.'),
 11: ('line', 'Латеральный край локтевой кости, обращённый к лучевой; место прикрепления межкостной перепонки.'),
 12: ('line', 'Граница передней и медиальной поверхностей тела.'),
 13: ('line', 'Задняя граница между задней и медиальной поверхностями, продолжающаяся от области локтевого отростка вдоль тела.'),
 14: ('line', 'Гребень, спускающийся от задней границы лучевой вырезки; костный ориентир области начала супинатора.'),
 15: ('volume', 'Округлый дистальный конец локтевой кости. Боковая суставная окружность взаимодействует с лучевой костью, дистальная поверхность — с суставным диском; прямой костной площадки для запястья здесь нет.'),
 16: ('area', 'Боковая суставная поверхность головки для локтевой вырезки лучевой кости; не вся головка и не суставной диск.'),
 17: ('volume', 'Заднемедиальный выступ у головки локтевой кости; отличается от соседней ямки и борозды сухожилия локтевого разгибателя запястья.'),
}
SOFT = {
 'hum_body_ant': 'Область начала плечевой мышцы на дистальной части передних поверхностей плечевой кости; не отдельный термин остеологии и не единственная точка.',
 'rad_supinator': 'Область прикрепления супинатора, охватывающая поверхности проксимальной части лучевой кости; требуется пространственно связанная маска поверхности.',
 'uln_distal_anterior': 'Область начала квадратного пронатора на дистальной части передней поверхности локтевой кости; отдельно от всей передней поверхности.',
 'membrane_mid': 'Межкостная перепонка предплечья — фиброзная пластинка между межкостными краями лучевой и локтевой костей. Это мягкотканное соединение, а не костная поверхность, синовиальный сустав или весь межкостный промежуток.',
}

def limits(p):
    need = 'Маска/трасса или сегмент данного образца с анатомической приёмкой; для суставов также данные о хряще, капсуле и связках.'
    p.update(geometryRequirements=dict(status='unverified_extent', neededEvidence=need),
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT),
        armForearmReview=dict(source=REPORT, scope='catalogue_and_representation', geometryAccepted=False), educationAvailable=False)
    p['modelNote'] = ('Сохранённая координата не подтверждает анатомическую локализацию. ' if p.get('p') else 'Координат нет; отражение другой стороны не применялось. ') + need
    return p

def review(record):
    if record.get('b') not in OWNERS: return record
    p = deepcopy(record); b = p['b']; refs = [GRAY_REF, SOB_REF]
    if p['t'] == 'ta':
        number = int(p['c'].split('.')[-1]); table = HUMERUS if b.startswith('humerus') else RADIUS if b == 'radius' else ULNA
        kind, definition = table[number]
        refs += [ref('ta98', 'FIPAT / IFAA — TA98 osteology', TA, p['c'], 'official_list')]
    else:
        kind, definition = 'area', SOFT[p['id']]; refs += [LD, PRUJ]
    p.update(geometryKind=kind, geometryKindReason=definition, anatomicalDefinition=definition, x=definition,
             side='left' if b.endswith('_left') else 'right')
    if b.startswith('humerus') and p.get('c', '').endswith(('.007', '.009')):
        refs += [LD, ref('ld_variation', 'Bhatt et al. (2013) — Variation in the insertion of the latissimus dorsi & its clinical importance',
            'https://pubmed.ncbi.nlm.nih.gov/24403744/', 'Abstract: usual insertion in groove floor; observed variant distinguished. PMID and metadata verified via EFetch.', 'indexed_abstract')]
        p['note'] = 'Источники расходятся: Sobotta (1914), p.86, относит широчайшую мышцу к гребню малого бугорка; Gray, UAMS и современная публикация описывают типичное прикрепление ко дну борозды. Границы прикрепления на данном образце не приняты.'
    if p['id'] == 'hum_crista_tuberculi_minoris': p['m'] = [m for m in p['m'] if m[0] != 'latissimus_dorsi']
    if p['id'] == 'hum_sulcus_intertubercularis': p['m'] = p['m'] + [['latissimus_dorsi', 'i']]
    if b.startswith('humerus') and p.get('c') == 'A02.4.04.017':
        p.update(anatomicalVariant=True, specimenPresence='unverified', anchorStatus='unverified'); refs += VARIANTS
    if p['id'] == 'membrane_mid':
        p['anatomicalEntity'] = 'fibrous_membrane'
        p['relatedLandmarks'] = ['rad_margo_interosseus', 'uln_margo_interosseus']
    if p['id'] in ('rad_margo_interosseus', 'uln_margo_interosseus'): p['relatedLandmarks'] = ['membrane_mid']
    parents = {'rad_fovea_articularis':'rad_caput', 'rad_circumferentia_articularis':'rad_caput',
        'rad_tuberositas_pronatoria':'rad_facies_lateralis', 'uln_circumferentia_articularis':'uln_caput',
        'hum_capitulum':'hum_condylus', 'hum_trochlea':'hum_condylus'}
    if p['id'] in parents: p['partOf'] = parents[p['id']]
    if b == 'humerus_left' and p.get('c') in ('A02.4.04.022','A02.4.04.023'): p['partOf'] = 'context_humerus_left_A02_4_04_021'
    p['refs'] = deepcopy(p.get('refs', []))
    for r in refs:
        if r['url'] not in {q['url'] for q in p['refs']}: p['refs'].append(deepcopy(r))
    return limits(p)

def extra(b, key, ru, kind, definition, refs, **fields):
    return limits(dict(id='extra_'+b+'_'+key, b=b, t='additional', ru=ru, lat='', x=definition,
        anatomicalDefinition=definition, geometryKind=kind, geometryKindReason=definition,
        p=None, n=None, m=[], side='left' if b.endswith('_left') else 'right',
        g='Дополнительные образования', nomenclatureStatus='descriptive_term_without_assigned_TA98_code', refs=deepcopy(refs), **fields))

def additional_records(bones):
    for b in sorted(bones & (OWNERS - {'interosseous_membrane'})):
        side = 'слева' if b.endswith('_left') else 'справа'
        yield extra(b, 'nutrient_foramina', 'Питательные отверстия '+side, 'space',
            'Входы сосудистых каналов тела кости. Число, диаметр и расположение вариабельны; карточка обозначает категорию образований, а не одно установленное отверстие этого меша.', [GRAY_REF, SOB_REF], anatomicalEntity='foramina_group')
        if b.startswith('humerus'):
            yield extra(b, 'anterior_border', 'Передний край плечевой кости '+side, 'line',
                'Граница переднемедиальной и переднелатеральной поверхностей тела. Проксимально связана с гребнем большого бугорка, но не совпадает с ним по всей длине.', [GRAY_REF, SOB_REF])
            joint = extra(b, 'glenohumeral_joint', 'Плечевой сустав '+side, 'volume',
                'Сустав головки плечевой кости и суставной впадины лопатки. Суставные поверхности остаются собственными образованиями своих костей; хрящ, губа и капсула не выводятся из костных мешей.',
                [SOB_REF, HUM_NCBI, ref('ta_gh', 'FIPAT / IFAA — TA98, Chapter 3', 'https://ifaa.unifr.ch/Public/EntryPage/PDF/TA98%20Chapter%203.pdf', 'A03.5.08.001', 'official_list')],
                anatomicalEntity='joint', educationCode='A03.5.08.001', catalogueBones=[], anchors=[],
                relations=[dict(bone=x, role='component') for x in (b, 'scapula_left' if b.endswith('_left') else 'scapula')])
            joint.update(lat='articulatio humeri', nomenclatureStatus='TA98_term')
            yield joint
    if 'ulna' in bones:
        yield extra('ulna', 'distal_fovea', 'Ямка у основания шиловидного отростка локтевой кости справа', 'area',
            'Углублённая область между головкой и основанием шиловидного отростка, связанная с прикреплением элементов треугольного фиброзно-хрящевого комплекса. Не суставная окружность и не весь шиловидный отросток.', [GRAY_REF, DRUJ])
        yield extra('ulna', 'ecu_groove', 'Борозда сухожилия локтевого разгибателя запястья справа', 'line',
            'Дорсальная борозда у дистального конца локтевой кости для сухожилия локтевого разгибателя запястья. Отличается от лучевых борозд и от ямки у основания шиловидного отростка.', [GRAY_REF, DRUJ])
    if 'humerus' in bones:
        joints = [
          ('elbow_joint', 'Локтевой сустав справа', 'articulatio cubiti', 'A03.5.09.001', ['humerus','radius','ulna'], 'Сложный сустав с плечелоктевым, плечелучевым и проксимальным лучелоктевым сочленениями в общей капсуле.'),
          ('humeroulnar_joint', 'Плечелоктевой сустав справа', 'articulatio humeroulnaris', 'A03.5.09.002', ['humerus','ulna'], 'Сочленение блока плечевой кости с блоковидной вырезкой локтевой; часть локтевого сустава.'),
          ('humeroradial_joint', 'Плечелучевой сустав справа', 'articulatio humeroradialis', 'A03.5.09.003', ['humerus','radius'], 'Сочленение головки мыщелка плечевой кости с суставной ямкой головки лучевой; часть локтевого сустава.'),
          ('proximal_radioulnar_joint', 'Проксимальный лучелоктевой сустав справа', 'articulatio radioulnaris proximalis', 'A03.5.09.004', ['radius','ulna'], 'Сочленение окружности головки лучевой кости с лучевой вырезкой локтевой и кольцевой связкой; часть комплекса локтевого сустава.'),
          ('distal_radioulnar_joint', 'Дистальный лучелоктевой сустав справа', 'articulatio radioulnaris distalis', 'A03.5.10.001', ['radius','ulna'], 'Сочленение головки локтевой кости с локтевой вырезкой лучевой; суставной диск и связки необходимы для полного представления, костные поверхности их не заменяют.'),
        ]
        for key, ru, lat, code, owners, definition in joints:
            b = owners[0]; refs = [SOB_REF, DRUJ if key.startswith('distal') else PRUJ,
                ref('ta_joints', 'FIPAT / IFAA — TA98 joints', TA_JOINTS, code, 'official_list')]
            p = extra(b, key, ru, 'volume', definition, refs, anatomicalEntity='joint', educationCode=code,
                catalogueBones=[], anchors=[], relations=[dict(bone=x, role='component') for x in owners])
            p.update(lat=lat, nomenclatureStatus='TA98_term')
            if key not in ('elbow_joint','distal_radioulnar_joint'): p['partOf']='extra_humerus_elbow_joint'
            yield p

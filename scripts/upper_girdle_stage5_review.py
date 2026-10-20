"""Bilateral pectoral-girdle catalogue review; no coordinates or mesh edits."""
from copy import deepcopy

REPORT = 'research/stage5-upper-girdle-report-2026-10-18.md'
GRAY = 'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
SOBOTTA = 'https://archive.org/download/atlastextbookofh01sobouoft/atlastextbookofh01sobouoft_djvu.txt'
TA = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH894%20A2F%20EN.htm'
OWNERS = {'clavicle', 'clavicle_left', 'scapula', 'scapula_left'}

def ref(key, title, url, locator, access='full_text'):
    return dict(id='upper_girdle_'+key, title=title, url=url, locator=locator,
                access=access, checked='2026-10-18')

SCAP_REFS = [ref('gray_scapula', 'Gray / Lewis (1918) — The Scapula', GRAY,
    'PDF pp.179–187: Surfaces; Spine; Acromion; Borders; Angles; Coracoid Process; Ossification (non-union of acromion).'),
    ref('sobotta_scapula', 'Sobotta / McMurrich (1914), Vol. I — The Scapula', SOBOTTA,
        'Printed pp.83–84; text accompanying Figs.107–110. OCR text, illustrations not assessed here.'),
    ref('ncbi_scapula', 'Miniato, Mudreac, Borger — Anatomy, Thorax, Scapula (2023)',
        'https://www.ncbi.nlm.nih.gov/sites/books/NBK538319/', 'Structure and Function; Physiologic Variants.')]
CLAV_REFS = [ref('gray_clavicle', 'Gray / Lewis (1918) — The Clavicle', GRAY,
    'PDF pp.177–179: lateral third, medial two-thirds, sternal and acromial extremities.'),
    ref('ncbi_clavicle', 'La Rose, Charlick, Varacallo — Anatomy, Shoulder and Upper Limb, Clavicle (2026)',
        'https://www.ncbi.nlm.nih.gov/sites/books/NBK525990/', 'Introduction; Muscles; Figure 1 caption.')]
VARIANT_REFS = [ref('naidoo', 'Naidoo et al. (2014) — The variant course of the suprascapular artery',
    'https://pubmed.ncbi.nlm.nih.gov/24902100/', 'Abstract; PMID 24902100; DOI 10.5603/FM.2014.0030.', 'indexed_abstract'),
    ref('polguj', 'Polguj et al. — The variable morphology of suprascapular nerve and vessels at suprascapular notch',
        'https://pubmed.ncbi.nlm.nih.gov/24633009/', 'Abstract Results: arrangements above/below the ligament; PMID 24633009.', 'indexed_abstract')]

# Explicit entity-by-entity decisions, not name matching. "area" includes a
# bounded anatomical region; "line" is a path, not a claim of zero width.
SCAPULA = {
 2: ('area', 'Поверхность лопатки, обращённая к грудной клетке; включает подлопаточную ямку и участки у медиального края.'),
 3: ('area', 'Широкое вогнутое поле рёберной поверхности. Ямка и вся рёберная поверхность связаны, но не являются независимыми дублями одной точки.'),
 4: ('area', 'Задняя поверхность кости, разделённая остью на надостную и подостную области.'),
 5: ('volume', 'Костная пластинка на задней стороне лопатки, переходящая латерально в акромион; это весь отросток, а не только линия его гребня.'),
 6: ('volume', 'Костное возвышение на ости лопатки. Не следует смешивать с дельтовидной бугристостью плечевой кости или считать единственный маркер полной формой бугорка.'),
 7: ('area', 'Вогнутая область задней поверхности выше ости лопатки.'),
 8: ('area', 'Обширная область задней поверхности ниже ости лопатки.'),
 9: ('volume', 'Уплощённое латеральное продолжение ости, выступающее над суставной областью. Вариант os acromiale связан с несращением центра окостенения; его наличие в данной модели не установлено.'),
 10: ('area', 'Суставная площадка на медиальной стороне акромиона для акромиального конца ключицы. Принадлежит лопатке, а не обеим костям одновременно.'),
 11: ('point', 'Пальпируемый угловой ориентир перехода ости в акромион. Точечное представление обозначает место поворота края, не весь акромион.'),
 12: ('line', 'Медиальная граница лопатки между верхним и нижним углами. Полный путь края и ширина прилегающей зоны требуют отдельной разметки.'),
 13: ('line', 'Латеральная граница от области суставной впадины к нижнему углу; не вся прилежащая костная поверхность.'),
 14: ('line', 'Верхняя граница между верхним углом и основанием клювовидного отростка; включает участок вырезки.'),
 15: ('space', 'Вырезка верхнего края у основания клювовидного отростка. Верхняя поперечная связка замыкает проход надлопаточного нерва. Артерия обычно проходит над связкой, но описаны независимые наблюдения прохождения под ней. Это не постоянное отверстие только из кости.'),
 16: ('area', 'Угловая область соединения медиального и латерального краёв. Её протяжённость не заменяется единственным пином; уровень относительно рёбер не принят как калибровка этой модели.'),
 17: ('volume', 'Утолщённая латеральная часть лопатки, несущая суставную впадину; отличается от самой суставной поверхности.'),
 18: ('area', 'Угловая область соединения верхнего и медиального краёв. Не доказанная точка фиксированного уровня грудной клетки.'),
 19: ('area', 'Вогнутая суставная поверхность для головки плечевой кости. Здесь выделяется костная поверхность, не объём плечевого сустава и не мягкотканная суставная губа.'),
 20: ('volume', 'Костное возвышение над суставной впадиной; отдельно от её суставной поверхности.'),
 21: ('volume', 'Костное возвышение ниже суставной впадины у верхней части латерального края.'),
 22: ('volume', 'Суженная костная часть вокруг основания суставной области, соединяющая её с остальной лопаткой.'),
 23: ('volume', 'Изогнутый костный отросток, отходящий от верхней части лопатки и направляющийся вперёд; его форма не сводится к вершине.'),
}
CLAVICLE = {
 2: ('volume', 'Медиальный утолщённый конец ключицы; отличается от покрывающей его суставной площадки.'),
 3: ('area', 'Суставная площадка грудинного конца. Грудино-ключичное соединение включает рукоятку, первый рёберный хрящ и внутрисуставной диск; костные поверхности не изображают все эти ткани.'),
 4: ('area', 'Шероховатое вдавление нижней поверхности у грудинного конца для рёберно-ключичной связки; нужна область, а не произвольный центр.'),
 5: ('volume', 'Тело ключицы между её концами, изогнутое в горизонтальной плоскости; медиальная часть выпукла вперёд, латеральная — в противоположную сторону.'),
 6: ('line', 'Продольная борозда нижней стороны тела. Линия задаёт требуемый путь борозды; её ширина и область прикрепления подключичной мышцы отдельно не размечены.'),
 7: ('volume', 'Уплощённый латеральный конец ключицы, соединяющийся с акромионом лопатки.'),
 8: ('area', 'Суставная площадка латерального конца для акромиона. Площадка принадлежит ключице; общий сустав представлен отдельно.'),
 9: ('area', 'Шероховатая область нижней стороны латеральной части ключицы, включающая конусовидный бугорок и трапециевидную линию.'),
 10: ('volume', 'Костное возвышение нижней поверхности у заднего края латеральной части, служащее местом прикрепления конусовидной связки.'),
 11: ('line', 'Костный гребень, идущий от конусовидного бугорка вперёд и латерально; место прикрепления трапециевидной связки.'),
}

def _limitations(p):
    kind = p['geometryKind']
    needed = ('Идентифицированный исходник, ракурсы и независимая анатомическая приёмка точки.' if kind == 'point' else
        'Размеченные на идентифицированном образце границы/маска структуры, ракурсы и анатомическая приёмка; для сустава также мягкие ткани.')
    p['geometryRequirements'] = dict(status='unverified_extent', neededEvidence=needed)
    p['geometryReview'] = dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT)
    p['modelNote'] = ('Исходный маркер сохранён; близость к мешу не подтверждает анатомическую локализацию. ' if p.get('p') else
        'Подтверждённой координаты нет; точка с противоположной стороны не переносилась. ') + needed
    p['educationAvailable'] = False
    p['upperGirdleReview'] = dict(source=REPORT, scope='catalogue_and_representation', geometryAccepted=False)
    return p

def review(record):
    if record.get('b') not in OWNERS or record.get('t') != 'ta':
        return record
    p = deepcopy(record)
    scap = p['b'].startswith('scapula'); number = int(p['c'].split('.')[-1])
    kind, definition = (SCAPULA if scap else CLAVICLE)[number]
    p.update(geometryKind=kind, geometryKindReason=definition, anatomicalDefinition=definition,
             x=definition, side='left' if p['b'].endswith('_left') else 'right')
    old = p.get('refs', [])
    refs = [ref('ta98', 'FIPAT / IFAA — TA98', TA, p['c'], 'official_list')]
    refs += SCAP_REFS if scap else CLAV_REFS
    if scap and number == 15: refs += VARIANT_REFS
    p['refs'] = old + [deepcopy(r) for r in refs if r['url'] not in {o['url'] for o in old}]
    if scap and number in (3, 7, 8):
        parent = {3:2, 7:4, 8:4}[number]
        p['partOf'] = ('context_scapula_left_A02_4_01_'+str(parent).zfill(3) if p['side']=='left' else
                       {2:'sca_facies_costalis', 4:'sca_facies_posterior'}[parent])
    if (scap and number == 10) or (not scap and number == 8):
        p['relatedLandmarks'] = ['extra_clavicle'+('_left' if p['side']=='left' else '')+'_acromioclavicular_joint']
    return _limitations(p)

def additional_records(bones):
    for side, suffix in [('right', ''), ('left', '_left')]:
        b = 'scapula'+suffix; label = 'слева' if suffix else 'справа'
        if b in bones:
            definition = 'Проход между латеральной частью ости и суставной областью лопатки, соединяющий надостную и подостную ямки. Английское название spinoglenoid notch; у Gray — great scapular notch. Отличается от вырезки верхнего края у клювовидного отростка.'
            yield _limitations(dict(id='extra_'+b+'_spinoglenoid_notch', b=b, t='additional',
                ru='Вырезка между остью и суставной областью лопатки '+label, lat='', x=definition,
                geometryKind='space', geometryKindReason=definition, p=None, n=None, m=[], side=side,
                g='Дополнительные образования', nomenclatureStatus='descriptive_term_without_assigned_TA98_code',
                refs=deepcopy([SCAP_REFS[0], SCAP_REFS[2]])))
        b = 'clavicle'+suffix
        if b in bones:
            definition = 'Сустав между акромиальным концом ключицы и акромионом лопатки. Это составное суставное образование, а не новая кость и не объединённая суставная площадка. Полная геометрия включает хрящи, капсулу и вариабельный диск; костные меши её не заменяют.'
            refs = deepcopy([CLAV_REFS[0], SCAP_REFS[1], CLAV_REFS[1]]) + [ref('disc_variation',
                'Musil et al. (2018) — A proposal for the extension of locomotor system nomenclature',
                'https://ifaa.unifr.ch/Public/TNAEntryPage/ref/Musil2018.pdf',
                'PDF p.4 / printed p.120, Juncturae; Systema articulare: AC disc is not invariably present. No frequency transferred to this specimen.'), ref('ta98_ac',
                'FIPAT / IFAA — TA98, Articulatio acromioclavicularis',
                'https://ifaa.unifr.ch/Public/EntryPage/TAH1434%20Part98A3%20EN.htm', 'A03.5.03.001', 'official_list')]
            yield _limitations(dict(id='extra_'+b+'_acromioclavicular_joint', b=b, t='additional',
                ru='Акромиально-ключичный сустав '+label, lat='articulatio acromioclavicularis', x=definition,
                geometryKind='volume', geometryKindReason=definition, anatomicalEntity='joint',
                p=None, n=None, m=[], side=side, g='Общие суставные образования', refs=refs,
                educationCode='A03.5.03.001', nomenclatureStatus='TA98_term', catalogueBones=[], anchors=[],
                relations=[dict(bone=owner, role='component', refs=[r['id'] for r in refs]) for owner in (b, 'scapula'+suffix)]))

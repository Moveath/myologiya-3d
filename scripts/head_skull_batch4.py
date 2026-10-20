"""Addressed sphenoid and temporal-squama display extents, not new geometry.

Each decision concerns the existing anatomical definition and source scope.
Neither the spelling of a term nor a surface anchor determines its type.
"""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL, OXFORD_URL

GULYA_URL = 'https://api.pageplace.de/preview/DT0400.9780849375989_A24589274/preview-9780849375989_A24589274.pdf'
MCF_URL = 'https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2023.1132774/full'
PALACKY_URL = 'https://www.atlascloveka.upol.cz/cs/cs02/cs0201/cs020114.html'

def source(key, title, url, locator, group):
    return _ref('batch4_'+key, title, url, locator, group, scope='representation', access='text')

GRAY_BODY = source('gray_body', 'Gray / Lewis, Anatomy of the Human Body (1918)', GRAY_URL+'#page=102',
    'PDF pp.102–105: Body, surfaces; distinguish depression, plate and projection. No dimensions transferred.', 'gray_lewis_1918')
OXFORD_BODY = source('oxford_body', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)', OXFORD_URL,
    'Printed pp.40–41 / PDF pp.59–60: body and its superior, lateral, anterior and inferior features.', 'van_gijn_dunne')
GRAY_WINGS = source('gray_wings', 'Gray / Lewis, Anatomy of the Human Body (1918)', GRAY_URL+'#page=105',
    'PDF pp.105–108: greater/lesser wings, pterygoid plates, notches, fossae and hamulus.', 'gray_lewis_1918')
MCF = source('mcf', 'Tayebi Meybodi et al. Comprehensive microsurgical anatomy of the middle cranial fossa, Part I (2023)', MCF_URL,
    'Anterior clinoid process; Middle fossa foramina (rotundum, ovale, spinosum, Vesalius, canaliculus innominatus). DOI 10.3389/fsurg.2023.1132774. No population dimensions or symmetry assumed for this specimen.', 'tayebi_meybodi_2023')
PALACKY = source('palacky_sphenoid', 'Libor Luňáček, Palacký University — Neurocranium', PALACKY_URL,
    'Os sphenoidale: greater/lesser wings and pterygoid plates. Used only for these named structures; erroneous heading calling the sphenoid paired is rejected.', 'lunacek_palacky')
GRAY_TEMPORAL = source('gray_temporal', 'Gray / Lewis, Anatomy of the Human Body (1918)', GRAY_URL+'#page=90',
    'PDF pp.90–93: squama surfaces, zygomatic process, articular eminence, mandibular fossa, borders; pp.98–99: fissures and suprameatal spine.', 'gray_lewis_1918')
OXFORD_TEMPORAL = source('oxford_temporal', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)', OXFORD_URL,
    'Printed pp.22–28 / PDF pp.41–47: squamous/tympanic parts, mandibular fossa and Fig.1.12. Do not adopt the conflation of supramastoid crest with Henle spine.', 'van_gijn_dunne')
GULYA = source('gulya', "Aina Julianna Gulya. Gulya and Schuknecht’s Anatomy of the Temporal Bone with Surgical Implications, 3rd ed. (2007)", GULYA_URL,
    'Printed pp.1–4 / PDF pp.22–25: squama, mastoid fossa, suprameatal spine, photos A–E and junctions of temporal components. Title/copyright checked; a publisher preview, not the entire book.', 'gulya_schuknecht')

# Explicit per-code decisions. Existing sources remain attached in all cases.
SPHENOID = {
  2: ('volume', 'Тело включает костное вещество и стенки пазух; наружная поверхность не представляет его целиком.', 'body'),
  5: ('area', 'Проверяется поверхность поперечной предперекрёстной борозды, а не объём перекрёста или ось его хода.', 'body'),
  6: ('area', 'В существующей карточке седло определено как область верхней поверхности тела; его костные границы и гипофиз не заменяются одной точкой.', 'body'),
  7: ('volume', 'Бугорок седла — костное возвышение; линия его верхнего края не охватывает весь рельеф.', 'body'),
  8: ('volume', 'Средний наклонённый отросток — костный выступ, отдельно от связки и возможного замкнутого кольца.', 'body'),
  9: ('area', 'Карточка обозначает углублённую костную поверхность гипофизарной ямки, не объём гипофиза.', 'body'),
 10: ('volume', 'Спинка седла представляет пластинку со сторонами и толщиной, не только её заднюю поверхность.', 'body'),
 11: ('volume', 'Задний наклонённый отросток имеет костный объём; вершина не заменяет весь отросток.', 'body'),
 12: ('area', 'Сонная борозда обозначает костное ложе; просвет артерии и кавернозного синуса в этот тип не включаются.', 'body'),
 13: ('volume', 'Язычок — костное возвышение у борозды, а не сама борозда или условная точка.', 'body'),
 14: ('volume', 'Рассматривается рельеф клиновидного гребня, а не только линия соединения с решётчатой костью.', 'body'),
 15: ('volume', 'Клюв — выступающее костное продолжение, отдельно от охватывающих его крыльев сошника.', 'body'),
 17: ('volume', 'Межпазушная перегородка — костная пластинка; её срединное положение и симметрия на образце не предполагаются.', 'body'),
 18: ('space', 'Апертура — вход в пазуху; её отверстие не подменяет всю полость или полный край.', 'body'),
 19: ('volume', 'Клиновидная раковина — тонкая костная пластинка, а не носовой ход.', 'body'),
 20: ('volume', 'Малое крыло включает верхнюю/нижнюю поверхности и соединения с телом; одно из них не заменяет всю часть.', 'wings'),
 22: ('volume', 'Передний наклонённый отросток — костное продолжение малого крыла, отдельно от зрительного канала.', 'clinoid'),
 24: ('volume', 'Большое крыло охватывает костное вещество нескольких поверхностей; оно не равно одной глазничной поверхности.', 'wings'),
 28: ('volume', 'Подвисочный гребень здесь является костным рельефом между двумя поверхностями; его ось была бы лишь частью представления.', 'wings'),
 35: ('space', 'Круглое отверстие представляется проходом, не произвольной точкой его костного края.', 'foramina'),
 36: ('space', 'Овальное отверстие — проход основания; форма просвета и его размеры на GLB отдельно не приняты.', 'foramina'),
 37: ('space', 'Венозное отверстие — вариабельный проход; тип не подтверждает наличие, число или симметрию на этой модели.', 'variant'),
 38: ('space', 'Остистое отверстие обозначает проход через кость; маркер не определяет обе апертуры и полный просвет.', 'foramina'),
 39: ('space', 'Каменистое отверстие рассматривается как вариабельный проход, а не часть каменистой височной кости по созвучию.', 'variant'),
 40: ('volume', 'Ость клиновидной кости — выступ большого крыла, не отдельная точка прикрепления.', 'wings'),
 41: ('area', 'Собственная борозда клиновидной кости — участок костного ложа слуховой трубы; не вся труба и не клиновидно-каменистая щель.', 'auditory'),
 42: ('volume', 'Крыловидный отросток включает обе пластинки и их костное соединение, не только контур.', 'wings'),
 43: ('volume', 'Латеральная пластинка имеет две поверхности и толщину; её мышечные области остаются раздельными.', 'wings'),
 44: ('volume', 'Медиальная пластинка — костная часть с поверхностями; крючок и вырезка не заменяют её целиком.', 'wings'),
 45: ('space', 'Вырезка — промежуток между нижними отделами пластинок; соединение с нёбной костью не превращает её в дубликат всей общей ямки.', 'wings'),
 46: ('space', 'Крыловидная ямка в этой карточке — открытое пространство между расходящимися пластинками, не вся поверхность одной пластинки.', 'existing'),
 47: ('area', 'Ладьевидная ямка — локальное неглубокое костное ложе; не самостоятельный канал.', 'existing'),
 48: ('volume', 'Влагалищный отросток — костная пластинка у медиальной крыловидной пластинки; он отделён от соседних каналов.', 'body'),
 49: ('area', 'Проверяется собственная борозда на влагалищном отростке; полный нёбно-влагалищный канал требует второй костной стенки.', 'existing'),
 50: ('area', 'Рассматривается местная борозда у соединения с сошником; это не весь сошниково-влагалищный канал.', 'existing'),
 51: ('volume', 'Крыловидный крючок — изогнутый костный выступ; его борозда для сухожилия является отдельным термином.', 'wings'),
}
TEMPORAL = {
 61: ('volume', 'Чешуйчатая часть — костная пластинка с наружной и внутренней поверхностями, не одна из этих поверхностей.'),
 62: ('line', 'Представляется ход верхнего края чешуи; собственный край кости не равен целому межкостному шву.'),
 64: ('line', 'Представляется собственный передний край чешуи; это не весь клиновидно-чешуйчатый шов.'),
 65: ('area', 'Наружная сторона чешуи — поверхность, отличная от пространства всей височной ямки.'),
 66: ('area', 'Борозда средней височной артерии — костное ложе, не просвет артерии или её осевая линия.'),
 67: ('volume', 'Скуловой отросток включает корни и костный объём; вся скуловая дуга дополнительно имеет скуловой вклад.'),
 68: ('volume', 'Надсосцевидный гребень — рельеф продолжения заднего корня, не надпроходная ость и не условный пин.'),
 69: ('area', 'Надпроходная ямочка — участок углублённой поверхности; это не сама полость сосцевидной пещеры.'),
 70: ('volume', 'Надпроходная ость — самостоятельный костный выступ; не весь надсосцевидный гребень.'),
 71: ('area', 'Нижнечелюстная ямка здесь — костное углубление; её задний несуставной участок не становится суставной поверхностью.'),
 72: ('area', 'Суставная область выделяется как часть костной поверхности; диск, капсула и всё пространство ВНЧС сюда не включены.'),
 73: ('volume', 'Суставной бугорок — костное возвышение перед ямкой; его суставная поверхность не равна всему костному объёму.'),
 74: ('space', 'Каменисто-барабанная щель — узкое сообщение, отдельно от соседних линий соединения частей и канальца барабанной струны.'),
 75: ('line', 'Для существующего определения соединения каменистой и чешуйчатой частей требуется линия стыка; открытый просвет на всём протяжении не предполагается.'),
 76: ('line', 'Карточка описывает границу барабанной и чешуйчатой частей одной кости; это линия соединения, не общий ориентир двух разных костей.'),
 77: ('line', 'Карточка описывает границу барабанной и сосцевидной частей одной кости; линия стыка не доказывает весь ход выходящего канальца.'),
 78: ('area', 'Внутренняя поверхность чешуи не равна всему объёму чешуйчатой части или всей средней черепной ямке.'),
}

def reviewed_decisions():
    result = {('sphenoid', f'A02.1.05.{n:03d}'): dict(kind=k, reason=r, group=g)
              for n, (k, r, g) in SPHENOID.items()}
    result.update({('temporal_'+side, f'A02.1.06.{n:03d}'): dict(kind=k, reason=r, group='temporal')
                   for side in ('right', 'left') for n, (k, r) in TEMPORAL.items()})
    return result

def decision_sources(record, decision):
    group = decision['group']
    if group == 'body': return (GRAY_BODY, OXFORD_BODY)
    if group == 'wings': return (GRAY_WINGS, PALACKY)
    if group == 'clinoid': return (GRAY_WINGS, MCF)
    if group == 'foramina': return (GRAY_WINGS, MCF)
    if group == 'variant': return (MCF,)  # Independent Palamenghi record already retained.
    if group == 'auditory': return (GRAY_WINGS, OXFORD_TEMPORAL)
    if group == 'existing': return ()  # Existing address-specific source pair reused; see review artifact.
    n = int(record['c'].rsplit('.', 1)[1])
    if n in (69, 70, 76, 77): return (GRAY_TEMPORAL, GULYA)
    if n in (62, 64, 78): return (GRAY_TEMPORAL, GULYA)
    if n == 75: return (GRAY_TEMPORAL, MCF)
    return (GRAY_TEMPORAL, OXFORD_TEMPORAL)

def apply_record_review(record):
    decision = reviewed_decisions().get((record['b'], record['c']))
    if not decision: return
    assert record['geometryKind'] == decision['kind']
    record['geometryReview'] = dict(
        status='representation_reviewed', rationale=decision['reason'],
        source='research/stage5-skull-batch4-2026-10-16/geometry-kind-review.json',
        coordinateAcceptance=False, extentAcceptance=False)
    record['refs'].extend(deepcopy(list(decision_sources(record, decision))))
    if record['b'] == 'sphenoid':
        record['modelNote'] += ' Тип представления не подтверждает форму на данной модели. Для парных образований одиночный маркер не подтверждает обе стороны; новые координаты и контуры не создавались.'
    else:
        record['modelNote'] += ' Тип представления уточнён для этой стороны; полная область или линия на сетке не размечена и по одному маркеру не принимается.'

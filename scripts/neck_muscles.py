"""Editorial neck muscle cards; factual summaries, not copied atlas prose.

Depths are interface groups. Evidence describes typical anatomy, never a
geometrical validation of BodyParts3D. Terminology: TA98 / Kolesnikov 2003,
pp. 44–47. No clinical advice or surgical measurements are included.
"""
from head_terms import BOOK_URL

IFAA = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1730%20A2F%20EN.htm'
IFAA_BACK = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1770%20A2F%20EN.htm'
KH = 'https://www.kenhub.com/en/library/anatomy/'
LOYOLA = 'https://www.stritch.luc.edu/lumen/meded/grossanatomy/homepage/muscletables/head-neckmuscletable.pdf'
UAMS = 'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-head-and-neck/'
BACK = UAMS.replace('muscles-of-the-head-and-neck/', 'muscles-of-the-back-region/')
GRAY = 'https://www.wikimd.org/wiki/'
GRAY_HYOID = GRAY + 'The_Supra-_and_Infrahyoid_Muscles'
GRAY_PRE = GRAY + 'The_Anterior_Vertebral_Muscles'
GRAY_BACK = GRAY + 'The_Deep_Muscles_of_the_Back'
GRAY_SUB = GRAY + 'The_Suboccipital_Muscles'
GRAY_SHOULDER = GRAY + 'The_Muscles_Connecting_the_Upper_Extremity_to_the_Vertebral_Column'
POLLAK = 'https://www.bjbms.org/ojs/index.php/bjbms/article/download/10787/3480/99389'
MACCHI = 'https://pubmed.ncbi.nlm.nih.gov/24438810/'
DSA_STUDY = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10183034/'
OPENSTAX = 'https://openstax.org/books/anatomy-and-physiology-2e/pages/11-3-axial-muscles-of-the-head-neck-and-back'

MUSCLE_TEMPLATES = {}
EVIDENCE = {}

def ref(url, locator):
    title = ('Gray, 1918: открытый текст' if 'wikimd' in url else
             'Loyola University Chicago: таблица мышц' if 'luc.edu' in url else
             'UAMS: таблица мышц' if 'uams.edu' in url else
             'Pollak et al., 2025: сосуды ременной мышцы головы' if url==POLLAK else
             'Macchi et al., 2014: сосуды подзатылочной области' if url==MACCHI else
             'Origin variations and brachial plexus relationship of the dorsal scapular artery, 2023' if url==DSA_STUDY else
             'OpenStax: Anatomy and Physiology 2e' if url==OPENSTAX else
             'Kenhub: открытая статья')
    return dict(url=url, title=title, locator=locator)

def add(key, ru, lat, code, o, i, a, n, s, *, group, depth=2, view='antlat',
        slug=None, second=GRAY_HYOID, locator=None, blood=LOYOLA, blood_locator=None,
        note='', parts=None, overrides=None):
    page = KH + (slug or key.replace('_','-')+'-muscle')
    second_ref = ref(second, locator or (lat + ': описание; Nerves; Actions'))
    fieldrefs = {}
    for field, section in [('o','Origin and insertion'),('i','Origin and insertion'),
                           ('a','Function / Actions'),('n','Innervation')]:
        fieldrefs[field] = [ref(page, section), second_ref.copy()]
    fieldrefs['s'] = [ref(page, 'Blood supply'), ref(blood, blood_locator or (lat + ', столбец Blood supply'))]
    if overrides: fieldrefs.update(overrides)
    muscle = dict(ru=ru,lat=('platysma' if lat=='platysma' else 'm. '+lat),code=code,
                  g=group,d=depth,v=view,L={1:'Поверхностный слой',2:'Средний слой',3:'Глубокий слой'}[depth],
                  o=o,i=i,a=a,n=n,s=s,note=note,fieldRefs=fieldrefs)
    if parts: muscle['parts']=parts
    refs = list({(r['url'],r['locator']):r for rr in fieldrefs.values() for r in rr}.values())
    refs += [dict(title='TA98: номенклатура',url=IFAA_BACK if code.startswith('A04.3') else IFAA,locator=code),
             dict(title='Колесников, 2003',url=BOOK_URL,locator='С. 44–47; '+code)]
    muscle['refs']=refs
    MUSCLE_TEMPLATES[key]=muscle
    EVIDENCE[key]=dict(code=code, fields=fieldrefs, checked='2026-10-13',
                       scope='whole_muscle', geometryValidated=False, note=note)

FACIAL='Шейная ветвь лицевого нерва (r. colli n. facialis, VII).'
ANSA='Шейная петля (ansa cervicalis), волокна передних ветвей шейных нервов.'
ANT='Передние ветви шейных спинномозговых нервов (rr. anteriores nervorum cervicalium).'
POST='Задние ветви шейных спинномозговых нервов (rr. posteriores nervorum cervicalium).'
SUB='Подзатылочный нерв (n. suboccipitalis): задняя ветвь C1.'
SUPTH='Ветви верхней щитовидной артерии (a. thyroidea superior).'
ASC='Ветви восходящей шейной артерии (a. cervicalis ascendens).'
OCC='Ветви затылочной артерии (a. occipitalis).'
DEEP='Ветви глубокой шейной артерии (a. cervicalis profunda).'

add('platysma','Подкожная мышца шеи','platysma','A04.2.01.001',
    'Фасция над верхними отделами большой грудной и дельтовидной мышц.',
    'Нижняя челюсть и мягкие ткани нижней части лица.',
    'Натягивает кожу шеи; помогает опускать нижнюю челюсть и угол рта.',FACIAL,
    'Подподбородочная и надлопаточная артерии (aa. submentalis et suprascapularis).',
    group='neck_superficial',depth=1,slug='the-platysma',second=GRAY+'The_Lateral_Cervical_Muscles',
    locator='Platysma; Nerve; Actions',blood_locator='С. 2, Platysma')
add('sternocleidomastoid','Грудино-ключично-сосцевидная мышца','sternocleidomastoideus','A04.2.01.008',
    'Рукоятка грудины и медиальная треть ключицы.',
    'Сосцевидный отросток и латеральная часть верхней выйной линии.',
    'С одной стороны наклоняет шею к себе и поворачивает лицо в противоположную сторону; с двух сторон участвует в сгибании шеи.',
    'Добавочный нерв (n. accessorius, XI); ветви шейного сплетения.',SUPTH,
    group='neck_superficial',depth=1,second=UAMS,locator='Строка sternocleidomastoid; Origin, Insertion, Action, Innervation',
    blood_locator='С. 3, Sternocleidomastoid',
    note='Грудинная и ключичная головки не выделены отдельными сетками исходной модели.')

add('digastric','Двубрюшная мышца','digastricus','A04.2.03.002',
    'Переднее брюшко — двубрюшная ямка нижней челюсти; заднее — сосцевидная вырезка височной кости.',
    'Промежуточное сухожилие, соединённое фиброзной петлёй с подъязычной костью.',
    'Поднимает подъязычную кость; при её фиксации помогает опускать нижнюю челюсть.',
    'Переднее брюшко — n. mylohyoideus (V3); заднее — n. facialis (VII).',
    'Переднее брюшко — a. submentalis; заднее — a. occipitalis.',group='neck_suprahyoid',
    blood_locator='С. 4, Digastric',parts={
      'anterior':dict(ru='Переднее брюшко',lat='venter anterior',code='A04.2.03.003',o='Двубрюшная ямка нижней челюсти.',i='Промежуточное сухожилие.',n='Челюстно-подъязычный нерв (n. mylohyoideus, V3).',x='Брюшко соединяется с подъязычной костью через сухожилие и фиброзную петлю.'),
      'posterior':dict(ru='Заднее брюшко',lat='venter posterior',code='A04.2.03.004',o='Сосцевидная вырезка височной кости.',i='Промежуточное сухожилие.',n='Двубрюшная ветвь лицевого нерва (VII).',x='Брюшко соединяется с подъязычной костью через сухожилие и фиброзную петлю.')})
add('stylohyoid','Шилоподъязычная мышца','stylohyoideus','A04.2.03.005',
    'Шиловидный отросток височной кости.', 'Тело подъязычной кости у основания большого рога.',
    'Поднимает подъязычную кость и тянет её назад.','Шилоподъязычная ветвь лицевого нерва (VII).',
    'Ветви лицевой и затылочной артерий (aa. facialis et occipitalis).',group='neck_suprahyoid',blood_locator='С. 4, Stylohyoid')
add('mylohyoid','Челюстно-подъязычная мышца','mylohyoideus','A04.2.03.006',
    'Челюстно-подъязычная линия нижней челюсти.', 'Срединный шов и тело подъязычной кости.',
    'Поднимает дно полости рта и подъязычную кость; при фиксации последней помогает опускать нижнюю челюсть.',
    'Челюстно-подъязычный нерв (n. mylohyoideus), ветвь нижнего альвеолярного нерва (V3).',
    'Подъязычная и подподбородочная артерии (aa. sublingualis et submentalis).',group='neck_suprahyoid',depth=3,blood_locator='С. 4, Mylohyoid')
add('geniohyoid','Подбородочно-подъязычная мышца','geniohyoideus','A04.2.03.007',
    'Нижняя подбородочная ость нижней челюсти.', 'Тело подъязычной кости.',
    'Тянет подъязычную кость вверх и вперёд; при её фиксации помогает опускать нижнюю челюсть.',
    'Волокна C1, идущие вместе с подъязычным нервом (n. hypoglossus).',
    'Подъязычная артерия (a. sublingualis).',group='neck_suprahyoid',depth=3,blood_locator='С. 4, Geniohyoid',
    overrides={'n':[ref(KH+'geniohyoid-muscle','Innervation'),ref(LOYOLA,'С. 4, Geniohyoid, Innervation')]})
add('sternohyoid','Грудино-подъязычная мышца','sternohyoideus','A04.2.04.002',
    'Задняя поверхность рукоятки грудины и медиального конца ключицы.', 'Нижний край тела подъязычной кости.',
    'Опускает подъязычную кость.',ANSA,SUPTH,group='neck_infrahyoid',blood_locator='С. 2, Sternohyoid')
add('omohyoid','Лопаточно-подъязычная мышца','omohyoideus','A04.2.04.003',
    'Нижнее брюшко — верхний край лопатки; верхнее — промежуточное сухожилие.',
    'Нижнее брюшко — промежуточное сухожилие; верхнее — тело подъязычной кости.',
    'Опускает и оттягивает назад подъязычную кость.',ANSA,SUPTH,group='neck_infrahyoid',blood_locator='С. 2, Omohyoid',
    note='В модели мышца дана целиком. Брюшки описаны отдельно, но не являются отдельными исходными сетками.',parts={
      'superior':dict(ru='Верхнее брюшко',lat='venter superior',code='A04.2.04.004',o='Промежуточное сухожилие.',i='Нижний край тела подъязычной кости.',noModel=True,x='Отдельная модель брюшка отсутствует; показана мышца целиком.'),
      'inferior':dict(ru='Нижнее брюшко',lat='venter inferior',code='A04.2.04.005',o='Верхний край лопатки медиальнее её вырезки.',i='Промежуточное сухожилие.',noModel=True,x='Отдельная модель брюшка отсутствует; показана мышца целиком.')})
add('sternothyroid','Грудино-щитовидная мышца','sternothyroideus','A04.2.04.006',
    'Задняя поверхность рукоятки грудины и хрящ I ребра.', 'Косая линия щитовидного хряща.',
    'Опускает щитовидный хрящ и гортань.',ANSA,SUPTH,group='neck_infrahyoid',depth=3,blood_locator='С. 2, Sternothyroid')
add('thyrohyoid','Щитоподъязычная мышца','thyrohyoideus','A04.2.04.007',
    'Косая линия щитовидного хряща.', 'Нижний край тела и большого рога подъязычной кости.',
    'Опускает подъязычную кость; при её фиксации поднимает гортань.',
    'Волокна C1, проходящие с подъязычным нервом (n. hypoglossus).',SUPTH,
    group='neck_infrahyoid',depth=3,second=LOYOLA,locator='С. 2, Thyrohyoid',blood_locator='С. 2, Thyrohyoid')

for key,ru,code,o,i,a in [
 ('scalenus_anterior','Передняя лестничная мышца','004','Передние бугорки поперечных отростков C3–C6.','Бугорок передней лестничной мышцы на I ребре.','Наклоняет шею в свою сторону; поднимает I ребро при фиксированной шее.'),
 ('scalenus_medius','Средняя лестничная мышца','005','Поперечные отростки C2–C7.','Верхняя поверхность I ребра позади борозды подключичной артерии.','Наклоняет шею в свою сторону; поднимает I ребро при фиксированной шее.'),
 ('scalenus_posterior','Задняя лестничная мышца','006','Задние бугорки нижних шейных поперечных отростков; часто C5–C7.','Наружная поверхность II ребра.','Наклоняет шею в свою сторону; поднимает II ребро при фиксированной шее.')]:
    note={'scalenus_anterior':'Сегментарные уровни иннервации различаются: Kenhub — C4–C6, UAMS — C5–C7, Loyola — C5–C8; единый узкий диапазон не заявлен.',
          'scalenus_medius':'Верхняя граница начала варьирует в описаниях: Gray и UAMS — C2, Kenhub также указывает C1. Это не признак ошибки конкретной сетки.',
          'scalenus_posterior':'Начало описывают как C5–C7 (UAMS; основной текст Kenhub) или C4–C6 (Loyola; таблица Kenhub). Приведена типичная область, а не неизменный для всех людей уровень.'}[key]
    add(key,ru,key.replace('_',' '),'A04.2.01.'+code,o,i,a,ANT,ASC,
        group='neck_scalene',depth=3,slug='scalene-muscles',second=GRAY+'The_Lateral_Vertebral_Muscles',
        locator=key.replace('_',' ')+'; Nerves; Actions',blood_locator='С. 4, Scalene ('+code+')',note=note)
    MUSCLE_TEMPLATES[key]['refs'] += [ref(UAMS,'Строка '+key.replace('_',' ')),ref(LOYOLA,'С. 4, Scalene')]

add('longus_colli','Длинная мышца шеи','longus colli','A04.2.01.002',
    'Тела C5–T3 и передние бугорки поперечных отростков C3–C5; состав по частям приведён ниже.',
    'Передний бугорок атланта, тела C2–C4 и передние бугорки поперечных отростков C5–C6.',
    'Сгибает шею; при одностороннем сокращении участвует в её наклоне и повороте.',ANT,
    'Ветви позвоночной и восходящей глоточной артерий (aa. vertebralis et pharyngea ascendens).',
    group='neck_prevertebral',depth=3,second=GRAY_PRE,blood_locator='С. 4, Longus colli',
    note='Источники приводят разные диапазоны иннервации: Kenhub C2–C6, Gray C2–C7, Loyola C2–C8. Названия трёх частей — описательные, отдельных кодов частей в данном списке TA98 нет.',parts={
      'superior_oblique':dict(ru='Верхняя косая часть',lat='pars obliqua superior',o='Передние бугорки поперечных отростков C3–C5.',i='Передний бугорок атланта.',x='Описательное деление длинной мышцы шеи; не отдельная мышца TA98.'),
      'vertical':dict(ru='Вертикальная часть',lat='pars verticalis',o='Передние поверхности тел C5–T3.',i='Передние поверхности тел C2–C4.',x='Описательное деление длинной мышцы шеи; не отдельная мышца TA98.'),
      'inferior_oblique':dict(ru='Нижняя косая часть',lat='pars obliqua inferior',o='Передние поверхности тел T1–T3.',i='Передние бугорки поперечных отростков C5–C6.',x='Описательное деление длинной мышцы шеи; не отдельная мышца TA98.')})
add('longus_capitis','Длинная мышца головы','longus capitis','A04.2.01.003',
    'Передние бугорки поперечных отростков C3–C6.', 'Базилярная часть затылочной кости.',
    'Сгибает голову.',ANT,ASC,group='neck_prevertebral',depth=3,second=GRAY_PRE,blood_locator='С. 4, Longus capitis')
add('rectus_capitis_anterior','Передняя прямая мышца головы','rectus capitis anterior','A04.2.02.002',
    'Передняя поверхность латеральной массы атланта и основание его поперечного отростка.',
    'Нижняя поверхность базилярной части затылочной кости.', 'Сгибает голову.',
    'Передние ветви C1–C2.', 'Ветви позвоночной и восходящей глоточной артерий.',
    group='neck_prevertebral',depth=3,second=GRAY_PRE,blood_locator='С. 4, Rectus capitis anterior')
add('rectus_capitis_lateralis','Латеральная прямая мышца головы','rectus capitis lateralis','A04.2.02.003',
    'Верхняя поверхность поперечного отростка атланта.', 'Яремный отросток затылочной кости.',
    'Наклоняет голову в свою сторону.', 'Передние ветви C1–C2.',
    'Ветви позвоночной и восходящей глоточной артерий.',group='neck_prevertebral',depth=3,
    second=GRAY_PRE,blood_locator='С. 4, Rectus capitis lateralis')

for key,ru,code,o,i,a in [
 ('rectus_capitis_posterior_major','Большая задняя прямая мышца головы','004','Остистый отросток осевого позвонка.','Латеральный участок нижней выйной линии затылочной кости.','Разгибает голову; при одностороннем сокращении поворачивает её в свою сторону.'),
 ('rectus_capitis_posterior_minor','Малая задняя прямая мышца головы','005','Задний бугорок атланта.','Медиальный участок нижней выйной линии затылочной кости.','Разгибает голову.'),
 ('obliquus_capitis_superior','Верхняя косая мышца головы','006','Поперечный отросток атланта.','Затылочная кость между верхней и нижней выйными линиями.','Разгибает голову и наклоняет её в свою сторону.'),
 ('obliquus_capitis_inferior','Нижняя косая мышца головы','007','Остистый отросток осевого позвонка.','Поперечный отросток атланта.','Поворачивает атлант и голову в свою сторону.')]:
    add(key,ru,key.replace('_',' '),'A04.2.02.'+code,o,i,a,SUB,OCC,
        group='neck_suboccipital',depth=3,view='post',second=GRAY_SUB,
        blood=BACK,blood_locator='Строка '+key.replace('_',' ')+', Artery')

add('splenius_capitis','Ременная мышца головы','splenius capitis','A04.3.02.103',
    'Нижняя часть выйной связки и остистые отростки C7–T3 (в описаниях также T4).',
    'Сосцевидный отросток и латеральный участок верхней выйной линии.',
    'С двух сторон разгибает голову и шею; с одной — наклоняет и поворачивает голову в свою сторону.',POST,
    OCC,group='neck_posterior',view='post',blood=POLLAK,blood_locator='С. 1351, Introduction, абзац о blood supply',
    second=GRAY_BACK,note='Границы начала зависят от источника: Gray — T3 или T4; Kenhub — T3. Сегментарная иннервация указана без спорного узкого диапазона.')
add('splenius_cervicis','Ременная мышца шеи','splenius cervicis','A04.3.02.104',
    'Остистые отростки T3–T6.', 'Поперечные отростки верхних шейных позвонков, обычно C1–C3.',
    'Разгибает шею; с одной стороны наклоняет и поворачивает её в свою сторону.',POST,DEEP,
    group='neck_posterior',view='post',second=GRAY_BACK,blood=BACK,blood_locator='Splenius cervicis, Artery')
add('iliocostalis_cervicis','Подвздошно-рёберная мышца шеи','iliocostalis cervicis','A04.3.02.009',
    'Углы III–VI рёбер.', 'Задние бугорки поперечных отростков C4–C6.',
    'Разгибает шею и наклоняет её в свою сторону.',POST,DEEP,group='neck_posterior',depth=3,view='post',
    slug='iliocostalis-muscle',second=GRAY_BACK,blood=BACK,blood_locator='Iliocostalis / Erector spinae, Artery')
add('longissimus_cervicis','Длиннейшая мышца шеи','longissimus cervicis','A04.3.02.013',
    'Поперечные отростки верхних грудных позвонков, обычно T1–T5.',
    'Задние бугорки поперечных отростков C2–C6.', 'Разгибает шею и наклоняет её в свою сторону.',POST,DEEP,
    group='neck_posterior',depth=3,view='post',slug='longissimus-muscle',second=GRAY_BACK,blood=BACK,blood_locator='Longissimus, Artery')
add('longissimus_capitis','Длиннейшая мышца головы','longissimus capitis','A04.3.02.014',
    'Поперечные отростки T1–T5 и отростки нижних шейных позвонков.', 'Сосцевидный отросток височной кости.',
    'Разгибает голову; с одной стороны наклоняет её в свою сторону.',POST,DEEP,
    group='neck_posterior',depth=3,view='post',slug='longissimus-muscle',second=GRAY_BACK,blood=BACK,blood_locator='Longissimus, Artery',
    note='Для шейного начала Gray называет суставные отростки нижних 3–4 позвонков, Kenhub — поперечные C4–C7. Расхождение сохранено; сетка сама по себе не разрешает его.')
add('spinalis_cervicis','Остистая мышца шеи','spinalis cervicis','A04.3.02.017',
    'Нижний отдел выйной связки и остистые отростки у перехода C7–T1.',
    'Остистый отросток C2; возможное распространение на C3–C4.', 'Разгибает шею.',POST,DEEP,
    group='neck_posterior',depth=3,view='post',slug='spinalis-muscle',second=GRAY_BACK,blood=BACK,blood_locator='Spinalis / Erector spinae, Artery',
    note='Границы прикреплений изменчивы; Gray отмечает непостоянство мышцы и возможное начало от T2, Kenhub — вариабельность её прикреплений.')
add('semispinalis_cervicis','Полуостистая мышца шеи','semispinalis cervicis','A04.3.02.208',
    'Поперечные отростки верхних 5–6 грудных позвонков.', 'Остистые отростки C2–C5.',
    'Разгибает шею; односторонне участвует в повороте в противоположную сторону.',POST,DEEP,
    group='neck_posterior',depth=3,view='post',second=GRAY_BACK,blood=BACK,blood_locator='Semispinalis, Artery')
add('semispinalis_capitis','Полуостистая мышца головы','semispinalis capitis','A04.3.02.209',
    'Отростки нижних шейных и верхних грудных позвонков.', 'Затылочная кость между выйными линиями.',
    'Разгибает голову и шею; односторонне участвует в повороте в противоположную сторону.',POST,
    OCC,group='neck_posterior',depth=3,view='post',blood=MACCHI,blood_locator='Abstract, Results: при отсутствии suboccipital artery of Salmon снабжение из occipital artery',
    second=GRAY_BACK,note='Gray описывает поперечные отростки C7 и T1–T6/T7, суставные C4–C6; Kenhub — суставные C4–C7 и поперечные T1–T6. Точные границы начала различаются.')

# These are regional views of the same named muscles, not extra muscles in a
# whole-body count. IDs are namespaced to avoid changing existing arm cards.
add('neck_trapezius','Трапециевидная мышца','trapezius','A04.3.01.001',
    'Затылочная кость, выйная связка, остистые отростки C7–T12.',
    'Латеральная треть ключицы, акромион и ость лопатки.',
    'Поднимает, приводит и опускает лопатку разными частями; участвует в её вращении кверху.',
    'Добавочный нерв (XI); шейные ветви C3–C4.',
    'Ветви поперечной артерии шеи (a. transversa colli).',group='neck_posterior',depth=1,view='post',
    slug='trapezius-muscle',second=BACK,locator='Trapezius, Origin / Insertion / Action / Innervation',blood=BACK,blood_locator='Trapezius, Artery',
    note='Региональный просмотр той же трапециевидной мышцы, которая имеется в разделе верхней конечности; в общем счёте тела её нельзя считать второй мышцей.',parts={
      'descending':dict(ru='Нисходящая часть',lat='pars descendens',code='A04.3.01.002',o='Верхняя выйная линия, наружный затылочный выступ, выйная связка.',i='Латеральная треть ключицы.',a='Поднимает лопатку.'),
      'transverse':dict(ru='Поперечная часть',lat='pars transversa',code='A04.3.01.003',o='Остистые отростки у шейно-грудного перехода и верхних грудных позвонков.',i='Акромион и ость лопатки.',a='Приводит лопатку.'),
      'ascending':dict(ru='Восходящая часть',lat='pars ascendens',code='A04.3.01.004',o='Остистые отростки нижних грудных позвонков.',i='Медиальный конец ости лопатки.',a='Опускает лопатку.')})
add('neck_levator_scapulae','Мышца, поднимающая лопатку','levator scapulae','A04.3.01.009',
    'Поперечные отростки C1–C4.', 'Медиальный край лопатки от верхнего угла до основания ости.',
    'Поднимает лопатку.', 'Дорсальный нерв лопатки (C5) и ветви C3–C4.',
    'Дорсальная артерия лопатки (a. dorsalis scapulae).',group='neck_posterior',view='post',
    slug='levator-scapulae-muscle',second=BACK,locator='Levator scapulae',
    overrides={'s':[ref(BACK,'Levator scapulae, Artery'),ref(DSA_STUDY,'Introduction: DSA supplies levator scapulae')]},
    note='Региональный просмотр той же мышцы, которая имеется в разделе верхней конечности; не дополнительная мышца в общем счёте тела.')

# Gray's deep-back excerpt has no general Nerves/Actions section after the
# detailed muscle descriptions. Use the actually present university columns.
for key in ('iliocostalis_cervicis','longissimus_cervicis','longissimus_capitis',
            'spinalis_cervicis','semispinalis_cervicis','semispinalis_capitis'):
    row={'iliocostalis_cervicis':'Iliocostalis',
         'longissimus_cervicis':'Longissimus','longissimus_capitis':'Longissimus',
         'spinalis_cervicis':'Spinalis','semispinalis_cervicis':'Semispinalis',
         'semispinalis_capitis':'Semispinalis'}[key]
    for field,col in [('a','Action'),('n','Innervation')]:
        MUSCLE_TEMPLATES[key]['fieldRefs'][field][1]=ref(BACK,row+', '+col)

MUSCLE_TEMPLATES['longissimus_capitis']['a']='Разгибает голову; с одной стороны наклоняет и поворачивает её в свою сторону.'
MUSCLE_TEMPLATES['longissimus_capitis']['fieldRefs']['a'][1]=ref(OPENSTAX,'Table 11.5, Longissimus capitis, Target motion direction')

# Disagreement notes retain the exact sources in addition to field summaries.
for key in ('scalenus_anterior','scalenus_medius','scalenus_posterior'):
    MUSCLE_TEMPLATES[key]['noteRefs']=[ref(KH+'scalene-muscles','Origins and insertions; Innervation'),
        ref(UAMS,'Строка '+key.replace('_',' ')+', Origin / Innervation'),ref(LOYOLA,'С. 4, соответствующая строка Scalene')]
MUSCLE_TEMPLATES['longus_colli']['noteRefs']=[ref(KH+'longus-colli-muscle','Innervation'),
    ref(GRAY_PRE,'Nerves: Longus colli'),ref(LOYOLA,'С. 4, Longus colli, Innervation')]

for key, muscle in MUSCLE_TEMPLATES.items():
    for part_key, part in muscle.get('parts',{}).items():
        # Part-specific locators, not an automatic assertion that every parent
        # field applies to every part. Only fields explicitly written exist.
        fields={field:[dict(r,locator=r['locator']+'; '+part['lat']) for r in muscle['fieldRefs'][field]]
                for field in ('o','i','n','a') if field in part}
        if key=='neck_trapezius':
            for field in fields:
                fields[field][1]=ref(GRAY_SHOULDER,'Trapezius: superior / middle / inferior fibers; '+
                    ('Actions' if field=='a' else 'начало и прикрепление')+'; '+part['lat'])
        part['fieldRefs']=fields
        EVIDENCE[key].setdefault('parts',{})[part_key]=dict(fields=fields,geometryValidated=False)
    # Rebuild bibliography after editorial overrides; preserve nomenclature.
    nomenclature=[r for r in muscle['refs'] if r['url'] in (IFAA,IFAA_BACK,BOOK_URL)]
    source_refs=[r for refs in muscle['fieldRefs'].values() for r in refs]
    source_refs += muscle.get('noteRefs',[])
    source_refs += [r for p in muscle.get('parts',{}).values() for refs in p['fieldRefs'].values() for r in refs]
    muscle['refs']=list({(r['url'],r['locator']):r for r in source_refs+nomenclature}.values())
    muscle['fieldStatus']={f:'checked_two_sources' for f in ('o','i','a','n','s')}
    EVIDENCE[key]['fieldStatus']=muscle['fieldStatus']
    EVIDENCE[key]['noteRefs']=muscle.get('noteRefs',[])

if __name__ == '__main__':
    import json
    from pathlib import Path
    target=Path(__file__).resolve().parents[1]/'research/neck-muscle-evidence.json'
    target.write_text(json.dumps(dict(version=1,templates=len(MUSCLE_TEMPLATES),
        evidence=EVIDENCE,externalExpertReview=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(MUSCLE_TEMPLATES)} neck muscle templates; evidence -> {target}')

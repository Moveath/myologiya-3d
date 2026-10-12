"""Editorial source for head cards, with field-level evidence.

Only short, independently worded summaries are published. The cached books,
articles, figures and atlases are not distributed. Layers are UI display groups,
not a claim that all facial muscles form three uniform anatomical laminae.
"""
from head_terms import BOOK_URL

IFAA = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1673%20A2F%20EN.htm'
DEGUM = 'https://www.degum.de/fileadmin/dokumente/sektionen/kopf-hals/Informationen_zum_Fach/Instruction_for_the_sonography_of_facial_muscles_v06a.pdf'
LUMEN = 'https://www.meddean.luc.edu/lumen/meded/grossanatomy/dissector/mml/'
KENHUB = 'https://www.kenhub.com/en/library/anatomy/'
TMA = 'https://teachmeanatomy.info/encyclopaedia/'
FACE = KENHUB + 'the-facial-muscles'
FACIAL = 'Лицевой нерв (n. facialis, VII).'
BUCCAL = 'Щёчные ветви лицевого нерва (rr. buccales n. facialis, VII).'
TEMPORAL = 'Височные ветви лицевого нерва (rr. temporales n. facialis, VII).'
MANDIBULAR = 'Краевая ветвь нижней челюсти лицевого нерва (r. marginalis mandibulae n. facialis, VII).'
FACIAL_ARTERY = 'Ветви лицевой артерии (a. facialis).'
LOWER_LABIAL = 'Нижняя губная артерия (a. labialis inferior).'
SUPERFICIAL_TEMPORAL = 'Ветви поверхностной височной артерии (a. temporalis superficialis).'

MUSCLE_TEMPLATES = {}
EVIDENCE = {}

def kh(slug): return KENHUB + slug + '-muscle'
def tma(slug): return TMA + slug[0] + '/' + slug + '/'

def add(key, ru, latin, code, origin, insertion, action, nerve, supply,
        anatomy, blood=None, *, group='head_face', depth=1, view='ant', note='', parts=None):
    muscle = dict(ru=ru, lat='m. '+latin, code=code, g=group, d=depth, v=view,
                  L={1:'Поверхностный слой',2:'Средний слой',3:'Глубокий слой'}[depth],
                  o=origin,i=insertion,a=action,n=nerve,s=supply,note=note)
    if parts: muscle['parts']=parts
    sources = list(dict.fromkeys([*anatomy,*(blood or anatomy)]))
    muscle['refs'] = [{'url':url,'title':('Loyola University: анатомия мышцы' if 'luc.edu' in url else
                     'DEGUM: таблицы мышц, с. 4–7' if 'degum.de' in url else
                     'TeachMeAnatomy' if 'teachmeanatomy' in url else
                     'Kenhub: открытая статья' if 'kenhub' in url else 'Анатомическое исследование')}
                     for url in sources]
    muscle['refs'] += [{'title':'TA98: латинские термины','url':IFAA},
                       {'title':'Колесников, 2003: с. 43–44','url':BOOK_URL}]
    MUSCLE_TEMPLATES[key]=muscle
    EVIDENCE[key]={'terminology':{'code':code,'sources':[IFAA,BOOK_URL],'book_pages':[43,44]},
                   'fields':{field:list(anatomy) for field in ['o','i','a','n']}}
    EVIDENCE[key]['fields']['s']=list(blood or anatomy)
    if note: EVIDENCE[key]['note']=note

add('occipitofrontalis','Затылочно-лобная мышца','occipitofrontalis','A04.1.03.003',
    'Лобное брюшко: кожа бровей и волокна соседних мимических мышц. Затылочное: область выйных линий затылочной кости.',
    'Сухожильный шлем (galea aponeurotica).',
    'Поднимает брови и образует складки лба; затылочное брюшко смещает кожу головы назад.',
    'Лобное брюшко — височные ветви; затылочное — задний ушной нерв. Оба отходят от лицевого нерва (VII).',
    'Лобное брюшко — ветви глазной и поверхностной височной артерий; затылочное — затылочная артерия.',
    [LUMEN+'fron.htm',kh('occipitofrontalis'),DEGUM], [kh('occipitofrontalis'),DEGUM],
    group='head_scalp',view='antlat',
    note='LUMEN и таблица DEGUM называют для затылочного брюшка наивысшую выйную линию (linea nuchalis suprema), Kenhub — верхнюю (linea nuchalis superior). Эти ориентиры не приравниваются друг к другу; точка начала на кости здесь не задана.',
    parts={
      'frontal':{'ru':'Лобное брюшко','lat':'venter frontalis','code':'A04.1.03.004',
                 'o':'Кожа бровей и волокна соседних мимических мышц.','i':'Сухожильный шлем.',
                 'a':'Поднимает брови, образует складки кожи лба.','n':TEMPORAL},
      'occipital':{'ru':'Затылочное брюшко','lat':'venter occipitalis','code':'A04.1.03.005',
                   'o':'Затылочная кость в области выйных линий; различие источников пояснено в примечании.',
                   'i':'Сухожильный шлем.','a':'Смещает кожу головы назад.',
                   'n':'Задний ушной нерв (n. auricularis posterior), ветвь лицевого нерва (VII).'}})

add('temporoparietalis','Височно-теменная мышца','temporoparietalis','A04.1.03.006',
    'Фасциальные структуры височной области над ушной раковиной.',
    'Сухожильный шлем (galea aponeurotica).',
    'Участвует в натяжении покровов головы; выраженность действия описывается неодинаково.',TEMPORAL,SUPERFICIAL_TEMPORAL,
    [LUMEN+'tepa.htm','https://www.kenhub.com/de/library/anatomie/musculus-temporoparietalis',DEGUM],
    [DEGUM,'https://www.kenhub.com/de/library/anatomie/musculus-temporoparietalis'],
    group='head_scalp',view='lat',
    note='LUMEN указывает фиксацию сухожильного шлема, Kenhub — натяжение кожи головы и содействие движениям уха. DEGUM не выделяет заметной функции. Поэтому конкретное движение не показано как обязательное.')

add('orbicularis_oculi','Круговая мышца глаза','orbicularis oculi','A04.1.03.013',
    'Медиальный край глазницы, медиальная связка века и слёзная кость.',
    'Ткани век и кожа вокруг глазницы.',
    'Закрывает веки; глубокая часть участвует в отведении слёз.',
    'Височные и скуловые ветви лицевого нерва (rr. temporales et zygomatici n. facialis, VII).',
    'Ветви глазной, лицевой, поверхностной височной и верхнечелюстной артерий.',
    [LUMEN+'ooc.htm',tma('orbicularis-oculi'),DEGUM],[tma('orbicularis-oculi'),DEGUM],
    parts={
      'orbital':{'ru':'Глазничная часть','lat':'pars orbitalis','code':'A04.1.03.017','a':'Сильно смыкает веки.'},
      'palpebral':{'ru':'Вековая часть','lat':'pars palpebralis','code':'A04.1.03.014','a':'Мягко смыкает веки при мигании.'},
      'deep':{'ru':'Глубокая часть','lat':'pars profunda','code':'A04.1.03.016','a':'Участвует в отведении слёз.',
              'x':'В учебниках также называется слёзной частью; в TA98 — pars profunda.'},
      'ciliary':{'ru':'Ресничный пучок','lat':'fasciculus ciliaris','code':'A04.1.03.015',
                 'x':'Термин TA98 для пучка вековой части. Отдельной геометрии в этой модели нет.'}})

add('corrugator_supercilii','Мышца, сморщивающая бровь','corrugator supercilii','A04.1.03.018',
    'Медиальный участок надбровной дуги лобной кости.','Кожа брови.',
    'Сближает брови, образуя вертикальные складки межбровья.',TEMPORAL,
    'Ветви глазной и поверхностной височной артерий.',
    [LUMEN+'crr.htm',tma('corrugator-supercilii'),kh('corrugator-supercilii')],
    [tma('corrugator-supercilii'),kh('corrugator-supercilii')],depth=2)

add('procerus','Мышца гордецов','procerus','A04.1.03.008',
    'Носовая кость и прилежащий хрящ носа.','Кожа межбровья.',
    'Тянет медиальную часть бровей вниз; образует поперечные складки у корня носа.',FACIAL,FACIAL_ARTERY,
    [LUMEN+'pro.htm',tma('procerus'),kh('procerus')],[tma('procerus'),kh('procerus')],
    note='Ветви лицевого нерва в источниках обозначены по-разному: LUMEN — височная, TeachMeAnatomy — щёчные; Kenhub перечисляет височные, нижние скуловые или щёчные. Общий для источников уровень — лицевой нерв.')

add('nasalis','Носовая мышца','nasalis','A04.1.03.009',
    'Верхняя челюсть у основания носа.','Поперечная часть — апоневроз спинки носа; крыльная — ткани крыла носа.',
    'Изменяет просвет ноздрей: поперечная часть суживает его, крыльная расширяет.',BUCCAL,
    'Ветви лицевой артерии и подглазничная артерия (a. infraorbitalis).',
    [tma('nasalis'),kh('nasalis')],[tma('nasalis'),kh('nasalis')],
    parts={'transverse':{'ru':'Поперечная часть','lat':'pars transversa','code':'A04.1.03.010',
                         'i':'Апоневроз спинки носа.','a':'Суживает ноздри.'},
           'alar':{'ru':'Крыльная часть','lat':'pars alaris','code':'A04.1.03.011',
                   'i':'Ткани крыла носа.','a':'Расширяет ноздри.'}})

add('depressor_septi_nasi','Мышца, опускающая перегородку носа','depressor septi nasi','A04.1.03.012',
    'Верхняя челюсть над медиальным резцом.','Подвижная часть перегородки носа.',
    'Тянет перегородку носа вниз.',FACIAL,FACIAL_ARTERY,
    [tma('depressor-septi-nasi'),DEGUM],[tma('depressor-septi-nasi'),DEGUM],
    note='В электронной таблице IFAA встречается код A04.1.02.012. В книге Колесникова (2003, с. 43) указан A04.1.03.012; здесь сохранён код печатного TA98.')

add('orbicularis_oris','Круговая мышца рта','orbicularis oris','A04.1.03.023',
    'Околоротовые мышцы, узел угла рта и прилежащие участки челюстей.',
    'Кожа и слизистая оболочка губ.','Смыкает и выдвигает губы.',BUCCAL,
    'Верхняя и нижняя губные артерии (aa. labiales superior et inferior).',
    [LUMEN+'oor.htm',kh('orbicularis-oris'),tma('orbicularis-oris')],
    [tma('orbicularis-oris'),kh('orbicularis-oris')],
    parts={'marginal':{'ru':'Краевая часть','lat':'pars marginalis','code':'A04.1.03.024',
                       'x':'Часть названа по TA98; отдельной геометрии в BodyParts3D нет.'},
           'labial':{'ru':'Губная часть','lat':'pars labialis','code':'A04.1.03.025',
                      'x':'Часть названа по TA98; отдельной геометрии в BodyParts3D нет.'}})

add('depressor_anguli_oris','Мышца, опускающая угол рта','depressor anguli oris','A04.1.03.026',
    'Наружная поверхность нижней челюсти в области косой линии.',
    'Узел угла рта (modiolus anguli oris).','Опускает угол рта.',FACIAL,LOWER_LABIAL,
    [LUMEN+'dao.htm',kh('depressor-anguli-oris')],[kh('depressor-anguli-oris'),DEGUM])

add('depressor_labii_inferioris','Мышца, опускающая нижнюю губу','depressor labii inferioris','A04.1.03.033',
    'Косая линия нижней челюсти.','Кожа и слизистая оболочка нижней губы.',
    'Опускает нижнюю губу.',MANDIBULAR,LOWER_LABIAL,
    [LUMEN+'dli.htm',kh('depressor-labii-inferioris'),DEGUM],[kh('depressor-labii-inferioris'),DEGUM],depth=2,
    note='LUMEN и DEGUM указывают краевую ветвь нижней челюсти лицевого нерва. В статье Kenhub указана шейная ветвь. Расхождение сохранено явно; в поле иннервации приведён вариант двух согласующихся источников.')

add('mentalis','Подбородочная мышца','mentalis','A04.1.03.037',
    'Передняя поверхность нижней челюсти ниже резцов.','Кожа подбородка.',
    'Поднимает и сморщивает кожу подбородка, выдвигает нижнюю губу.',MANDIBULAR,LOWER_LABIAL,
    [LUMEN+'men.htm',kh('mentalis')],[kh('mentalis'),DEGUM],depth=2)

add('risorius','Мышца смеха','risorius','A04.1.03.028',
    'Фасции околоушной и жевательной областей.','Узел угла рта и прилежащая кожа.',
    'Оттягивает угол рта латерально.',BUCCAL,FACIAL_ARTERY,
    [LUMEN+'ris.htm',kh('risorius')],[kh('risorius'),DEGUM],
    note='Начальные прикрепления изменчивы; перечислены общие фасциальные области, а не единственная обязательная точка.')

add('zygomaticus_major','Большая скуловая мышца','zygomaticus major','A04.1.03.029',
    'Наружная поверхность скуловой кости.','Узел угла рта.',
    'Тянет угол рта вверх и латерально.',FACIAL,FACIAL_ARTERY,
    [LUMEN+'zmj.htm',kh('zygomaticus-major')],[kh('zygomaticus-major'),DEGUM],view='antlat')
add('zygomaticus_minor','Малая скуловая мышца','zygomaticus minor','A04.1.03.030',
    'Скуловая кость у нижнего края глазницы.','Ткани верхней губы.',
    'Поднимает верхнюю губу.',FACIAL,FACIAL_ARTERY,
    [LUMEN+'zmn.htm',kh('zygomaticus-minor')],[kh('zygomaticus-minor'),DEGUM],view='antlat')
add('levator_labii_superioris','Мышца, поднимающая верхнюю губу','levator labii superioris','A04.1.03.031',
    'Область подглазничного края верхней челюсти.','Ткани верхней губы.',
    'Поднимает верхнюю губу.',FACIAL,
    'Ветви лицевой и подглазничной артерий.',
    [LUMEN+'lls.htm',kh('levator-labii-superioris'),DEGUM],[kh('levator-labii-superioris'),DEGUM])
add('levator_nasolabialis','Мышца, поднимающая верхнюю губу и крыло носа','levator labii superioris alaeque nasi','A04.1.03.032',
    'Лобный отросток верхней челюсти.','Верхняя губа и ткани крыла носа.',
    'Поднимает верхнюю губу и крыло носа.',FACIAL,
    'Ветви лицевой и подглазничной артерий.',
    [LUMEN+'llsa.htm',FACE,DEGUM],[FACE,DEGUM],
    note='В электронной таблице IFAA используется более позднее название m. levator nasolabialis. В карточке сохранена латынь печатного TA98 и русского издания 2003 года.')
add('levator_anguli_oris','Мышца, поднимающая угол рта','levator anguli oris','A04.1.03.034',
    'Клыковая ямка верхней челюсти.','Узел угла рта.',
    'Поднимает угол рта.',FACIAL,
    'Верхняя губная и подглазничная артерии.',
    [LUMEN+'lao.htm',kh('levator-anguli-oris')],[kh('levator-anguli-oris'),DEGUM],depth=2)
add('buccinator','Щёчная мышца','buccinator','A04.1.03.036',
    'Альвеолярные области обеих челюстей у моляров и крылонижнечелюстной шов (raphe pterygomandibularis).',
    'Узел угла рта; волокна вплетаются в круговую мышцу рта.',
    'Прижимает щёку к зубам и помогает удерживать пищу между зубными рядами.',BUCCAL,
    'Щёчная артерия (a. buccalis), ветвь верхнечелюстной артерии.',
    [LUMEN+'buc.htm',kh('buccinator'),tma('buccinator')],[kh('buccinator'),tma('buccinator')],depth=3,view='lat')

add('masseter','Жевательная мышца','masseter','A04.1.04.002',
    'Скуловая дуга; места начала двух частей различаются.',
    'Наружная поверхность ветви и угла нижней челюсти.',
    'Поднимает нижнюю челюсть, закрывая рот.',
    'Жевательный нерв (n. massetericus), ветвь нижнечелюстного нерва (V3).',
    'Жевательная артерия (a. masseterica), ветвь верхнечелюстной артерии.',
    [LUMEN+'mass.htm',tma('masseter'),kh('masseter')],[tma('masseter'),kh('masseter')],
    group='head_mastication',depth=2,view='lat',
    parts={'superficial':{'ru':'Поверхностная часть','lat':'pars superficialis','code':'A04.1.04.003',
                          'o':'Передний отдел скуловой дуги и верхнечелюстной отросток скуловой кости.'},
           'deep':{'ru':'Глубокая часть','lat':'pars profunda','code':'A04.1.04.004',
                   'o':'Глубокая поверхность заднего отдела скуловой дуги.'}})
add('temporalis','Височная мышца','temporalis','A04.1.04.005',
    'Височная ямка и височная фасция.','Венечный отросток нижней челюсти.',
    'Поднимает нижнюю челюсть; задние волокна тянут её назад.',
    'Глубокие височные нервы (nn. temporales profundi), ветви нижнечелюстного нерва (V3).',
    'Глубокие височные артерии и ветви поверхностной височной артерии.',
    [LUMEN+'temp.htm',kh('temporalis'),tma('temporalis')],[kh('temporalis'),tma('temporalis')],
    group='head_mastication',depth=2,view='lat')
add('lateral_pterygoid','Латеральная крыловидная мышца','pterygoideus lateralis','A04.1.04.006',
    'Большое крыло клиновидной кости и наружная поверхность латеральной пластинки крыловидного отростка.',
    'Крыловидная ямка шейки нижней челюсти и структуры височно-нижнечелюстного сустава.',
    'Выдвигает нижнюю челюсть; участвует в открывании рта и боковых движениях.',
    'Нерв латеральной крыловидной мышцы, ветвь нижнечелюстного нерва (V3).',
    'Крыловидные ветви верхнечелюстной артерии (rr. pterygoidei a. maxillaris).',
    [LUMEN+'lpte.htm',tma('lateral-pterygoid'),kh('lateral-pterygoid')],
    [tma('lateral-pterygoid'),kh('lateral-pterygoid')],group='head_mastication',depth=3,view='lat',
    note='Учебные описания прикрепления упрощены по-разному: TeachMeAnatomy объединяет обе головки у шейки челюсти, LUMEN дополнительно называет суставной диск, Kenhub разделяет костное и капсульное прикрепления. Общая карточка сохраняет оба участка без утверждения об одинаковом прикреплении головок.',
    parts={'upper':{'ru':'Верхняя головка','lat':'caput superius','code':'A04.1.04.007',
                     'o':'Подвисочная поверхность большого крыла клиновидной кости.'},
           'lower':{'ru':'Нижняя головка','lat':'caput inferius','code':'A04.1.04.008',
                     'o':'Наружная поверхность латеральной пластинки крыловидного отростка клиновидной кости.'}})
add('medial_pterygoid','Медиальная крыловидная мышца','pterygoideus medialis','A04.1.04.009',
    'Медиальная поверхность латеральной пластинки крыловидного отростка, бугор верхней челюсти и пирамидальный отросток нёбной кости.',
    'Медиальная поверхность ветви и угла нижней челюсти.',
    'Поднимает нижнюю челюсть и участвует в боковых жевательных движениях.',
    'Нерв медиальной крыловидной мышцы, ветвь нижнечелюстного нерва (V3).',
    'Крыловидные ветви верхнечелюстной артерии.',
    [LUMEN+'mpte.htm',tma('medial-pterygoid'),kh('medial-pterygoid')],
    [tma('medial-pterygoid'),kh('medial-pterygoid')],group='head_mastication',depth=3,view='lat')

for key,ru,code,origin,insertion,action in [
    ('auricularis_anterior','Передняя ушная мышца','020','Височная фасция и край сухожильного шлема.','Ость завитка ушной раковины.','Слабо тянет ушную раковину вперёд.'),
    ('auricularis_superior','Верхняя ушная мышца','021','Сухожильный шлем.','Верхняя часть ушной раковины.','Слабо тянет ушную раковину вверх.'),
    ('auricularis_posterior','Задняя ушная мышца','022','Сосцевидный отросток височной кости.','Задняя поверхность хряща ушной раковины в области раковины.','Слабо тянет ушную раковину назад.'),
]:
    posterior = key.endswith('posterior')
    blood = [DEGUM, KENHUB+'posterior-auricular-artery']
    supply = 'Задняя ушная артерия (a. auricularis posterior).'
    if key.endswith('anterior'):
        supply = SUPERFICIAL_TEMPORAL
        # Independent open publisher summary confirms this vessel.
        blood = [DEGUM,'https://www.elsevier.com/resources/anatomy/muscular-system/muscles-of-head/auricularis-anterior-muscle/23524']
    add(key,ru,key.replace('_',' '),'A04.1.03.'+code,origin,insertion,action,
        'Задний ушной нерв, ветвь лицевого нерва (VII).' if posterior else TEMPORAL,
        supply,[DEGUM,FACE],blood,group='head_ear',view='lat')

COOK = 'https://journals.sagepub.com/doi/10.1177/074880680001700402'
DS_STUDY = 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264148'
add('depressor_supercilii','Мышца, опускающая бровь','depressor supercilii','A04.1.03.019',
    'Лобный отросток верхней челюсти — по двум анатомическим исследованиям.',
    'Кожа медиальной части брови.','Опускает медиальный участок брови.',FACIAL,
    'Ветви глазной артерии (a. ophthalmica).',
    [COOK,DS_STUDY,DEGUM],
    [DEGUM,'https://www.elsevier.com/resources/anatomy/muscular-system/muscles-of-head/depressor-supercilii/21131'],depth=2,
    note='Cook и соавт. и исследование PLOS ONE описывают начало от лобного отростка верхней челюсти. В сводной таблице DEGUM указана лобная кость. Это расхождение не скрыто; модели мышцы в выбранном наборе нет.')

TM_STUDY='https://www.scielo.cl/pdf/ijmorphol/v31n4/art40.pdf'
TM_DICT='https://www.academie-medecine.fr/le-dictionnaire/index.php?q=muscle+transverse+du+menton'
add('transversus_menti','Поперечная мышца подбородка','transversus menti','A04.1.03.027',
    'Волокна мышцы, опускающей угол рта, с одной стороны.',
    'Соответствующие волокна противоположной стороны в области подбородка.',
    'Отдельная функция не установлена двумя независимыми источниками; в тест по функции не включена.',
    'Лицевой нерв (n. facialis, VII).',
    'Конкретная питающая ветвь не подтверждена двумя независимыми источниками.',
    [TM_STUDY,kh('depressor-anguli-oris')],
    [TM_STUDY],
    note='Непостоянный поперечный пучок. В исследовании 2013 года описано питание ветвями подподбородочной артерии; это наблюдение одного исследования не выдано за подтверждённую общую норму.')
TM_DEFINITION='https://www.imaios.cn/en/e-anatomy/anatomical-structures/transversus-menti-muscle-14215192'
EVIDENCE['transversus_menti']['fields']['n'] = [TM_STUDY,TM_DEFINITION]
MUSCLE_TEMPLATES['transversus_menti']['refs'].append({'title':'Открытое определение: иннервация','url':TM_DEFINITION})
EVIDENCE['transversus_menti']['unconfirmed'] = ['a','s']

# Name-only parts inherit general fields in the UI; source evidence stays with
# the parent record. Inherited fields are explicitly labelled by the renderer.
for key,muscle in MUSCLE_TEMPLATES.items():
    for field in ('o','i','a','n','s'):
        if field not in EVIDENCE[key].get('unconfirmed',[]):
            assert len(set(EVIDENCE[key]['fields'][field])) >= 2, (key,field)
    EVIDENCE[key]['parts'] = {part:{'code':value['code'],
        'fields':{f:EVIDENCE[key]['fields'][f] for f in ('o','i','a','n') if f in value}}
        for part,value in muscle.get('parts',{}).items()}

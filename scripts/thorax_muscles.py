"""Thoracic teaching cards: concise authored summaries and field-level evidence.

Source geometry, nomenclature and typical anatomy are separate assertions.
No clinical measurements or inferred attachment polygons are supplied here.
"""
from copy import deepcopy
from head_terms import BOOK_URL
from neck_muscles import MUSCLE_TEMPLATES as NECK

KH='https://www.kenhub.com/en/library/anatomy/'
BASE='https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/'
UAMS=BASE+'muscles-of-the-thorax/'
BACK=BASE+'muscles-of-the-back-region/'
LOYOLA='https://www.stritch.luc.edu/lumen/meded/grossanatomy/homepage/MuscleTables/ThoraxMuscleTable.pdf'
LOYOLA_BACK=LOYOLA.replace('ThoraxMuscleTable','BackMuscleTable')
GRAY='https://www.wikimd.org/wiki/'
GT=GRAY+'The_Muscles_of_the_Thorax'
GB=GRAY+'The_Deep_Muscles_of_the_Back'
GP=GRAY+'The_Muscles_Connecting_the_Upper_Extremity_to_the_Anterior_and_Lateral_Thoracic_Walls'
STAT='https://www.ncbi.nlm.nih.gov/sites/books/NBK538321/'
TMA='https://teachmeanatomy.info/thorax/muscles/diaphragm/'
TTU='https://anatomy.ttuhscep.edu/schemes/peritoneum_ans.html'
HUMAN_INTERCOSTALS='https://pmc.ncbi.nlm.nih.gov/articles/PMC2278403/'
VT_RESP='https://publishing.vt.edu/en/books/59/files/bf7ac307-efde-46ae-b416-fb193cd612ef.pdf'
SERRATUS_STUDY='https://pubmed.ncbi.nlm.nih.gov/11424195/'
STERNALIS1='https://pmc.ncbi.nlm.nih.gov/articles/PMC3117696/'
STERNALIS2='https://pmc.ncbi.nlm.nih.gov/articles/PMC7459670/'
STERNALIS3='https://pmc.ncbi.nlm.nih.gov/articles/PMC3417776/'
IFAA='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/04.4.01%20TA98%20EN.htm'
IFAA_DIAPHRAGM=IFAA.replace('04.4.01','04.4.02')
IFAA_BACK='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1770%20A2F%20EN.htm'
PUBLICATION_TITLES={
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4644838/':'Sternalis muscle: case report, 2015',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2548324/':'Kahrilas et al., 2008: Approaches to the Diagnosis and Grading of Hiatal Hernia',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7263794/':'Surgical Anatomy of Paraesophageal Hernias',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3846937/':'The anatomical compartments and their connections as demonstrated by ectopic air',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9877484/':'Three-dimensional morphogenesis of the human diaphragm',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3731110/':'Bordoni & Zanier, 2013: Anatomic connections of the diaphragm',
 'https://ifaa.unifr.ch/Public/TNAEntryPage/ref/Musil2019.pdf':'Musil et al., 2019: A plea for an extension of the anatomical nomenclature',
}

MUSCLE_TEMPLATES={}
EVIDENCE={}
SIDED_TEMPLATES=set()

def ref(url,locator):
    title=('Gray, 1918: открытый текст' if 'wikimd' in url else
           'Kenhub: открытая статья' if 'kenhub' in url else
           'UAMS: учебная таблица' if 'uams.edu' in url else
           'Loyola University Chicago: таблица мышц, 2015' if 'luc.edu' in url else
           'Vilensky et al., 2001' if url==SERRATUS_STUDY else
           'Raikos et al., 2011: грудинная мышца' if url==STERNALIS1 else
           'Petto et al., 2020: грудинная мышца' if url==STERNALIS2 else
           'Schulman et al., 2012: грудинная мышца' if url==STERNALIS3 else
           'StatPearls: Anatomy, Thorax, Muscles' if url==STAT else
           'TeachMeAnatomy: диафрагма' if url==TMA else
           'Texas Tech: учебный анатомический разбор' if url==TTU else
           'Wilson et al., 2001: межрёберные мышцы человека' if url==HUMAN_INTERCOSTALS else
           'Virginia Tech: Pulmonary Physiology for Pre-Clinical Students' if url==VT_RESP else
           PUBLICATION_TITLES.get(url,'Анатомическое исследование / обзор'))
    return dict(url=url,title=title,locator=locator)

def pair(url1,loc1,url2,loc2):return [ref(url1,loc1),ref(url2,loc2)]

def add(key,ru,lat,code,o,i,a,n,s,*,group,slug=None,second=UAMS,row=None,
        depth=2,view='antlat',sided=True,noModel=False,note='',parts=None,overrides=None,noteRefs=None):
    key='thorax_'+key
    page=KH+(slug or key[7:].replace('_','-')+'-muscle')
    row=row or lat
    fields={f:pair(page,section,second,row+', '+col) for f,section,col in [
        ('o','Origin and insertion','Origin'),('i','Origin and insertion','Insertion'),
        ('a','Function','Action'),('n','Innervation','Innervation'),('s','Blood supply','Artery / Blood supply')]}
    if overrides:fields.update(overrides)
    m=dict(ru=ru,lat=lat,code=code,g=group,d=depth,v=view,
        L={1:'Поверхностный слой',2:'Средний слой',3:'Глубокий слой'}[depth],
        o=o,i=i,a=a,n=n,s=s,note=note,fieldRefs=fields,fieldStatus={f:'checked_two_sources' for f in fields},
        noModel=noModel)
    if noteRefs:m['noteRefs']=noteRefs
    if parts:m['parts']=parts
    MUSCLE_TEMPLATES[key]=m
    if sided:SIDED_TEMPLATES.add(key)
    return m

def part(ru,lat,code=None,*,o=None,i=None,x=None,noModel=False,refs=None):
    p=dict(ru=ru,lat=lat,noModel=noModel)
    if code:p['code']=code
    for f,v in [('o',o),('i',i),('x',x)]:
        if v is not None:p[f]=v
    if refs:p['fieldRefs']={f:deepcopy(refs) for f in ('o','i','x') if f in p}
    return p

INTER='Межрёберные нервы (nn. intercostales).'
POST='Задние ветви спинномозговых нервов (rr. posteriores nervorum spinalium), посегментно.'
ART='Ветви задних межрёберных артерий (aa. intercostales posteriores).'
PECT='Грудная ветвь грудоакромиальной артерии (r. pectoralis a. thoracoacromialis).'
GROUP_NOTE='Это общая карточка группы; число объектов модели не равно числу отдельных мышечных пучков.'

add('pectoralis_major','Большая грудная мышца','m. pectoralis major','A04.4.01.002',
    'Медиальная половина ключицы, передняя поверхность грудины, хрящи верхних рёбер и апоневротические ткани верхней части живота.',
    'Гребень большого бугорка плечевой кости — латеральный край межбугорковой борозды.',
    'Приводит плечо и вращает его внутрь; ключичная часть участвует в сгибании плеча.',
    'Медиальный и латеральный грудные нервы (nn. pectorales medialis et lateralis).',PECT,
    group='thorax_pectoral',depth=1,slug='major-pectoralis-muscle',
    overrides={'a':pair(KH+'major-pectoralis-muscle','Function',STAT,'Structure and Function: pectoralis major, clavicular head')},
    note='Рёберное начало в источниках обозначено по-разному: Kenhub I–VI, UAMS II–VI, Loyola — хрящи истинных рёбер. Граница не считается одинаковой у всех людей. Это региональный просмотр мышцы, уже представленной в руке.',
    parts={
      'clavicular':part('Ключичная часть','pars clavicularis','A04.4.01.003',o='Передняя поверхность медиальной половины ключицы.',i='Латеральный край межбугорковой борозды плечевой кости.'),
      'sternocostal':part('Грудино-рёберная часть','pars sternocostalis','A04.4.01.004',o='Передняя поверхность грудины и хрящи верхних рёбер.',i='Латеральный край межбугорковой борозды плечевой кости.'),
      'abdominal':part('Брюшная часть','pars abdominalis','A04.4.01.005',o='Апоневротические ткани передней стенки живота: передняя пластинка влагалища прямой мышцы / апоневроз наружной косой мышцы.',i='Латеральный край межбугорковой борозды плечевой кости.',x='Источники описывают эту область через разные связанные апоневротические структуры; точная граница не измерена по модели.')} )
add('pectoralis_minor','Малая грудная мышца','m. pectoralis minor','A04.4.01.006',
    'Передняя поверхность III–V рёбер около рёберных хрящей.', 'Клювовидный отросток лопатки.',
    'Тянет лопатку вперёд и вниз.', 'Основной источник — медиальный грудной нерв (n. pectoralis medialis).',PECT,
    group='thorax_pectoral',note='Kenhub дополнительно описывает связь с латеральным грудным нервом через ansa pectoralis; университетские краткие таблицы указывают медиальный нерв. Карточка перечисляет основной источник, а не исключает добавочные ветви.')
add('subclavius','Подключичная мышца','m. subclavius','A04.4.01.007',
    'I ребро у соединения с его хрящом.', 'Нижняя поверхность средней трети ключицы.',
    'Стабилизирует ключицу.', 'Подключичный нерв (n. subclavius), C5–C6.',
    'Ключичная ветвь грудоакромиальной артерии (r. clavicularis a. thoracoacromialis).',
    group='thorax_pectoral',second=GP,row='Subclavius; Nerves; Actions',
    overrides={'s':pair(KH+'subclavius-muscle','Blood supply',STAT,'Blood Supply and Lymphatics: subclavius'),
               'a':pair(KH+'subclavius-muscle','Function',STAT,'Structure and Function: subclavius')})
add('serratus_anterior','Передняя зубчатая мышца','m. serratus anterior','A04.4.01.008',
    'Наружные поверхности I–VIII или IX рёбер.', 'Рёберная поверхность медиального края лопатки.',
    'Смещает лопатку вперёд; нижние пучки участвуют в её вращении кверху.',
    'Длинный грудной нерв (n. thoracicus longus), C5–C7.',
    'Латеральная грудная артерия (a. thoracica lateralis).',group='thorax_pectoral',second=BACK,row='serratus anterior',
    note='Число рёберных зубцов изменчиво; исходная модель не задаёт универсальное число для всех людей.')

for key,ru,code in [('externi','Наружные межрёберные мышцы','012'),('interni','Внутренние межрёберные мышцы','013'),('intimi','Самые внутренние межрёберные мышцы','014')]:
    page=KH+{'externi':'external-intercostal-muscles','interni':'internal-intercostal-muscles','intimi':'innermost-intercostal-muscles'}[key]
    note=GROUP_NOTE
    if key!='externi':note+=' Термины «начало» и «прикрепление» в таблицах иногда переставлены; здесь связь описана сверху вниз.'
    if key=='intimi':note+=' Loyola указывает подъём рёбер, Kenhub и StatPearls — помощь при выдохе; бесспорная общая функция — поддержка межрёберных промежутков.'
    action={'externi':'Поддерживают межрёберные промежутки; участвуют в подъёме рёбер при вдохе.',
            'interni':'Поддерживают межрёберные промежутки; межкостные пучки помогают опускать рёбра при усиленном выдохе.',
            'intimi':'Поддерживают межрёберные промежутки; обычно описываются как помощники усиленного выдоха.'}[key]
    add('intercostales_'+key,ru,'mm. intercostales '+key,'A04.4.01.'+code,
        'Нижний край вышележащего ребра'+(' в области рёберной борозды.' if key!='externi' else '.'),
        'Верхний край соседнего нижележащего ребра.',action,INTER,
        'Передние и задние межрёберные артерии (aa. intercostales anteriores et posteriores).',
        group='thorax_wall',depth={'externi':1,'interni':2,'intimi':3}[key],sided=False,
        slug=page[len(KH):],second=UAMS,row={'externi':'external intercostal','interni':'internal intercostal','intimi':'innermost intercostal'}[key],note=note,
        overrides={'o':pair(page,'Origin and insertion',GT if key!='intimi' else LOYOLA,'Intercostales '+key if key!='intimi' else 'С. 1, Innermost intercostal, Origin'),
                   'i':pair(page,'Origin and insertion',GT if key!='intimi' else LOYOLA,'Intercostales '+key if key!='intimi' else 'С. 1, Innermost intercostal, Insertion'),
                   'a':pair(page,'Function',LOYOLA if key=='externi' else STAT,'С. 1, External intercostal, Main actions' if key=='externi' else 'Structure and Function: intercostal layers'),
                   's':pair(page,'Blood supply',LOYOLA,'С. 1, '+{'externi':'External','interni':'Internal','intimi':'Innermost'}[key]+' intercostal, Blood supply')},
        noteRefs=[ref(LOYOLA,'С. 1, межрёберные мышцы'),ref(STAT,'Structure and Function')])
add('subcostales','Подрёберные мышцы','mm. subcostales','A04.4.01.015',
    'Внутренняя поверхность рёбер возле углов.', 'Внутренняя поверхность второго или третьего нижележащего ребра.',
    'Помогают опускать рёбра при усиленном выдохе.',INTER,ART,
    group='thorax_wall',depth=3,sided=False,noModel=True,slug='subcostal-muscles',second=LOYOLA,row='С. 1, Subcostal',
    note='Отдельной исходной модели нет. Направление описано сверху вниз; UAMS называет эти концы в обратном порядке. Положение не восстанавливается из межрёберных сеток.')
add('transversus_thoracis','Поперечная мышца груди','m. transversus thoracis','A04.4.01.016',
    'Задняя поверхность нижней части грудины, мечевидного отростка и прилежащих рёберных хрящей.', 'Внутренние поверхности хрящей II–VI рёбер.',
    'Опускает рёберные хрящи, помогая усиленному выдоху.',INTER,
    'Внутренняя грудная артерия (a. thoracica interna).',group='thorax_wall',depth=3,
    note='Рёберное начало Kenhub уточняет как хрящи IV–VII рёбер, Gray — нижние три–четыре хряща истинных рёбер. В краткой таблице UAMS перечислены только грудина и мечевидный отросток.',
    overrides={'o':pair(KH+'transversus-thoracis-muscle','Origin and insertion',GT,'Transversus thoracis')})

add('levatores_costarum','Мышцы, поднимающие рёбра','mm. levatores costarum','A04.4.01.009',
    'Поперечные отростки C7–T11.', 'Ребро ниже места начала, между бугорком и углом; длинные пучки достигают второго нижележащего ребра.',
    'Могут поднимать рёбра; значение для дыхания обсуждается.',POST,ART,
    group='thorax_wall',depth=3,view='post',slug='levatores-costarum-muscles',
    note='Для нервных сегментов иннервации источники дают разные диапазоны: Kenhub C8–T11, UAMS C7–T11. Это обозначения нервов, а не позвонков начала мышцы: позвонка C8 нет. Gray считал действие на рёбра небольшим; современные таблицы описывают подъём рёбер. Это не симуляция дыхательной механики.',
    overrides={'i':pair(KH+'levatores-costarum-muscles','Origin and insertion: longi/breves',GT,'Levatores costarum (после Transversus thoracis)'),
               'a':pair(KH+'levatores-costarum-muscles','Functions',UAMS,'levatores costarum, Action')},
    parts={
      'longi':part('Длинные мышцы, поднимающие рёбра','mm. levatores costarum longi','A04.4.01.010',x='Нижние длинные пучки достигают второго ребра ниже позвонка начала.',refs=pair(KH+'levatores-costarum-muscles','Origin and insertion: lower four / longi',GT,'Levatores costarum longi')),
      'breves':part('Короткие мышцы, поднимающие рёбра','mm. levatores costarum breves','A04.4.01.011',x='Короткие пучки прикрепляются к первому ребру ниже позвонка начала.',refs=pair(KH+'levatores-costarum-muscles','Origin and insertion: breves',GT,'Levatores costarum breves'))})

add('diaphragm','Диафрагма','diaphragma','A04.4.02.001',
    'Мечевидный отросток, внутренние поверхности шести нижних рёбер и их хрящей, верхние поясничные позвонки и дугообразные связки.',
    'Сухожильный центр (centrum tendineum).', 'При сокращении опускает сухожильный центр и увеличивает объём грудной полости при вдохе.',
    'Двигательная иннервация — диафрагмальные нервы (nn. phrenici), C3–C5.',
    'Верхние и нижние диафрагмальные, мышечно-диафрагмальные и перикардодиафрагмальные артерии.',
    group='thorax_diaphragm',depth=2,sided=False,slug='diaphragm',
    note='Одна непарная мышца. Подразделения ниже — учебные описания: отдельные сетки частей и точные границы отверстий исходником не подтверждаются.',
    overrides={'s':pair(KH+'diaphragm','Blood supply',LOYOLA,'С. 1, Diaphragm, Blood supply')},parts={
      'sternal':part('Грудинная часть диафрагмы','pars sternalis diaphragmatis','A04.4.02.009',o='Задняя поверхность мечевидного отростка.',i='Сухожильный центр.',noModel=True),
      'costal':part('Рёберная часть диафрагмы','pars costalis diaphragmatis','A04.4.02.008',o='Внутренние поверхности VII–XII рёбер и их хрящей.',i='Сухожильный центр.',noModel=True),
      'lumbar':part('Поясничная часть диафрагмы','pars lumbalis diaphragmatis','A04.4.02.002',o='Верхние поясничные позвонки и дугообразные связки.',i='Сухожильный центр.',noModel=True)})

for key,ru,code,o,i in [
 ('serratus_posterior_superior','Верхняя задняя зубчатая мышца','011','Нижняя часть выйной связки и остистые отростки C7–T3.','Верхние края II–V рёбер латеральнее углов.'),
 ('serratus_posterior_inferior','Нижняя задняя зубчатая мышца','010','Остистые отростки T11–L2 и пояснично-грудная фасция.','Нижние края IX–XII рёбер латеральнее углов.')]:
    superior=key.endswith('superior')
    add(key,ru,'m. '+key.replace('_',' '),'A04.3.01.'+code,o,i,
        ('Традиционно описывают подъём верхних рёбер.' if superior else 'Традиционно описывают тягу нижних рёбер вниз и назад.')+' Дыхательная роль не считается окончательно доказанной.',
        'Передние ветви грудных спинномозговых нервов.',ART,group='thorax_back',view='post',
        slug='serratus-posterior-muscles',second=BACK,row=key.replace('_',' '),
        note='Vilensky и соавт. (2001) ставят под сомнение дыхательную функцию и предлагают преимущественно проприоцептивную роль. Kenhub также отмечает дискуссию. '+
             ('Число рёбер в сводках различается: Gray/Kenhub II–V; UAMS I–IV; Loyola II–IV.' if superior else 'Начало в Gray может распространяться до L3; в современных кратких таблицах обычно T11–L2.'),
        overrides={'o':pair(KH+'serratus-posterior-muscles','Origin and insertion: '+key.replace('_',' '),GT,key.replace('_',' ')),
                   'i':pair(KH+'serratus-posterior-muscles','Origin and insertion: '+key.replace('_',' '),GT,key.replace('_',' ')),
                   'a':pair(KH+'serratus-posterior-muscles','Function',SERRATUS_STUDY,'Abstract')},
        noteRefs=[ref(SERRATUS_STUDY,'Abstract'),ref(KH+'serratus-posterior-muscles','Function'),ref(BACK,key.replace('_',' ')),ref(LOYOLA,'С. 1, '+key.replace('_',' '))])

add('iliocostalis_thoracis','Подвздошно-рёберная мышца: грудной исходный объект','m. iliocostalis','A04.3.02.005',
    'Углы VII–XII рёбер.', 'Углы I–VI рёбер и поперечный отросток C7.',
    'Разгибает позвоночник; при одностороннем сокращении наклоняет его в свою сторону.',POST,ART,
    group='thorax_deep_back',depth=3,view='post',slug='iliocostalis-muscle',second=BACK,row='iliocostalis',
    note='Источник модели именует объект iliocostalis thoracis. В TA98 отдельного термина с этим названием нет: здесь приведено общее m. iliocostalis. Pars thoracica A04.3.02.008 относится к m. iliocostalis lumborum и автоматически с этой сеткой не отождествляется.',
    overrides={f:pair(KH+'iliocostalis-muscle','Origin and insertion: iliocostalis thoracis',GB,'Iliocostalis dorsi') for f in ('o','i')})
add('longissimus_thoracis','Длиннейшая мышца груди','m. longissimus thoracis','A04.3.02.011',
    'Общее сухожилие мышцы, выпрямляющей позвоночник, и задние элементы поясничных позвонков.',
    'Поперечные отростки грудных позвонков и задние участки нижних рёбер в области углов.',
    'Разгибает позвоночник и наклоняет его в свою сторону.',POST,ART,
    group='thorax_deep_back',depth=3,view='post',slug='longissimus-muscle',second=BACK,row='longissimus',
    overrides={f:pair(KH+'longissimus-muscle','Origin and insertion: longissimus thoracis',GB,'Sacrospinalis (common origin); Longissimus dorsi') for f in ('o','i')},
    note='Региональное название не означает, что мышца ограничена T1–T12: присутствуют поясничные прикрепления. Kenhub перечисляет рёбра VII–XII и область углов; Gray — нижние девять–десять рёбер между бугорками и углами. Точный диапазон рёберных пучков не считается универсальным.')
add('spinalis_thoracis','Остистая мышца груди','m. spinalis thoracis','A04.3.02.016',
    'Остистые отростки T11–L2.', 'Остистые отростки верхних грудных позвонков; обычно диапазон T2–T8.',
    'Разгибает позвоночник.',POST,ART,group='thorax_deep_back',depth=3,view='post',slug='spinalis-muscle',second=BACK,row='spinalis',
    overrides={f:pair(KH+'spinalis-muscle','Origin and insertion: spinalis thoracis',GB,'Spinalis dorsi') for f in ('o','i')},
    note='Число верхних прикреплений изменчиво: Gray описывает четыре–восемь верхних грудных позвонков, Kenhub даёт T2–T8.')
add('semispinalis_thoracis','Полуостистая мышца груди','m. semispinalis thoracis','A04.3.02.207',
    'Поперечные отростки T6–T10.', 'Остистые отростки C6–T4.',
    'Разгибает позвоночник; при одностороннем сокращении участвует в повороте в противоположную сторону.',POST,ART,
    group='thorax_deep_back',depth=3,view='post',second=BACK,row='semispinalis',
    overrides={f:pair(KH+'semispinalis-thoracis-muscle','Anatomy',GB,'Semispinalis dorsi') for f in ('o','i')})
add('multifidus','Многораздельные мышцы','mm. multifidi','A04.3.02.202',
    'В грудной области — поперечные отростки позвонков; в поясничной — сосцевидные отростки и крестцово-подвздошная область; в шейной — суставные отростки нижних шейных позвонков.',
    'Остистые отростки расположенных выше позвонков; пучки перекрывают несколько уровней.',
    'Стабилизируют позвоночник, участвуют в разгибании и повороте в противоположную сторону.',POST,
    'В грудной области — задние межрёберные и подрёберная артерии; другие области имеют собственные сегментарные источники.',
    group='thorax_deep_back',depth=3,view='post',second=LOYOLA_BACK,row='С. 2, Multifidus',
    overrides={'o':pair(KH+'multifidus-muscle','Origin and insertion',GB,'Multifidus: sacral, lumbar, thoracic, cervical regions'),
               'a':[ref(KH+'multifidus-muscle','Functions'),ref(LOYOLA_BACK,'С. 2, Multifidus, Main actions: stabilization'),ref(BACK,'multifidus, Action: extension and contralateral rotation')]},
    note='Исходная сетка многораздельных мышц охватывает несколько областей; её нельзя считать отдельно сегментированной грудной частью. Kenhub описывает пучки через 2–5 уровней, Loyola через 2–4; диапазон не унифицирован.',
    parts={'thoracic':part('Многораздельные мышцы груди','m. multifidus thoracis','A04.3.02.204',
        o='Поперечные отростки грудных позвонков.',i='Остистые отростки вышележащих позвонков.',noModel=True,
        refs=pair(KH+'multifidus-muscle','Origin and insertion: thoracic region',GB,'Multifidus, thoracic region'))})
add('rotatores_thoracis','Мышцы-вращатели груди','mm. rotatores thoracis','A04.3.02.212',
    'Поперечные отростки грудных позвонков.', 'Области оснований остистых отростков на один или два уровня выше.',
    'Стабилизируют позвонки; участвуют в разгибании и повороте в противоположную сторону.',POST,ART,
    group='thorax_deep_back',depth=3,view='post',sided=False,slug='rotatores-muscles',second=BACK,row='rotatores',
    note=GROUP_NOTE+' Longi и breves — принятое описательное деление; отдельных кодов этих частей в выбранной главе TA98 нет.',
    overrides={'a':pair(KH+'rotatores-muscles','Functions',LOYOLA_BACK,'С. 2, Rotatores, Main actions')},
    parts={
      'longi':part('Длинные пучки вращателей','rotatores longi',x='Связывают поперечный отросток с областью основания остистого отростка двумя уровнями выше.',noModel=True,refs=pair(KH+'rotatores-muscles','Origin and insertion: long rotators',BACK,'rotatores, Insertion: long rotatores')),
      'breves':part('Короткие пучки вращателей','rotatores breves',x='Достигают соседнего вышележащего позвонка.',noModel=True,refs=pair(KH+'rotatores-muscles','Origin and insertion: short rotators',GB,'Rotatores'))})
add('interspinales_thoracis','Межостистые мышцы груди','mm. interspinales thoracis','A04.3.02.303',
    'Остистый отросток нижележащего позвонка.', 'Остистый отросток соседнего вышележащего позвонка.',
    'Участвуют в разгибании позвоночника.',POST,ART,group='thorax_deep_back',depth=3,view='post',sided=False,
    slug='interspinales-muscles',second=LOYOLA_BACK,row='С. 1, Interspinales',
    note='Грудные пучки развиты не на всех уровнях. Gray и Kenhub по-разному перечисляют отдельные интервалы; сплошная цепочка T1–T12 не заявляется. '+GROUP_NOTE,
    noteRefs=pair(KH+'interspinales-muscles','Origin and insertion: thoracis',GB,'Interspinales, thoracic region'))
add('intertransversarii_thoracis','Межпоперечные мышцы груди','mm. intertransversarii thoracis','A04.3.02.403',
    'Поперечный отросток одного позвонка.', 'Поперечный отросток соседнего позвонка.',
    'Участвуют в боковом наклоне позвоночника.',POST,ART,group='thorax_deep_back',depth=3,view='post',sided=False,noModel=True,
    second=LOYOLA_BACK,row='С. 1, Intertransversarii',
    overrides={f:pair(BACK,'intertransversarii, '+col,LOYOLA_BACK,'С. 1, Intertransversarii, '+col) for f,col in [('o','Origin'),('i','Insertion'),('a','Main actions'),('n','Innervation'),('s','Blood supply')]},
    note='В грудной области это ограниченные сегментарные пучки; отдельной сетки нет. Не изображены как цепочка между всеми грудными позвонками.',
    noteRefs=pair(GB,'Intertransversarii, thoracic region',LOYOLA_BACK,'С. 1, Intertransversarii (thoracic)'))

add('latissimus_dorsi','Широчайшая мышца спины','m. latissimus dorsi','A04.3.01.006',
    'Остистые отростки нижних грудных позвонков, пояснично-грудная фасция, подвздошный гребень и нижние рёбра.',
    'Дно межбугорковой борозды плечевой кости.', 'Разгибает, приводит плечо и вращает его внутрь.',
    'Грудоспинной нерв (n. thoracodorsalis).', 'Грудоспинная артерия (a. thoracodorsalis).',
    group='thorax_back',depth=1,view='post',second=LOYOLA_BACK,row='С. 1, Latissimus dorsi',
    note='Региональный просмотр мышцы, уже представленной в руке. Источники называют три либо четыре нижних ребра; число рёберных пучков не фиксировано для каждого человека.')
for size,ru,code,o,i in [
 ('major','Большая ромбовидная мышца','007','Остистые отростки T2–T5.','Медиальный край лопатки ниже её ости.'),
 ('minor','Малая ромбовидная мышца','008','Нижняя часть выйной связки и остистые отростки C7–T1.','Медиальный край лопатки у основания ости.')]:
    add('rhomboid_'+size,ru,'m. rhomboideus '+size,'A04.3.01.'+code,o,i,
        'Приводит лопатку к позвоночнику и участвует в её вращении суставной впадиной вниз.',
        'Дорсальный нерв лопатки (n. dorsalis scapulae).','Дорсальная артерия лопатки (a. dorsalis scapulae).',
        group='thorax_back',view='post',slug='rhomboid-muscles',second=BACK,row='rhomboideus '+size)

trap=deepcopy(NECK['neck_trapezius'])
trap.update(g='thorax_back',note='Региональный просмотр той же трапециевидной мышцы из разделов шеи и руки; в счёте всего тела она не дублируется.')
MUSCLE_TEMPLATES['thorax_trapezius']=trap
SIDED_TEMPLATES.add('thorax_trapezius')

add('sternalis','Грудинная мышца — вариант','m. sternalis','A04.4.01.001',
    'Изменчиво: описаны прикрепления к верхней части грудины и подключичной области.',
    'Изменчиво: нижние рёбра, их хрящи и апоневротические ткани передней стенки живота.',
    'Установленной общей функции нет; предлагаемые действия остаются гипотезами.',
    'Описаны грудные и/или межрёберные нервы; единой схемы для всех вариантов нет.',
    'В опубликованных случаях описаны ветви внутренней грудной артерии.',
    group='thorax_pectoral',depth=1,sided=False,noModel=True,
    note='Непостоянная мышца: наличия в данном образце и геометрии модели не установлено. Карточка представляет вариант, а не «недостающую нормальную мышцу».',
    overrides={**{f:pair(STERNALIS1,'Introduction / Discussion',STERNALIS2,'Introduction / Discussion: attachments, function, innervation') for f in ('o','i','a','n')},
               's':pair(STERNALIS2,'Discussion: Arráez-Aybar neurovascular pedicle',STERNALIS3,'Discussion: internal thoracic artery'),
               'a':pair(STERNALIS1,'Discussion: function remains unknown','https://pmc.ncbi.nlm.nih.gov/articles/PMC4644838/','Discussion: function not known / proposed actions')})

# Parts receive their own evidence; no silent parent-function inheritance.
for pkey,p in MUSCLE_TEMPLATES['thorax_pectoralis_major']['parts'].items():
    p['fieldRefs']={f:pair(KH+'major-pectoralis-muscle','Origin and insertion: '+p['lat'],GP,'Pectoralis major: clavicular / sternocostal / abdominal origin; insertion') for f in ('o','i','x') if f in p}
for pkey,p in MUSCLE_TEMPLATES['thorax_diaphragm']['parts'].items():
    p['fieldRefs']={f:pair(KH+'diaphragm','Origins and insertions: '+p['lat'],GT,'Diaphragm: sternal, costal and lumbar parts') for f in ('o','i')}

# Physiological actions are region-dependent, not identical for every fascicle.
internal=MUSCLE_TEMPLATES['thorax_intercostales_interni']
internal['a']='Поддерживают межрёберные промежутки. Межкостные пучки преимущественно помогают выдоху, межхрящевые (парастернальные) — вдоху.'
internal['fieldRefs']['a']=[ref(KH+'internal-intercostal-muscles','Function: support'),ref(UAMS,'internal intercostal, Action: support'),ref(HUMAN_INTERCOSTALS,'Introduction; Discussion: respiratory mechanical advantage'),ref(VT_RESP,'Mechanics of Breathing, diagram: internal intercostals except interchondral part')]
internal['note']+=' Действие зависит от области пучка; единая функция «только выдох» для всей мышцы была бы упрощением.'
internal['noteRefs'] += [ref(HUMAN_INTERCOSTALS,'Abstract; Discussion'),ref(VT_RESP,'Mechanics of Breathing')]
MUSCLE_TEMPLATES['thorax_intercostales_intimi']['note']+=' Kenhub отдельно подчёркивает, что точная функция этого слоя не установлена окончательно.'
MUSCLE_TEMPLATES['thorax_intercostales_intimi']['fieldStatus']['a']='discussed_two_sources'
interspinales=MUSCLE_TEMPLATES['thorax_interspinales_thoracis']
interspinales['a']='В таблице Loyola указана помощь разгибанию позвоночника; вклад небольших грудных пучков точно не установлен.'
interspinales['note']+=' Kenhub подчёркивает неопределённость функции и относит выраженное действие преимущественно к шейному и поясничному отделам. Функция грудных пучков не приравнивается к функции всех межостистых мышц.'
interspinales['fieldStatus']['a']='discussed_two_sources'
MUSCLE_TEMPLATES['thorax_levatores_costarum']['fieldStatus']['a']='discussed_two_sources'
for key in ('thorax_serratus_posterior_superior','thorax_serratus_posterior_inferior','thorax_sternalis'):
    MUSCLE_TEMPLATES[key]['fieldStatus']['a']='discussed_two_sources'

# Associated structures are textual features, never fabricated mesh parts.
DIAPHRAGM_FEATURE_NOTE='Учебное описание. Отдельной размеченной геометрии и проверенного контура этого образования в текущей модели нет.'
def diaphragm_feature(number,ru,lat,x,refs,note=''):
    return dict(code='A04.4.02.'+number,ru=ru,lat=lat,x=x,refs=refs,
                noModel=True,modelNote=DIAPHRAGM_FEATURE_NOTE,note=note,
                evidenceStatus='checked_two_sources',geometryValidated=False)

MUSCLE_TEMPLATES['thorax_diaphragm']['features']=[
    diaphragm_feature('003','Правая ножка','crus dextrum',
      'Прикрепляется к телам L1–L3 и соответствующим межпозвоночным дискам.',
      pair(GT,'Diaphragm: crura, right crus',TMA,'Anatomical Position and Attachments: right crus')),
    diaphragm_feature('004','Левая ножка','crus sinistrum',
      'Прикрепляется к телам L1–L2 и соответствующим межпозвоночным дискам.',
      pair(GT,'Diaphragm: crura, left crus',TMA,'Anatomical Position and Attachments: left crus')),
    diaphragm_feature('005','Срединная дугообразная связка','lig. arcuatum medianum',
      'Соединяет медиальные края ножек дугой впереди аорты.',
      pair(GT,'Diaphragm: tendinous arch across front of aorta',TTU,'Questions 3 and 23: median arcuate ligament / aortic hiatus')),
    diaphragm_feature('006','Медиальная дугообразная связка','lig. arcuatum mediale',
      'Фасциальная дуга над большой поясничной мышцей.',
      pair(GT,'Diaphragm: medial lumbocostal arch',TTU,'Questions 3 and 20: medial arcuate ligament')),
    diaphragm_feature('007','Латеральная дугообразная связка','lig. arcuatum laterale',
      'Фасциальная дуга над квадратной мышцей поясницы между поперечным отростком L1 и XII ребром.',
      pair(GT,'Diaphragm: lateral lumbocostal arch',TTU,'Questions 3 and 20: lateral arcuate ligament')),
    diaphragm_feature('010','Аортальное отверстие','hiatus aorticus',
      'Проход позади диафрагмы между ножками; через него проходят аорта и грудной проток. Учебный ориентир — уровень T12.',
      pair(GT,'Diaphragm: aortic hiatus',TTU,'Question 23: aortic hiatus')),
    diaphragm_feature('011','Пищеводное отверстие','hiatus oesophageus',
      'Отверстие в мышечной части для пищевода и блуждающих стволов. Учебный ориентир — уровень T10.',
      pair(GT,'Diaphragm: esophageal hiatus',KH+'diaphragm','Structure and relations; openings table')),
    diaphragm_feature('012','Диафрагмально-пищеводная связка','lig. phrenicooesophageale',
      'Соединительная ткань, связывающая пищевод с диафрагмой в области пищеводного отверстия.',
      pair('https://pmc.ncbi.nlm.nih.gov/articles/PMC2548324/','Phrenoesophageal membrane: fixation of esophagogastric region to diaphragm','https://pmc.ncbi.nlm.nih.gov/articles/PMC7263794/','Normal esophageal anatomy: endoabdominal fascia and phrenoesophageal ligament')),
    diaphragm_feature('013','Сухожильный центр','centrum tendineum',
      'Центральная сухожильная область, к которой сходятся мышечные пучки диафрагмы.',
      pair(GT,'Diaphragm: central tendon',KH+'diaphragm','Structure and relations: three muscular parts insert into central tendon')),
    diaphragm_feature('014','Отверстие полой вены','foramen venae cavae',
      'Отверстие в сухожильном центре для нижней полой вены.',
      pair(GT,'Diaphragm: vena caval foramen',KH+'diaphragm','Structure and relations: caval foramen through central tendon')),
    diaphragm_feature('015','Грудино-рёберный треугольник','trigonum sternocostale',
      'Промежуток между грудинной и рёберной частями диафрагмы.',
      pair('https://pmc.ncbi.nlm.nih.gov/articles/PMC3846937/','Abdominothoracic continuum; Figure 7: gaps between sternal and costal origins','https://pmc.ncbi.nlm.nih.gov/articles/PMC9877484/','Discussion: border between costal and sternal fibers, sternocostal triangle')),
    diaphragm_feature('016','Пояснично-рёберный треугольник','trigonum lumbocostale',
      'Область между поясничной и рёберной частями; выраженность мышечных пучков здесь изменчива.',
      pair('https://pmc.ncbi.nlm.nih.gov/articles/PMC3731110/','Anatomy and anatomic connections: costal and lumbar tracts, Bochdalek triangle','https://pmc.ncbi.nlm.nih.gov/articles/PMC9877484/','Discussion: lumbocostal triangles and interindividual differences')),
    diaphragm_feature('017','Диафрагмальная фасция','fascia diaphragmatica',
      'Фасциальное покрытие диафрагмы. Слои покрытий и их связи будут рассматриваться отдельно от мышечной сетки.',
      pair('https://pmc.ncbi.nlm.nih.gov/articles/PMC3846937/','Abdominothoracic continuum: fasciae lining superior and inferior diaphragm','https://ifaa.unifr.ch/Public/TNAEntryPage/ref/Musil2019.pdf','Diaphragma: superior and inferior fascial coverings'),
      note='Названия верхнего и нижнего фасциальных слоёв различаются между редакциями терминологии; здесь сохранён термин TA98 без присвоения фасции поверхности модели.')
]

def finalize():
    for key,m in MUSCLE_TEMPLATES.items():
        nomenclature=IFAA_BACK if m['code'].startswith('A04.3') else IFAA_DIAPHRAGM if m['code'].startswith('A04.4.02') else IFAA
        refs=[r for rr in m['fieldRefs'].values() for r in rr]+m.get('noteRefs',[])
        refs += [r for p in m.get('parts',{}).values() for rr in p.get('fieldRefs',{}).values() for r in rr]
        refs += [r for feature in m.get('features',[]) for r in feature['refs']]
        refs += [dict(title='TA98: номенклатура',url=nomenclature,locator=m['code']),dict(title='Колесников, 2003',url=BOOK_URL,locator='С. 45–48; '+m['code'])]
        m['refs']=list({(r['url'],r['locator']):r for r in refs}.values())
        EVIDENCE[key]=dict(code=m['code'],fields=m['fieldRefs'],fieldStatus=m['fieldStatus'],
            note=m.get('note',''),noteRefs=m.get('noteRefs',[]),noModel=m.get('noModel',False),
            geometryValidated=False,features=deepcopy(m.get('features',[])),parts={pk:dict(code=p.get('code'),fields=p.get('fieldRefs',{}),noModel=p.get('noModel',False)) for pk,p in m.get('parts',{}).items()})

finalize()
GROUP_TEMPLATES=set(MUSCLE_TEMPLATES)-SIDED_TEMPLATES
assert len(MUSCLE_TEMPLATES)==26
assert len(SIDED_TEMPLATES)==17

if __name__=='__main__':
    import json
    from pathlib import Path
    fixture=json.loads(Path('verify/ifaa-thorax-muscles.json').read_text(encoding='utf-8'))
    output=dict(version=1,checked='2026-10-13',templates=len(MUSCLE_TEMPLATES),
        instances=2*len(SIDED_TEMPLATES)+len(GROUP_TEMPLATES),evidence=EVIDENCE,
        independentAnatomistAcceptance=False,completeGeometryClaim=False,
        nomenclatureExceptions=fixture.get('nomenclatureExceptions',{}),
        correctionNotes=fixture.get('correctionNotes',{}),
        sourceModelNameMapping={'thorax_iliocostalis_thoracis':dict(sourceName='iliocostalis thoracis',displayCode='A04.3.02.005',displayLatin='m. iliocostalis',
          rejectedAutomaticMapping='A04.3.02.008',reason='The TA98 pars thoracica belongs to m. iliocostalis lumborum; equivalence to the source mesh has not been established.')},
        scope='Костно-мышечный учебный модуль грудной области; сосудистые поля перечисляют проверенные основные источники, а не полный сосудистый атлас.')
    Path('research/thorax-muscle-evidence.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(MUSCLE_TEMPLATES)} templates; {output["instances"]} cards')

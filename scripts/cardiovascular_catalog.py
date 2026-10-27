"""Cardiovascular catalogue, separate from skeletal muscles and bone landmarks.

Source identity is not an anatomical or runtime admission. Admissions live in
cardiovascular_admissions.json; missing geometry stays explicit.
"""
SOURCES = {
 'heart':dict(title='OpenStax — Heart Anatomy',url='https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy',locator='Location; chambers, septa, valves; coronary circulation'),
 'nih':dict(title='NHLBI — What the Heart Looks Like',url='https://www.nhlbi.nih.gov/health/heart/anatomy',locator='Heart chambers; heart tissue; labelled interior diagram'),
 'flow':dict(title='NHLBI — How Blood Flows',url='https://www.nhlbi.nih.gov/health/heart/blood-flow',locator='Chambers, valves and pulmonary/systemic circuits'),
 'vessels':dict(title='OpenStax — Circulatory Pathways',url='https://openstax.org/books/anatomy-and-physiology-2e/pages/20-5-circulatory-pathways',locator='Pulmonary circulation; aorta and branches; systemic veins; hepatic portal system'),
 'aorta':dict(title='NCBI Bookshelf — Aorta',url='https://www.ncbi.nlm.nih.gov/books/NBK537319/',locator='Structure and Function; arch, thoracic and abdominal divisions'),
 'abdomen':dict(title='NCBI Bookshelf — Abdominal Aorta',url='https://www.ncbi.nlm.nih.gov/books/NBK525964/',locator='Major visceral and terminal branches'),
 'coronary':dict(title='NCBI Bookshelf — Coronary Circulation',url='https://www.ncbi.nlm.nih.gov/books/NBK482413/',locator='Coronary origins, anterior interventricular and circumflex branches'),
 'svc':dict(title='NCBI Bookshelf — Superior Vena Cava',url='https://www.ncbi.nlm.nih.gov/books/NBK545255/',locator='Formation from brachiocephalic veins; drainage; variations'),
 'ivc':dict(title='NCBI Bookshelf — Inferior Vena Cava',url='https://www.ncbi.nlm.nih.gov/books/NBK482353/',locator='Common iliac formation; renal tributaries; right atrium'),
 'ta':dict(title='FIPAT — TA98: cor',url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/12.1.00.001%20Entity%20TA98%20EN.htm',locator='Nomenclature A12; term check only, not geometry'),
 'arm':dict(title='NCBI Bookshelf — Forearm Arteries',url='https://www.ncbi.nlm.nih.gov/books/NBK545155/',locator='Brachial bifurcation; radial/ulnar arteries; variation'),
 'brachial':dict(title='NCBI Bookshelf — Brachial Artery',url='https://www.ncbi.nlm.nih.gov/books/NBK537145/',locator='Continuation of axillary artery; terminal branches'),
 'leg':dict(title='NCBI Bookshelf — Lower Limb Arteries',url='https://www.ncbi.nlm.nih.gov/books/NBK544319/',locator='Femoral, popliteal, tibial and fibular routes'),
 'armveins':dict(title='NCBI Bookshelf — Venous drainage of upper extremities',url='https://www.ncbi.nlm.nih.gov/books/NBK27370/',locator='Deep and superficial venous routes'),
 'legveins':dict(title='NCBI Bookshelf — Popliteal Vein',url='https://www.ncbi.nlm.nih.gov/books/NBK541078/',locator='Tibial/fibular tributaries, small saphenous and femoral continuation'),
 'greatsaphenous':dict(title='NCBI Bookshelf — Saphenous Vein',url='https://www.ncbi.nlm.nih.gov/books/NBK532880/',locator='Great saphenous course and femoral junction'),
 'azygos':dict(title='NCBI Bookshelf — Azygos Veins',url='https://www.ncbi.nlm.nih.gov/books/NBK554430/',locator='Azygos and hemiazygos drainage'),
 'portal':dict(title='Schmidt et al. — Portal vein anatomy and variants',url='https://pmc.ncbi.nlm.nih.gov/articles/PMC3036482/',locator='Normal anatomy and anatomical variations; original morphologic/imaging review'),
 'papillary':dict(title='NCBI Bookshelf — Anatomy, Thorax, Heart Papillary Muscles',url='https://www.ncbi.nlm.nih.gov/books/NBK557802/',locator='Structure and Function: papillary muscles of both ventricles, chordae tendineae'),
 'cardiacveins':dict(title='NCBI Bookshelf — Anatomy, Thorax, Coronary Sinus',url='https://www.ncbi.nlm.nih.gov/books/NBK557566/',locator='Structure and Function: great, middle cardiac and posterior left ventricular veins; anterior cardiac veins'),
 'ta_heart':dict(title='FIPAT — TA98: heart (A12.1)',url='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH3614%20A2F%20EN.htm',locator='A12.1.02.017–019, A12.1.04.007–008, A12.1.04.012–015; term and FMA identity only'),
 'ta_coronary':dict(title='FIPAT — TA98: coronary arteries (A12.2.03)',url='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/EN/TAH3774%20A4%20EN.htm',locator='A12.2.03.101–111 (right), A12.2.03.201–214 (left; list TAH3785); term and FMA identity only'),
 'ta_cardiacveins':dict(title='FIPAT — TA98: veins of heart (A12.3.01)',url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/12.3.01.003%20Entity%20TA98%20EN.htm',locator='A12.3.01.002–012 entity pages; term and FMA identity only'),
}
NOTICE='Учебные модели BodyParts3D. Точные внутренние границы, просветы и соединения не подтверждены.'
CARDS={}
def add(key,ru,lat,system='heart',fma=None,sec='trunk',side='unseparated',facts=None,refs=None,**kw):
    id='cv_'+key
    assert id not in CARDS
    CARDS[id]=dict(ru=ru,lat=lat,system=system,g='cv_'+sec+'_'+system,sub='cardiovascular',side=side,
        facts=facts or {},refs=[SOURCES[k] for k in (refs or ['heart','nih'])],fma=fma,**kw)
    return id

add('heart','Сердце','cor',fma='FMA7274',facts={'Положение':'Средостение; позади грудины.','Модель':'Общая стенка сердца. Камеры выделены масками граней этой модели по разметке Z-Anatomy; перегородки отдельно не выделены.'})
for key,ru,lat,side,role in [
 ('atrium_right','Правое предсердие','atrium dextrum','right','Принимает системный венозный возврат.'),
 ('atrium_left','Левое предсердие','atrium sinistrum','left','Принимает кровь лёгочных вен.'),
 ('ventricle_right','Правый желудочек','ventriculus dexter','right','Выход в лёгочный ствол.'),
 ('ventricle_left','Левый желудочек','ventriculus sinister','left','Выход в аорту.'),
 ('septum_atrial','Межпредсердная перегородка','septum interatriale','unseparated','Разделяет предсердия.'),
 ('septum_ventricular','Межжелудочковая перегородка','septum interventriculare','unseparated','Разделяет желудочки.')]:
    add(key,ru,lat,side=side,partOf='cv_heart',facts={'Отношение':role})
for key,ru,lat,fma,role in [
 ('valve_tricuspid','Правый предсердно-желудочковый клапан','valva atrioventricularis dextra; valva tricuspidalis','FMA7234','Правое предсердие → правый желудочек.'),
 ('valve_mitral','Левый предсердно-желудочковый клапан','valva atrioventricularis sinistra; valva mitralis','FMA7235','Левое предсердие → левый желудочек.'),
 ('valve_aortic','Клапан аорты','valva aortae',None,'Левый желудочек → аорта.'),
 ('valve_pulmonary','Клапан лёгочного ствола','valva trunci pulmonalis','FMA7246','Правый желудочек → лёгочный ствол.')]:
    add(key,ru,lat,fma=fma,partOf='cv_heart',side='right' if key=='valve_tricuspid' else 'left' if key=='valve_mitral' else 'unseparated',facts={'Положение':role},refs=['heart','flow'],modelScope='Статическая модель. Для предсердно-желудочковых клапанов исходный набор включает хорды; их отдельные границы не размечены.')

def artery(key,ru,lat,fma=None,origin=None,supply='',sec='trunk',side='unseparated',refs=None,**kw):
    if kw.get('partOf'):kw['partOf']=kw['partOf'].replace('cv_aorta','cv_a_aorta')
    return add('a_'+key,ru,lat,'arteries',fma,sec,side,{'Область кровоснабжения':supply} if supply else {},refs or ['vessels','aorta'],origin=(('cv_' if origin.startswith('ventricle_')else 'cv_a_')+origin if origin else None),**kw)
artery('aorta','Аорта','aorta',origin='ventricle_left',supply='Большой круг кровообращения.')
artery('aorta_ascending','Восходящая аорта','aorta ascendens','FMA3736','ventricle_left',partOf='cv_aorta')
artery('aorta_arch','Дуга аорты','arcus aortae','FMA3768','aorta_ascending',partOf='cv_aorta')
artery('aorta_descending','Нисходящая аорта','aorta descendens','FMA3784','aorta_arch',partOf='cv_aorta',factsNote='Исходный меш объединяет грудной и брюшной отделы; они выделены масками граней по уровню нижнего края тела T12 (аортальное отверстие диафрагмы).')
artery('aorta_thoracic','Грудная часть аорты','pars thoracica aortae',origin='aorta_arch',partOf='cv_aorta_descending')
artery('aorta_abdominal','Брюшная часть аорты','pars abdominalis aortae',origin='aorta_thoracic',partOf='cv_aorta_descending',refs=['vessels','abdomen'])
artery('pulmonary_trunk','Лёгочный ствол','truncus pulmonalis',origin='ventricle_right',supply='Малый круг; лёгочные артерии.',refs=['vessels','flow'])
# The combined pulmonary tree is a candidate, not a renamed isolated trunk.
artery('pulmonary_arteries','Лёгочные артерии — объединённый набор','arteriae pulmonales','FMA66326','pulmonary_trunk',supply='Лёгкие.',refs=['vessels','flow'],modelScope='Объединённый набор; ствол и стороны требуют сегментации.')
artery('coronary_right','Правая венечная артерия','arteria coronaria dextra','FMA3802','aorta_ascending','Сердце.',side='right',refs=['heart','coronary'])
artery('coronary_left','Левая венечная артерия','arteria coronaria sinistra','FMA4685','aorta_ascending','Сердце.',side='left',refs=['heart','coronary'])
artery('coronary_anterior_interventricular','Передняя межжелудочковая ветвь','ramus interventricularis anterior','FMA3862nsn','coronary_left','Желудочки и перегородка.',refs=['heart','coronary'])
artery('coronary_circumflex','Огибающая ветвь','ramus circumflexus','FMA3895','coronary_left','Левые отделы сердца.',side='left',refs=['heart','coronary'])
artery('brachiocephalic','Плечеголовной ствол','truncus brachiocephalicus','FMA3932nsn','aorta_arch',side='right')
for side,adj,la,cca,sub in [('right','Правая','dextra','FMA3941','FMA3953'),('left','Левая','sinistra','FMA4058','FMA4694')]:
    origin='brachiocephalic' if side=='right' else 'aorta_arch'
    artery('carotid_common_'+side,adj+' общая сонная артерия','arteria carotis communis '+la,cca,origin,'Голова и шея.',sec='neck',side=side)
    artery('subclavian_'+side,adj+' подключичная артерия','arteria subclavia '+la,sub,origin,'Плечевой пояс, шея и верхняя конечность.',sec='neck',side=side)
for key,ru,lat,fma,supply in [
 ('celiac','Чревный ствол','truncus coeliacus','FMA50737','Верхние органы брюшной полости.'),
 ('mesenteric_superior','Верхняя брыжеечная артерия','arteria mesenterica superior','FMA14749','Средняя кишка.'),
 ('mesenteric_inferior','Нижняя брыжеечная артерия','arteria mesenterica inferior','FMA14750','Задняя кишка.')]:
    artery(key,ru,lat,fma,'aorta_abdominal',supply,refs=['vessels','abdomen'])
for side,adj,la,renal,iliac,external,internal in [('right','Правая','dextra','FMA14752','FMA14765','FMA18806','FMA18809'),('left','Левая','sinistra','FMA14753','FMA14766','FMA18807','FMA18810')]:
    artery('renal_'+side,adj+' почечная артерия','arteria renalis '+la,renal,'aorta_abdominal','Почка.',side=side,refs=['vessels','abdomen'])
    artery('iliac_common_'+side,adj+' общая подвздошная артерия','arteria iliaca communis '+la,iliac,'aorta_abdominal','Таз и нижняя конечность.',sec='leg',side=side,refs=['vessels','abdomen'])
    artery('iliac_external_'+side,adj+' наружная подвздошная артерия','arteria iliaca externa '+la,external,'iliac_common_'+side,sec='leg',side=side,refs=['vessels','abdomen'])
    artery('iliac_internal_'+side,adj+' внутренняя подвздошная артерия','arteria iliaca interna '+la,internal,'iliac_common_'+side,'Таз.',sec='leg',side=side,refs=['vessels','abdomen'])

def vein(key,ru,lat,fma=None,drains=None,area='',sec='trunk',side='unseparated',refs=None,**kw):
    return add('v_'+key,ru,lat,'veins',fma,sec,side,{'Венозный отток':area} if area else {},refs or ['vessels','ivc'],drainsTo=(('cv_' if drains.startswith('atrium_')else 'cv_v_')+drains if drains else None),**kw)
vein('cava_superior','Верхняя полая вена','vena cava superior','FMA4720','atrium_right','Верхняя половина тела.',refs=['vessels','svc'])
vein('cava_inferior','Нижняя полая вена','vena cava inferior','FMA10951','atrium_right','Нижняя половина тела.')
vein('pulmonary_veins','Лёгочные вены — объединённый набор','venae pulmonales','FMA66643','atrium_left','Лёгкие.',refs=['vessels','flow'],modelScope='Объединённый набор; отдельные устья и стороны не размечены.')
for side,adj,la,brachio,jug,sub,renal,iliac,external,internal in [
 ('right','Правая','dextra','FMA4751','FMA4754','FMA4755','FMA14335','FMA21387','FMA18885','FMA18887'),
 ('left','Левая','sinistra','FMA4761','FMA4762','FMA4763','FMA14336','FMA21388','FMA18886','FMA18888')]:
    vein('brachiocephalic_'+side,adj+' плечеголовная вена','vena brachiocephalica '+la,brachio,'cava_superior',side=side,refs=['vessels','svc'])
    vein('jugular_internal_'+side,adj+' внутренняя яремная вена','vena jugularis interna '+la,jug,'brachiocephalic_'+side,'Голова и шея.',sec='neck',side=side,refs=['vessels','svc'])
    vein('subclavian_'+side,adj+' подключичная вена','vena subclavia '+la,sub,'brachiocephalic_'+side,'Верхняя конечность.',sec='neck',side=side,refs=['vessels','svc'])
    vein('renal_'+side,adj+' почечная вена','vena renalis '+la,renal,'cava_inferior','Почка.',side=side)
    vein('iliac_common_'+side,adj+' общая подвздошная вена','vena iliaca communis '+la,iliac,'cava_inferior','Таз и нижняя конечность.',sec='leg',side=side)
    vein('iliac_external_'+side,adj+' наружная подвздошная вена','vena iliaca externa '+la,external,'iliac_common_'+side,sec='leg',side=side)
    vein('iliac_internal_'+side,adj+' внутренняя подвздошная вена','vena iliaca interna '+la,internal,'iliac_common_'+side,'Таз.',sec='leg',side=side)

GROUPS=[dict(id='cv_'+sec+'_'+system,title=title,sec=sec,region='cardiovascular') for sec in ['trunk','neck','arm','leg'] for system,title in [('heart','Сердце'),('arteries','Артерии'),('veins','Вены')]]

# Priority pathways absent from the identified source meshes remain searchable
# cards, not fabricated tubes. Relations describe the usual adult arrangement.
for side,adj,la in [('right','Правая','dextra'),('left','Левая','sinistra')]:
    for key,name,latin,parent,supply in [
      ('axillary','подмышечная','axillaris','subclavian','Подмышечная область и верхняя конечность.'),
      ('brachial','плечевая','brachialis','axillary','Плечо.'),
      ('radial','лучевая','radialis','brachial','Предплечье и кисть.'),
      ('ulnar','локтевая','ulnaris','brachial','Предплечье и кисть.')]:
        artery(key+'_'+side,adj+' '+name+' артерия','arteria '+latin+' '+la,origin=parent+'_'+side,supply=supply,sec='arm',side=side,refs=['vessels','arm' if key in ['radial','ulnar']else 'brachial'])
    for key,name,latin,parent in [
      ('femoral','бедренная','femoralis','iliac_external'),('popliteal','подколенная','poplitea','femoral'),
      ('tibial_anterior','передняя большеберцовая','tibialis anterior','popliteal'),
      ('tibial_posterior','задняя большеберцовая','tibialis posterior','popliteal'),
      ('fibular','малоберцовая','fibularis','tibial_posterior')]:
        artery(key+'_'+side,adj+' '+name+' артерия','arteria '+latin+' '+la,origin=parent+'_'+side,sec='leg',side=side,refs=['vessels','leg'])
    for key,name,latin,dest in [
      ('axillary','подмышечная вена','vena axillaris','subclavian'),
      ('cephalic','латеральная подкожная вена руки','vena cephalica','axillary'),
      ('basilic','медиальная подкожная вена руки','vena basilica','axillary')]:
        vein(key+'_'+side,adj+' '+name,latin+' '+la,drains=dest+'_'+side,sec='arm',side=side,refs=['vessels','armveins'])
    vein('brachial_'+side,('Правые' if side=='right'else 'Левые')+' плечевые вены','venae brachiales '+('dextrae'if side=='right'else 'sinistrae'),drains='axillary_'+side,sec='arm',side=side,refs=['vessels','armveins'])
    for key,name,latin,dest in [
      ('femoral','бедренная','femoralis','iliac_external'),('popliteal','подколенная','poplitea','femoral'),
      ('saphenous_great','большая подкожная','saphena magna','femoral'),
      ('saphenous_small','малая подкожная','saphena parva','popliteal')]:
        vein(key+'_'+side,adj+' '+name+' вена','vena '+latin+' '+la,drains=dest+'_'+side,sec='leg',side=side,refs=['vessels','greatsaphenous' if key=='saphenous_great'else 'legveins'])
vein('azygos','Непарная вена','vena azygos',drains='cava_superior',refs=['vessels','azygos'])
vein('hemiazygos','Полунепарная вена','vena hemiazygos',drains='azygos',side='left',refs=['vessels','azygos'])
vein('portal','Воротная вена печени','vena portae hepatis',area='Органы пищеварения и селезёнка → печень.',refs=['vessels','portal'],factsNote='Воротная вена направляется к синусоидам печени; прямой связи с нижней полой веной в каталоге нет.')
vein('splenic','Селезёночная вена','vena splenica','FMA14331','portal',refs=['vessels','portal'])
vein('mesenteric_superior','Верхняя брыжеечная вена','vena mesenterica superior','FMA14332','portal',refs=['vessels','portal'])
for key,ru,lat,fma in [('gastric_left','Левая желудочная артерия','arteria gastrica sinistra','FMA14768'),('hepatic_common','Общая печёночная артерия','arteria hepatica communis','FMA14771'),('splenic','Селезёночная артерия','arteria splenica','FMA14773')]:
    artery(key,ru,lat,fma,'celiac',refs=['vessels','abdomen'])

# LOG-20261026-03: further BodyParts3D 3.0 heart parts. TA98 entity pages give the same FMA identifiers.
for key,ru,lat,fma,side,ventricle,code in [
 ('papillary_rv_anterior','Передняя сосочковая мышца правого желудочка','musculus papillaris anterior (ventriculi dextri)','FMA7260','right','ventricle_right','A12.1.02.017'),
 ('papillary_rv_posterior','Задняя сосочковая мышца правого желудочка','musculus papillaris posterior (ventriculi dextri)','FMA7261','right','ventricle_right','A12.1.02.018'),
 ('papillary_rv_septal','Перегородочная сосочковая мышца правого желудочка','musculus papillaris septalis','FMA7262','right','ventricle_right','A12.1.02.019'),
 ('papillary_lv_posterior','Задняя сосочковая мышца левого желудочка','musculus papillaris posterior (ventriculi sinistri)','FMA7266','left','ventricle_left','A12.1.04.008'),
 ('papillary_lv_unspecified','Сосочковая мышца левого желудочка (без уточнения в источнике)','musculus papillaris (ventriculi sinistri)','FMA9352nsn','left','ventricle_left',None)]:
    add(key,ru,lat,fma=fma,side=side,partOf='cv_'+ventricle,refs=['heart','papillary','ta_heart'],taCode=code,
        facts={'Отношение':'Отходит от стенки желудочка; через сухожильные хорды удерживает створки предсердно-желудочкового клапана.'},
        **({'factsNote':'Источник называет её «papillary muscle of left ventricle, nsn» без уточнения передней или задней. По положению она лежит кпереди от задней сосочковой мышцы, но название по положению не присваивается.'} if fma=='FMA9352nsn' else {}))
for key,ru,lat,fma,origin,supply,side,code,note in [
 ('coronary_right_marginal','Правая краевая ветвь','ramus marginalis dexter','FMA3818','coronary_right','Правый желудочек по правому краю сердца.','right','A12.2.03.106',None),
 ('coronary_posterior_interventricular','Задняя межжелудочковая ветвь','ramus interventricularis posterior','FMA3840nsn','coronary_right','Задние отделы обоих желудочков и перегородки.','unseparated','A12.2.03.108','Отходит от правой венечной артерии при правом типе кровоснабжения; источник модели — правая венечная артерия.'),
 ('coronary_right_posterolateral','Правая заднебоковая ветвь','ramus posterolateralis dexter','FMA76994','coronary_right','Задняя стенка левого желудочка.','right','A12.2.03.111','В TA98 термин в скобках: ветвь непостоянная и зависит от типа кровоснабжения сердца.'),
 ('coronary_septal_right','Межжелудочковые перегородочные ветви правой венечной артерии','rami interventriculares septales (arteriae coronariae dextrae)','FMA71669','coronary_right','Задняя часть межжелудочковой перегородки.','unseparated','A12.2.03.109',None),
 ('coronary_septal_left','Межжелудочковые перегородочные ветви передней межжелудочковой ветви','rami interventriculares septales (rami interventricularis anterioris)','FMA71670','coronary_anterior_interventricular','Передние две трети межжелудочковой перегородки.','unseparated','A12.2.03.205',None)]:
    artery(key,ru,lat,fma,origin,supply,side=side,refs=['coronary','heart','ta_coronary'],taCode=code,**({'factsNote':note} if note else {}))
vein('coronary_sinus','Венечная пазуха','sinus coronarius',drains='atrium_right',area='Большая часть венозной крови стенки сердца.',refs=['cardiacveins','heart','ta_cardiacveins'],taCode='A12.3.01.002',
     factsNote='Лежит в задней части венечной борозды и открывается в правое предсердие.')
for key,ru,lat,fma,dest,area,code in [
 ('cardiac_great','Большая вена сердца','vena cardiaca magna','FMA4707','coronary_sinus','Передняя межжелудочковая борозда, затем венечная борозда; продолжается в венечную пазуху.','A12.3.01.003'),
 ('cardiac_middle','Средняя вена сердца','vena cardiaca media; vena interventricularis posterior','FMA4713','coronary_sinus','Задняя межжелудочковая борозда от верхушки к венечной пазухе.','A12.3.01.009'),
 ('ventricle_left_posterior','Задние вены левого желудочка','venae ventriculi sinistri posteriores','FMA76751','coronary_sinus','Задняя стенка левого желудочка.','A12.3.01.006'),
 ('cardiac_anterior','Передние вены правого желудочка','venae ventriculi dextri anteriores; venae cardiacae anteriores','FMA71567','atrium_right','Передняя стенка правого желудочка; впадают прямо в правое предсердие.','A12.3.01.012')]:
    vein(key,ru,lat,fma,dest,area,refs=['cardiacveins','heart','ta_cardiacveins'],taCode=code)

def validate():
    for id,c in CARDS.items():
        for relation in ['partOf','origin','drainsTo']:
            if c.get(relation):assert c[relation] in CARDS,(id,relation,c[relation])
        assert len(c['refs'])>=2 and c['side'] in ['left','right','unseparated']
    return True
validate()

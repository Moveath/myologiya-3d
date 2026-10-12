"""Topographic facts for additional neurocranial markers.

All prose is original Russian summary. Anatomy Standard illustrations are consulted
as reference only; their images/meshes are NOT redistributed in the atlas.
Gray 1918 is public domain. Independent original anatomical studies are used for
variants and narrow canals; the evidence locators state which facts were checked.
Geometric observations/limitations are separately stored on each coordinate row.
"""

def ref(title, url, locator):
    return {'title': title, 'url': url, 'locator': locator}

AS = {b: ref('Anatomy Standard — '+title,
    f'https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-{latin}.html',
    'Авторские подписанные виды кости: передний, задний, верхний, нижний и косые ракурсы.')
    for b, title, latin in [('frontal','лобная кость','frontale'),('parietal','теменная кость','parietale'),
    ('occipital','затылочная кость','occipitale'),('sphenoid','клиновидная кость','sphenoidale'),
    ('ethmoid','решётчатая кость','ethmoidale')]}
GRAY = {b:ref('Gray, Anatomy of the Human Body (1918) — '+title,
    'https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/'+slug+'/', section)
    for b,title,slug,section in [
    ('frontal','The Frontal Bone','5a-3-the-frontal-bone','Squama; Orbital or Horizontal Part; Surfaces; Borders, pp.135–137.'),
    ('parietal','The Parietal Bone','5a-2-the-parietal-bone','Surfaces, Borders, Angles, pp.133–134.'),
    ('occipital','The Occipital Bone','5a-1-the-occipital-bone','Lateral Parts; Basilar Part; Squama, pp.129–132.'),
    ('sphenoid','The Sphenoid Bone','5a-5-the-sphenoid-bone','Body; Great Wings; Small Wings; Pterygoid Processes; Sphenoidal Conchae, pp.147–152.'),
    ('ethmoid','Ethmoid Bone','5a-6-ethmoid-bone','Cribriform Plate; Perpendicular Plate; Labyrinth, pp.153–155.')
]}
# Accessible transcription of the same 1918 frontal chapter, not another source.
GRAY['frontal']['url']='https://wikimd.org/wiki/The_Frontal_Bone'
# Complete public-domain transcription was read in Saylor's osteology course PDF.
# PDF pages differ from the printed 1918 page numbers retained in the locators.
GRAY_PDF='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
for _bone,_page in [('occipital',76),('parietal',82),('frontal',85),('sphenoid',102),('ethmoid',110)]:
    GRAY[_bone]['url']=GRAY_PDF+f'#page={_page}'
    GRAY[_bone]['locator']+=f' Электронная перепечатка Saylor: начиная со страницы PDF {_page}.'
KEN = {b:ref('Kenhub — '+b+' bone (открытая статья)',
    f'https://www.kenhub.com/en/library/anatomy/the-{b}-bone',
    'Anatomy; surfaces, borders and component parts. Не используются платные модели или изображения.')
    for b in AS}
TMA_F=ref('TeachMeAnatomy — The Frontal Bone','https://teachmeanatomy.info/head/osteology/frontal-bone/','Squamous Part; Orbital Part; Nasal Part.')
TMA_O=ref('TeachMeAnatomy — The Occipital Bone','https://teachmeanatomy.info/head/osteology/occipital-bone/','Condylar; Basilar; Squamous parts.')
FRONTAL_NOTCH=ref('Haładaj et al. (2019) — Supraorbital and supratrochlear nerves','https://pmc.ncbi.nlm.nih.gov/articles/PMC6647930/','Materials and Methods: границы supraorbital notch и frontal notch на надглазничном крае; Fig.3–4.')
TROCHLEA=ref('Radiological anatomy of the trochlear spine (2025)','https://pmc.ncbi.nlm.nih.gov/articles/PMC13179243/','Introduction; Results; Fig.1–3: superomedial anterior orbit; fovea and spine.')
MCF=ref('Tayebi Meybodi et al. (2023) — Middle cranial fossa, part I','https://doi.org/10.3389/fsurg.2023.1132774','Bony anatomy: sphenoid body, clinoid processes and sphenoid foramina; Fig.2–4.')
MCP=ref('The Prevalence of the Middle Clinoid Process (2024)','https://pmc.ncbi.nlm.nih.gov/articles/PMC11226267/','Introduction and Fig.1–3: основание у переднелатерального края седла, вариабельность.')
LIMBUS=ref('IMAIOS — Limbus of sphenoid (открытое определение)','https://www.imaios.cn/en/e-anatomy/anatomical-structures/limbus-of-sphenoid-129992','Definition: задняя граница jugum, передняя граница sulcus prechiasmaticus.')
CANALS=ref('Visualisation of the vomerovaginal canal (2019)','https://pmc.ncbi.nlm.nih.gov/articles/PMC6637440/','Osteological study and endoscopic dissection: vomer, vaginal process, palatine; differences between VVC and PVC.')
CANALS2=ref('Simultaneous observation of palatovaginal and vomerovaginal canals (2015)','https://pmc.ncbi.nlm.nih.gov/articles/PMC4658943/','Discussion and Fig.2–3: различение нёбно-влагалищного и сошниково-влагалищного каналов.')
PETROSUM=ref('Correlation Analysis on Accessory Foramina in the Sphenoid Bone (2023)','https://pmc.ncbi.nlm.nih.gov/articles/PMC10670589/','Canaliculus innominatus, Fig.3: между foramen spinosum и foramen ovale.')
PTERYGO=ref('Morphological study of sphenoid ligaments ossification (2023)','https://pmc.ncbi.nlm.nih.gov/articles/PMC10587028/','Introduction and anatomy of pterygospinous ligament: posterior margin of lateral plate, sphenoid spine.')
VAR_OCC=ref('Bergman et al. — Variations of the Occipital Bone','https://www.anatomyatlases.org/AnatomicVariants/SkeletalSystem/Text/OccipitalBone.shtml','Interparietal/Inca bone; paramastoid process; variations around foramen magnum.')
CRANIO=ref('Gray (1918) — Exterior of the Skull',GRAY_PDF+'#page=153','Norma Basalis: basion and opisthion; condylar fossa and canals. Перепечатка Saylor, PDF с.153; craniometry, PDF с.173.')
SINUS_GROOVES=ref('Píšová et al. (2017) — Craniovascular traits','https://www.isita-org.com/Jass/Contents/2017vol95/Pisova/28190005.pdf','Fig.6 and text: внутренний затылочный гребень, затылочный и краевой синусы вокруг большого отверстия.')
GALLI=ref('Académie nationale de médecine — Aile de la crista galli','https://academie-medecine.fr/le-dictionnaire/index.php?q=aile+de+la+crista+galli','Две боковые пластинки у переднего края crista galli, соединение с лобной костью.')
ETHMOID_CT=ref('Whyte & Boeddinghaus (2019) — Maxillary sinus imaging anatomy','https://pmc.ncbi.nlm.nih.gov/articles/PMC6951102/','Infundibulum: uncinate process medial, lamina papyracea lateral; basal lamella separates anterior/posterior ethmoid.')
ETHMOID_STAT=ref('StatPearls — Ethmoid Bone','https://www.ncbi.nlm.nih.gov/books/NBK544328/','Structure and Function; uncinate process and infundibulum.')
SUPREME=ref('Orhan et al. — A surgical view of the superior nasal turbinate (2010)','https://pubmed.ncbi.nlm.nih.gov/20012078/','Cadaveric study: наличие и варианты supreme nasal turbinate, relation to superior turbinate.')
SUPREME2=ref('Supreme Nasal Turbinate as an Additional Surgical Landmark (2020)','https://pmc.ncbi.nlm.nih.gov/articles/PMC7294892/','Endoscopic case and figures: supreme turbinate above superior turbinate.')

DESCRIPTIONS={}
def add(prefix, rows, default_refs):
    for num, text, *other in rows:
        r={'x':text,'refs':other[0] if other else default_refs,'scope':'anatomy'}
        if len(other)>1:r['note']=other[1]
        DESCRIPTIONS[f'A02.1.{prefix}.{num:03d}']=r

add('03',[
 (7,'Сохраняющийся шов по средней линии между правой и левой половинами лобной чешуи. Его наличие у взрослого является вариантом.',[GRAY['frontal'],AS['frontal']]),
 (9,'Отверстие или вырезка в медиальной части надглазничного края.',[AS['frontal'],FRONTAL_NOTCH]),
 (10,'Вырезка или отверстие у перехода надглазничного края в медиальный край глазницы.',[AS['frontal'],FRONTAL_NOTCH]),
 (18,'Небольшое образование у нижнего конца лобного гребня на границе с решётчатой костью.',[GRAY['frontal'],AS['frontal']]),
 (20,'Срединный выступ носовой части, направленный вниз.',[GRAY['frontal'],TMA_F]),
 (24,'Вариабельный небольшой выступ в переднемедиальной области глазницы, рядом с блоковой ямкой.',[GRAY['frontal'],TROCHLEA]),
 (25,'Небольшое углубление переднемедиальной области глазничной поверхности.',[GRAY['frontal'],TROCHLEA]),
 (26,'Углубление в переднелатеральной области глазничной поверхности.',[GRAY['frontal'],TMA_F]),
 (27,'Задний край глазничной части, соединяющийся с клиновидной костью.',[GRAY['frontal'],AS['frontal']]),
 (28,'Вырезка между правой и левой глазничными частями, предназначенная для решётчатой кости.',[GRAY['frontal'],AS['frontal']]),
 (29,'Воздухоносная полость внутри лобной кости над глазницей.',[GRAY['frontal'],TMA_F]),
 (30,'Отверстие лобной пазухи на нижней стороне кости, впереди решётчатой вырезки.',[GRAY['frontal'],AS['frontal']]),
 (31,'Костная перегородка между правой и левой лобными пазухами.',[GRAY['frontal'],TMA_F]),
], [GRAY['frontal'],AS['frontal']])

add('02',[
 (3,'Участок венозной борозды на внутренней поверхности сосцевидного угла.',[GRAY['parietal'],AS['parietal']],
  'В открытой статье Kenhub борозда отнесена к затылочному углу; Gray и подписанный внутренний вид Anatomy Standard помещают её у сосцевидного угла. Здесь принят этот вариант локализации.'),
 (4,'Продольное углубление на внутренней поверхности вдоль сагиттального края.'),
 (5,'Борозда на внутренней поверхности, восходящая от клиновидного угла.'),
 (6,'Ветвящиеся сосудистые борозды на внутренней поверхности кости.'),
 (8,'Верхняя дугообразная линия наружной поверхности.'),
 (9,'Нижняя из двух височных линий наружной поверхности.'),
 (16,'Задневерхний угол на стыке затылочного и сагиттального краёв.'),
 (19,'Небольшое отверстие у заднего отдела сагиттального края; может отсутствовать.'),
], [AS['parietal'],KEN['parietal']])

add('04',[
 (3,'Срединная точка переднего края большого отверстия.',[CRANIO,ref('Académie nationale de médecine — Basion','https://academie-medecine.fr/le-dictionnaire/index.php?q=basion','Point médian du bord antérieur du foramen magnum.')]),
 (4,'Срединная точка заднего края большого отверстия.',[CRANIO,ref('Immersive Surgical Anatomy of the Craniometric Points (2020)','https://pmc.ncbi.nlm.nih.gov/articles/PMC7366040/','Craniometric points, Fig.4B: opisthion and basion.')]),
 (7,'Срединный бугорок нижней поверхности базилярной части.'),
 (8,'Борозда вдоль бокового края базилярной части у каменистой части височной кости.'),
 (13,'Вариант отдельного сохранения верхней части затылочной чешуи.',[GRAY['occipital'],VAR_OCC]),
 (15,'Канал в области ямки позади затылочного мыщелка.',[CRANIO,TMA_O]),
 (16,'Короткий канал у основания затылочного мыщелка.',[AS['occipital'],TMA_O]),
 (17,'Углубление позади затылочного мыщелка.',[CRANIO,TMA_O]),
 (18,'Возвышение верхней поверхности латеральной части над каналом подъязычного нерва.'),
 (19,'Вырезка переднего края яремного отростка; участвует в ограничении яремного отверстия.',[AS['occipital'],TMA_O]),
 (20,'Выступ латеральной части, направленный к височной кости.',[AS['occipital'],TMA_O]),
 (21,'Небольшой выступ яремной вырезки, разделяющий её части.',[GRAY['occipital'],ref('Complete morphometric analysis of jugular foramen (2016)','https://pmc.ncbi.nlm.nih.gov/articles/PMC5111328/','Methods: endocranial aspect, Fig.1 — peak of intrajugular process of occipital bone.')]),
 (24,'Наивысшая из выйных линий, расположенная выше верхней выйной линии.'),
 (26,'Поперечная линия наружной поверхности ниже верхней выйной линии.'),
 (32,'Венозная борозда верхней стороны яремного отростка, продолжающаяся к яремной вырезке.'),
 (33,'Борозда в области внутреннего затылочного гребня.',[SINUS_GROOVES,KEN['occipital']]),
 (34,'Борозда вдоль внутричерепного края большого отверстия.',[SINUS_GROOVES,KEN['occipital']]),
 (35,'Вариабельный выступ нижней стороны яремного отростка.',[GRAY['occipital'],VAR_OCC]),
], [AS['occipital'],GRAY['occipital']])

add('05',[
 (4,'Поперечный край между клиновидным возвышением и предперекрёстной бороздой.',[GRAY['sphenoid'],MCF]),
 (5,'Поперечная борозда впереди бугорка седла.',[AS['sphenoid'],MCF]),
 (8,'Небольшой вариабельный выступ у латерального края бугорка седла.',[MCP,MCF]),
 (11,'Выступ верхнелатерального угла спинки седла.',[AS['sphenoid'],MCF]),
 (12,'Борозда на боковой поверхности тела клиновидной кости.',[AS['sphenoid'],MCF]),
 (13,'Костный гребешок у задней части латерального края сонной борозды.'),
 (16,'Воздухоносная полость внутри тела клиновидной кости.',[AS['sphenoid'],KEN['sphenoid']]),
 (17,'Перегородка между правой и левой клиновидными пазухами.',[GRAY['sphenoid'],KEN['sphenoid']]),
 (18,'Отверстие на передней стенке клиновидной пазухи.'),
 (19,'Тонкая костная пластинка передненижней стенки клиновидной пазухи.'),
 (21,'Канал у основания малого крыла, соединяющий полость черепа с глазницей.',[AS['sphenoid'],MCF]),
 (22,'Выступ заднего края малого крыла около тела клиновидной кости.',[AS['sphenoid'],MCF]),
 (23,'Щель между большим и малым крыльями, латеральнее тела.',[AS['sphenoid'],MCF]),
 (28,'Гребень на границе височной и подвисочной поверхностей большого крыла.'),
 (33,'Верхний край большого крыла, соединяющийся с теменной костью.'),
 (35,'Отверстие у основания большого крыла, ведущее в крылонёбную ямку.',[AS['sphenoid'],MCF]),
 (37,'Вариабельное отверстие большого крыла, расположенное медиальнее овального.',[MCF,PETROSUM]),
 (38,'Небольшое отверстие большого крыла позади и латеральнее овального.',[AS['sphenoid'],MCF]),
 (39,'Вариабельное небольшое отверстие между овальным и остистым отверстиями.',[MCF,PETROSUM]),
 (40,'Костный выступ заднелатерального участка большого крыла.'),
 (41,'Борозда между областью ости клиновидной кости и корнем медиальной крыловидной пластинки.'),
 (45,'Нижняя вырезка между латеральной и медиальной крыловидными пластинками.'),
 (47,'Углубление у верхнего конца медиальной крыловидной пластинки.'),
 (48,'Медиальное расширение у корня медиальной крыловидной пластинки.',[AS['sphenoid'],CANALS]),
 (49,'Борозда нижней поверхности влагалищного отростка, дополняемая клиновидным отростком нёбной кости.',[AS['sphenoid'],CANALS2]),
 (50,'Борозда в области соединения влагалищного отростка с крылом сошника.',[CANALS,CANALS2]),
 (52,'Борозда наружной стороны крыловидного крючка.'),
 (53,'Канал у основания крыловидного отростка, открывающийся впереди в крылонёбную ямку.',[AS['sphenoid'],MCF]),
 (54,'Выступ заднего края латеральной крыловидной пластинки.',[AS['sphenoid'],PTERYGO]),
], [AS['sphenoid'],GRAY['sphenoid']])

add('07',[
 (3,'Мелкие отверстия решётчатой пластинки по сторонам петушиного гребня.',[AS['ethmoid'],KEN['ethmoid']]),
 (5,'Боковое расширение переднего края петушиного гребня, соединяющееся с лобной костью.',[AS['ethmoid'],GALLI]),
 (8,'Передняя группа воздухоносных ячеек решётчатого лабиринта.'),
 (9,'Средняя группа ячеек решётчатого лабиринта.'),
 (10,'Задняя группа воздухоносных ячеек решётчатого лабиринта.'),
 (12,'Вариабельная раковина выше верхней носовой раковины.',[SUPREME,SUPREME2]),
 (13,'Короткая раковина задневерхнего отдела медиальной стороны лабиринта.'),
 (14,'Нижняя свободная изогнутая пластинка медиальной стороны лабиринта.'),
 (15,'Возвышение латеральной стенки среднего носового хода, выше полулунной расщелины.',[AS['ethmoid'],ETHMOID_CT]),
 (16,'Тонкий крючкообразный отросток лабиринта впереди решётчатого пузырька.',[AS['ethmoid'],ETHMOID_CT]),
 (17,'Узкое пространство латеральнее крючковидного отростка.',[AS['ethmoid'],ETHMOID_CT]),
 (18,'Щель между крючковидным отростком и решётчатым пузырьком.',[ETHMOID_CT,KEN['ethmoid']]),
], [AS['ethmoid'],GRAY['ethmoid']])

# Previously positioned terms: replace nomenclature-only descriptions with short
# independently checked topography. Existing coordinate placement is not changed.
add('03',[
 (2,'Вертикальная часть кости, образующая лоб.'),
 (3,'Выпуклая передняя поверхность лобной чешуи.'),
 (4,'Округлое возвышение над надглазничным краем.'),
 (5,'Дугообразное возвышение над надглазничным краем.'),
 (6,'Срединная область между надбровными дугами.'),
 (8,'Верхняя граница входа в глазницу.'),
 (11,'Область чешуи позади и ниже височной линии.'),
 (12,'Край чешуи, соединяющийся с теменными костями.'),
 (13,'Линия, поднимающаяся назад от скулового отростка.'),
 (14,'Латеральное продолжение надглазничного края к скуловой кости.'),
 (15,'Вогнутая поверхность чешуи, обращённая внутрь черепа.'),
 (16,'Срединный гребень нижней части внутренней поверхности.'),
 (17,'Срединная борозда внутренней поверхности над лобным гребнем.'),
 (19,'Участок кости между надглазничными краями, над носовыми костями.'),
 (21,'Нижний зубчатый край носовой части.'),
 (22,'Горизонтальные пластинки по сторонам решётчатой вырезки.'),
 (23,'Нижняя поверхность глазничной части, обращённая в глазницу.'),
], [GRAY['frontal'],AS['frontal']])

add('02',[
 (2,'Вогнутая поверхность, обращённая в полость черепа.'),
 (7,'Выпуклая наружная сторона кости.'),
 (10,'Возвышение центральной области наружной поверхности.'),
 (11,'Задний край, соединяющийся с затылочной костью.'),
 (12,'Нижний край, преимущественно соединяющийся с височной костью.'),
 (13,'Верхний медиальный край у противоположной теменной кости.'),
 (14,'Передний край, соединяющийся с лобной костью.'),
 (15,'Передневерхний угол между лобным и сагиттальным краями.'),
 (17,'Передненижний угол между лобным и чешуйчатым краями.'),
 (18,'Задненижний угол между чешуйчатым и затылочным краями.'),
], [GRAY['parietal'],AS['parietal']])

add('04',[
 (2,'Крупное отверстие между базилярной частью, латеральными частями и чешуёй.'),
 (5,'Участок затылочной кости впереди большого отверстия.'),
 (6,'Наклонная внутричерепная поверхность базилярной части; продолжается к клиновидной кости.'),
 (9,'Часть кости сбоку от большого отверстия.'),
 (10,'Широкая пластинка выше и позади большого отверстия.'),
 (11,'Нижнебоковой край чешуи у сосцевидной части височной кости.'),
 (12,'Верхний зубчатый край чешуи у теменных костей.'),
 (14,'Суставное возвышение нижней поверхности латеральной части.'),
 (22,'Срединное возвышение наружной поверхности чешуи.'),
 (23,'Срединный гребень между наружным выступом и большим отверстием.'),
 (25,'Парная линия, идущая латерально от наружного затылочного выступа.'),
 (27,'Наружная область чешуи выше выйных линий.'),
 (28,'Возвышение внутренней поверхности чешуи, разделяющее четыре ямки.'),
 (29,'Центральная область пересечения частей крестообразного возвышения.'),
 (30,'Срединный гребень от внутреннего выступа к большому отверстию.'),
 (31,'Борозда внутренней поверхности латеральнее внутреннего затылочного выступа.'),
 (36,'Верхняя парная ямка внутренней поверхности чешуи.'),
 (37,'Нижняя парная ямка внутренней поверхности чешуи.'),
], [GRAY['occipital'],AS['occipital']])

add('05',[
 (2,'Срединная часть кости между крыльями.'),
 (3,'Передняя площадка верхней поверхности тела, перед предперекрёстной бороздой.'),
 (6,'Область верхней поверхности тела между бугорком и спинкой седла.'),
 (7,'Поперечное возвышение перед гипофизарной ямкой.'),
 (9,'Углубление в центре турецкого седла.'),
 (10,'Задняя костная стенка турецкого седла.'),
 (14,'Вертикальный срединный гребень передней поверхности тела.'),
 (15,'Срединное выступающее продолжение гребня на нижней поверхности тела.'),
 (20,'Тонкая пластинка сбоку от передневерхней части тела.'),
 (24,'Крупный боковой отросток тела клиновидной кости.'),
 (25,'Вогнутая внутричерепная сторона большого крыла.'),
 (26,'Латеральная поверхность большого крыла выше подвисочного гребня.'),
 (27,'Нижняя поверхность большого крыла ниже подвисочного гребня.'),
 (29,'Участок большого крыла, обращённый в крылонёбную ямку.'),
 (30,'Переднемедиальная поверхность большого крыла в латеральной стенке глазницы.'),
 (31,'Край глазничной поверхности большого крыла у скуловой кости.'),
 (32,'Верхний край глазничной поверхности большого крыла у лобной кости.'),
 (34,'Латеральный край большого крыла у чешуи височной кости.'),
 (36,'Отверстие большого крыла позади и латеральнее круглого отверстия.'),
 (42,'Отросток, направленный вниз от области соединения тела и большого крыла.'),
 (43,'Латеральная пластинка крыловидного отростка.'),
 (44,'Медиальная пластинка крыловидного отростка.'),
 (46,'Углубление сзади между крыловидными пластинками.'),
 (51,'Изогнутый нижний конец медиальной крыловидной пластинки.'),
], [GRAY['sphenoid'],AS['sphenoid']])

add('07',[
 (2,'Горизонтальная пластинка между лабиринтами, в крыше носовой полости.'),
 (4,'Срединный выступ над решётчатой пластинкой.'),
 (6,'Срединная пластинка, спускающаяся в костную перегородку носа.'),
 (7,'Парная масса ячеек по сторонам перпендикулярной пластинки.'),
 (11,'Латеральная пластинка лабиринта, обращённая в глазницу.'),
], [GRAY['ethmoid'],AS['ethmoid']])

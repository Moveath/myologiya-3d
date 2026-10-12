"""Independent anatomical evidence for all 118 facial-bone terms.

Sources were read 2026-10-12. Nomenclature remains in head_terms.py. Text below
is a concise original Russian description, not copied atlas prose. Coordinates
and limits of source-mesh representation are in pins_head/face-extra.json.
Public-domain Buchanan and Gray are separate textbooks; copies of Gray are
never counted as independent from Gray. No proprietary imagery is redistributed.
"""

BUCHANAN = "https://embryology.med.unsw.edu.au/embryology/index.php?title=Book_-_Buchanan%27s_Manual_of_Anatomy_including_Embryology_5"
PALACKY = 'https://www.atlascloveka.upol.cz/cs/cs02/cs0201/cs020115.html'
GRAY = 'https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/pages-{}/'
STANDARD = 'https://www.anatomystandard.com/ossa-et-juncturae/cranium/maxilla.html'

def ref(title, url, locator):
    return {'title': title, 'url': url, 'locator': locator}

def buch(section, locator):
    return ref('Buchanan, Manual of Anatomy', BUCHANAN, section + ': ' + locator)

def gray(page, locator):
    return ref('Gray, Anatomy of the Human Body, 1918', GRAY.format(page), 'с. '+str(page)+', '+locator)

def pal(section, locator):
    return ref('Университет Палацкого, Libor Luňáček', PALACKY+'#'+section, locator)

def std(locator):
    return ref('Anatomy Standard, Maxilla', STANDARD, locator)

DESCRIPTIONS = {}
def add(prefix, num, x, a, b, note=None):
    code = num if isinstance(num,str) else f'A{prefix}.{num:03}'
    DESCRIPTIONS[code]={'x':x,'refs':[a,b]}
    if note: DESCRIPTIONS[code]['note']=note

P='02.1.12'
add(P,4,'Канал под глазничной поверхностью; продолжается вперёд к подглазничному отверстию.',buch('The Maxillae','orbital surface; infra-orbital canal'),pal('o2','MAXILLA: facies orbitalis, sulcus infraorbitalis → canalis infraorbitalis'))
add(P,5,'Борозда задней части глазничной поверхности, переходящая вперёд в подглазничный канал.',buch('The Maxillae','orbital plate; groove running forwards'),std('Anterior and lateral aspects: Sulcus infraorbitalis'))
add(P,12,'Шов на границе скулового отростка верхней челюсти и скуловой кости.',buch('The Maxillae','zygomatic process: articular surface for zygomatic bone'),ref('Kenhub, Maxilla','https://www.kenhub.com/en/library/anatomy/the-maxilla','Anatomy: zygomatic process meets zygomatic bone'))
add(P,14,'Небольшие отверстия на подвисочной поверхности, ведущие в альвеолярные каналы.',gray(158,'infratemporal surface: apertures of alveolar canals'),buch('The Maxillae','posterior surface: posterior dental canals'))
add(P,15,'Внутрикостные каналы задней стенки, направляющиеся к зубным альвеолам.',gray(158,'infratemporal surface: alveolar canals'),buch('The Maxillae','posterior dental canals leading to molar sockets'))
add(P,18,'Борозда перед верхнечелюстной расщелиной на носовой поверхности.',gray(160,'nasal surface: lacrimal groove'),buch('The Maxillae','nasal surface: groove in front of opening of sinus'))
add(P,19,'Гребень на носовой поверхности для соединения с нижней носовой раковиной.',gray(160,'conchal crest'),pal('o2','MAXILLA: crista conchalis'))
add(P,20,'Край соединения со слёзной костью у заднего края лобного отростка.',buch('The Maxillae','frontal process and medial border of orbital surface'),std('Lateral view: Margo lacrimalis'))
add(P,22,'Борозда позади верхнечелюстной расщелины, у соединения с нёбной костью.',gray(160,'nasal surface, oblique groove behind aperture'),buch('The Maxillae','nasal surface: greater palatine canal groove'))
add(P,25,'Гребень лобного отростка перед слёзной бороздой.',pal('o2','MAXILLA: crista lacrimalis anterior'),ref('Kenhub, Maxilla','https://www.kenhub.com/en/library/anatomy/the-maxilla','Anatomy: frontal process and anterior lacrimal crest'))
add(P,26,'Вырезка в переднем отделе медиального края глазничной поверхности.',buch('The Maxillae','medial border of orbital plate: lacrimal notch'),std('Medial view: Incisura lacrimalis'))
add(P,27,'Гребень медиальной поверхности лобного отростка, связанный со средней носовой раковиной.',pal('o2','MAXILLA: crista ethmoidalis'),std('Medial view: Crista ethmoidalis'))
add(P,31,'Передняя резцовая часть верхней челюсти, содержащая альвеолы резцов.',gray(162,'premaxilla / os incisivum'),buch('The Maxillae','intermaxillary portion bearing central and lateral incisors'))
add(P,'A02.1.00.061','Каналы переднего отдела нёба, соединяющие носовую поверхность с областью резцовой ямки.',gray(162,'incisive canals in incisive foramen'),buch('The Maxillae','palatine process: incisive fossa and incisive canals'))
add(P,32,'Шов от резцовой области к промежутку между боковым резцом и клыком.',gray(162,'linear suture on underside of palatine process'),buch('The Maxillae','suture between maxilla proper and premaxilla'))
spine1=ref('Alkhani и соавт., 2025','https://pmc.ncbi.nlm.nih.gov/articles/PMC12421211/','Introduction; Figure 2: palatine spines and grooves')
add(P,33,'Костные выступы вдоль нёбных борозд на нижней поверхности нёбного отростка.',spine1,std('Bottom view: Spinae palatinae'))
add(P,34,'Продольные борозды на нёбной поверхности, медиальнее альвеол моляров.',spine1,gray(162,'inferior surface: groove at posterior lateral border'))
add(P,38,'Костные перегородки между соседними зубными альвеолами.',buch('The Maxillae','alveolar process: sockets partitioned by septa'),std('Bottom view: Septa interalveolaria'))
septum1=ref('Digital Histology','https://digitalhistology.org/organs-systems/digestive/oral-cavity/tooth/advanced/periodontium-6/','Molar and dental alveolus: Interradicular septum')
septum2=ref('Al Rasheed College of Dentistry, Omar Faridh Fawzi','https://www.alrasheedcol.edu.iq/lect-download-258','Oral Histology, Lecture 11, p. 4, Interradicular fibers group')
add(P,39,'Перегородки между корнями внутри альвеолы многокорневого зуба.',septum1,septum2)
add(P,'A02.1.00.062','Устья резцовых каналов в переднем отделе нёба позади резцов.',gray(162,'incisive foramen and orifices of lateral canals'),buch('The Maxillae','palatine process: incisive fossa'))

P='02.1.14'
add(P,7,'Бугорок на глазничной стороне лобного отростка, ниже лобно-скулового шва.',ref('Gayretli и соавт., 2023','https://pubmed.ncbi.nlm.nih.gov/37133786/','Abstract: Whitnall tubercle, orbital rim and frontozygomatic suture'),ref('Американская академия офтальмологии, EyeWiki','https://eyewiki.aao.org/Bony_Anatomy_of_the_Orbit','Lateral Wall: Whitnall tubercle'))
add(P,8,'Выступ заднего края лобного отростка над началом височного отростка.',buch('The Zygomatic Bones','temporal border: marginal tubercle'),ref('Anatomical study of marginal tubercle, 2017','https://pmc.ncbi.nlm.nih.gov/articles/PMC5234273/','Introduction: posterior border of frontal process'))
add(P,9,'Отверстие на глазничной поверхности скуловой кости.',gray(165,'orbital process: zygomatico-orbital foramina'),buch('The Zygomatic Bones','orbital process: superior/orbital surface openings'))
add(P,10,'Отверстие латеральной поверхности скуловой кости.',buch('The Zygomatic Bones','lateral surface: zygomatic foramen'),pal('o3','OS ZYGOMATICUM: facies lateralis / foramen zygomaticofaciale'))
add(P,11,'Отверстие височной поверхности скуловой кости.',buch('The Zygomatic Bones','zygomatico-temporal canal opening on temporal surface'),pal('o3','OS ZYGOMATICUM: facies temporalis / foramen zygomaticotemporale'))

P='02.1.13'
add(P,6,'Борозда наружной стороны перпендикулярной пластинки у соединения с верхней челюстью.',gray(168,'maxillary surface: deep vertical groove'),buch('The Palatine Bone','lateral surface of perpendicular plate: greater palatine canal'))
add(P,8,'Каналы пирамидального отростка, заканчивающиеся малыми нёбными отверстиями.',gray(168,'pyramidal process: lesser palatine foramina'),buch('The Palatine Bone','tubercle: palatine canals and inferior openings'))
add(P,9,'Нижний гребень носовой поверхности перпендикулярной пластинки.',gray(167,'nasal surface: conchal crest'),buch('The Palatine Bone','medial surface: lower conchal crest'))
add(P,10,'Верхний гребень носовой поверхности перпендикулярной пластинки.',gray(167,'nasal surface: ethmoidal crest'),buch('The Palatine Bone','medial surface: upper ethmoidal crest'))
add(P,12,'Верхний задний отросток, позади клиновидно-нёбной вырезки.',gray(169,'sphenoidal process and sphenopalatine notch'),buch('The Palatine Bone','sphenoidal process surmounting posterior border'))
add(P,16,'Отверстия на нижней стороне пирамидального отростка.',gray(168,'base of pyramidal process: lesser palatine foramina'),ref('Kenhub, Palatine bone','https://www.kenhub.com/en/library/anatomy/the-palatine-bone','Processes: pyramidal process, inferior surface'))
add(P,17,'Задний срединный выступ горизонтальной пластинки.',gray(167,'horizontal plate: posterior nasal spine'),buch('The Palatine Bone','posterior border: spine formed with opposite side'))
add(P,18,'Гребень медиального края горизонтальной пластинки, обращённый к сошнику.',gray(167,'horizontal plate: medial border and nasal crest'),buch('The Palatine Bone','medial border: nasal crest'))
add(P,19,'Поперечный гребень у заднего края нёбной поверхности.',gray(167,'inferior surface: transverse ridge near posterior margin'),buch('The Palatine Bone','horizontal plate: inferior surface, posterior short crest'))

P='02.1.09'
add(P,3,'Продольная борозда впереди заднего слёзного гребня.',buch('The Lacrimal Bones','lateral surface: anterior division and lacrimal groove'),ref('Kenhub, Lacrimal bone','https://www.kenhub.com/en/library/anatomy/the-lacrimal-bone','Lateral surface: groove anterior to posterior lacrimal crest'))
add(P,4,'Крючок нижнего конца заднего слёзного гребня.',buch('The Lacrimal Bones','lacrimal crest terminates in lacrimal hamulus'),pal('o8','OS LACRIMALE: hamulus lacrimalis'))
P='02.1.10'
add(P,2,'Продольная борозда внутренней поверхности носовой кости.',buch('The Nasal Bones','posterior surface: ethmoidal sulcus'),pal('o9','OS NASALE: sulcus ethmoidalis'))
add(P,3,'Мелкие отверстия наружной поверхности носовой кости.',buch('The Nasal Bones','anterior surface: minute foramen near centre'),pal('o9','OS NASALE: foramina nasalia'))
P='02.1.08'
add(P,2,'Передний восходящий отросток верхнего края нижней носовой раковины.',gray(169,'inferior concha: anterior/lacrimal process'),buch('The Inferior Nasal Conchse','superior border: lacrimal process'))
add(P,3,'Пластинка, отходящая латерально и вниз от верхнего края раковины.',gray(169,'maxillary process curves downward and lateralward'),buch('The Inferior Nasal Conchse','maxillary process folded downwards and outwards'))
add(P,4,'Восходящий отросток позади слёзного отростка.',gray(169,'ethmoidal process behind lacrimal process'),buch('The Inferior Nasal Conchse','superior border: ethmoidal process'))
P='02.1.11'
add(P,3,'Косая борозда боковой поверхности сошника, направленная вперёд и вниз.',buch('The Vomer','lateral surface: groove forwards and downwards'),pal('o7','VOMER: sulcus vomeris'))
vomerpaper=ref('Marušić, Vinter, Krmpotić-Nemanić, 2006','https://www.croris.hr/crosbi/publikacija/prilog-casopis/140366','Lost and found anatomical terms: Crista choanalis vomeris, abstract')
add(P,4,'Хоанный гребень задней области сошника; его определение расходится в источниках.',vomerpaper,pal('o7','VOMER: crista choanalis'), 'Marušić и соавт. описывают гребень от угла крыльев к заднему свободному краю; атлас Палацкого отождествляет его с задним краем. Маркер показывает ориентировочную область по первому описанию, а не точную линию.')
add(P,5,'Клиновидная область заднего отдела сошника.',vomerpaper,pal('o7','VOMER: pars cuneiformis'), 'Marušić и соавт. определяют её как участок позади хоанного гребня; атлас Палацкого не задаёт точную границу. На данной модели граница не подтверждена.')

P='02.1.15'
add(P,4,'Срединная область соединения правой и левой половин тела.',gray(172,'external surface: symphysis'),buch('The Mandible','lateral surface: median ridge marking symphysis'))
add(P,9,'Ямка внутренней поверхности у нижнего края, латеральнее подбородочных остей.',gray(173,'digastric depression below mental spines'),buch('The Mandible','medial surface: digastric fossa'))
add(P,10,'Верхняя подбородочная ость внутренней стороны симфиза.',gray(172,'internal surface: upper mental spines'),buch('The Mandible','medial surface: upper genial tubercles'))
add(P,11,'Нижняя подбородочная ость под верхней остью.',gray(172,'internal surface: lower spines or median ridge'),buch('The Mandible','medial surface: lower genial tubercles'))
add(P,12,'Косая линия внутренней поверхности тела, поднимающаяся назад к молярам.',gray(173,'mylohyoid line'),buch('The Mandible','medial surface: mylo-hyoid line'))
add(P,13,'Вариант костного выступа язычной поверхности тела, обычно в области премоляров.',ref('University of Anbar','https://www.uoanbar.edu.iq/eStoreImages/Bank/15411.pdf','Anatomical Landmarks: Torus mandibularis'),ref('October 6 University','https://o6u.edu.eg/uploads/Dent/Anatomical%20Landmarks.pdf','Mandibular landmarks: torus in lingual premolar area'))
add(P,14,'Углубление над передним отделом челюстно-подъязычной линии.',gray(173,'sublingual gland area above anterior line'),buch('The Mandible','sublingual fossa'))
add(P,15,'Углубление ниже заднего отдела челюстно-подъязычной линии.',gray(173,'submaxillary gland fossa below hinder line'),buch('The Mandible','submandibular fossa'))
add(P,19,'Перегородки между соседними зубными альвеолами.',buch('The Mandible','alveolar border and sockets corresponding to maxilla'),ref('Kenhub, Mandible','https://www.kenhub.com/en/library/anatomy/the-mandible','Body: interalveolar septa partition the sockets'))
add(P,20,'Перегородки между корнями внутри альвеолы многокорневого зуба.',septum1,septum2)
retro1=ref('Occurrence of the Retromolar Foramen, 2014','https://pmc.ncbi.nlm.nih.gov/articles/PMC4197892/','Introduction: retromolar fossa behind third molar and its boundaries')
retro2=ref('Mandibular Retromolar Foramen and Canal, 2021','https://pmc.ncbi.nlm.nih.gov/articles/PMC7944007/','Introduction and Figure 1: retromolar triangle, fossa and boundaries')
add(P,22,'Треугольная площадка непосредственно позади последнего нижнего моляра.',retro1,retro2)
add(P,23,'Углубление позади моляров между передним краем ветви и височным гребнем.',retro1,retro2)
add(P,27,'Шероховатая область медиальной стороны угла нижней челюсти.',gray(173,'ramus medial surface: rough area behind mylohyoid groove'),buch('The Mandible','rough impression between mandibular foramen and angle'))
add(P,28,'Вход в канал на медиальной стороне ветви.',gray(173,'medial surface of ramus: mandibular foramen'),buch('The Mandible','medial ramus: mandibular foramen'))
add(P,29,'Выступ переднего края отверстия нижней челюсти.',gray(173,'lingula at anterior margin of foramen'),buch('The Mandible','thin sharp plate anterior and medial to foramen'))
add(P,30,'Внутрикостный канал ветви и тела под зубными альвеолами.',gray(173,'mandibular canal'),buch('The Mandible','mandibular canal traverses bone towards symphysis'))
add(P,31,'Борозда, идущая от области отверстия вперёд и вниз.',gray(173,'mylohyoid groove from lower back part of foramen'),buch('The Mandible','mylo-hyoid groove'))
add(P,33,'Гребень медиальной стороны венечного отростка, спускающийся к позадимолярной области.',buch('The Mandible','ridge on medial coronoid surface continuing towards last molar'),retro2)
add(P,38,'Ямка передней поверхности шейки нижней челюсти.',buch('The Mandible','neck: anterior depression for lateral pterygoid'),pal('o1','MANDIBULA: fossa pterygoidea below head, anteriorly'))

# Short topography for the previously retained surface markers, reviewed together
# with the added points. This removes nomenclature-only evidence from these cards.
for num,x,page,locator in [
 (2,'Основная часть верхней челюсти, содержащая верхнечелюстную пазуху.',158,'body'),
 (3,'Верхняя поверхность тела, обращённая в глазницу.',158,'orbital surface'),
 (6,'Край между передней и глазничной поверхностями.',158,'margin of orbit'),
 (7,'Передняя сторона тела верхней челюсти.',158,'anterior surface'),
 (8,'Отверстие передней поверхности ниже подглазничного края.',158,'infraorbital foramen'),
 (9,'Углубление передней поверхности ниже подглазничного отверстия.',158,'canine fossa'),
 (10,'Вогнутый медиальный край передней поверхности у входа в носовую полость.',158,'nasal notch'),
 (11,'Передний выступ у нижнего конца носовой вырезки.',158,'anterior nasal spine'),
 (13,'Задняя сторона тела, обращённая в подвисочную область.',158,'infratemporal surface'),
 (16,'Задненижний выступ тела позади последнего моляра.',158,'maxillary tuberosity'),
 (17,'Медиальная поверхность тела, обращённая к носовой полости.',160,'nasal surface'),
 (21,'Большое отверстие носовой поверхности в верхнечелюстную пазуху.',160,'opening into maxillary sinus'),
 (23,'Полость внутри тела верхней челюсти.',160,'maxillary sinus'),
 (24,'Восходящий отросток у медиального края кости.',158,'frontal process; Fig. 157'),
 (28,'Латеральный отросток для соединения со скуловой костью.',158,'zygomatic process'),
 (29,'Горизонтальный отросток, выступающий медиально и участвующий в костном нёбе.',162,'palatine process'),
 (30,'Верхний гребень медиального края нёбного отростка.',163,'nasal crest'),
 (35,'Нижний зубоносный отросток верхней челюсти.',162,'alveolar arch; Fig. 160'),
 (36,'Изогнутый свободный край альвеолярного отростка.',162,'alveolar arch; Fig. 160'),
 (37,'Костные лунки для корней верхних зубов.',162,'alveolar arch; Fig. 160'),
 (40,'Выступы наружной стороны альвеолярного отростка, соответствующие корням зубов.',158,'anterior surface: eminences for tooth roots'),
]:
    b_locator={24:'frontal process',35:'alveolar process',36:'alveolar process: inferior border',37:'alveolar process: sockets'}.get(num,locator)
    add('02.1.12',num,x,gray(page,locator),buch('The Maxillae',b_locator))
for num,x,locator in [
 (2,'Наружная поверхность скуловой кости.','lateral surface'),
 (3,'Поверхность, обращённая в височную область.','temporal surface'),
 (4,'Поверхность скуловой кости, обращённая в глазницу.','orbital surface'),
 (5,'Задний отросток, направленный к височной кости.','temporal process'),
 (6,'Верхний отросток, направленный к лобной кости.','frontal process'),
]:
    add('02.1.14',num,x,buch('The Zygomatic Bones',locator),pal('o3','OS ZYGOMATICUM: '+locator))
for num,x,page,locator in [
 (2,'Вертикальная пластинка нёбной кости.',167,'perpendicular plate'),
 (3,'Медиальная сторона перпендикулярной пластинки.',167,'nasal surface'),
 (4,'Латеральная сторона перпендикулярной пластинки.',168,'maxillary surface'),
 (5,'Вырезка между глазничным и клиновидным отростками.',168,'sphenopalatine notch'),
 (7,'Отросток, выступающий назад и латерально от соединения пластинок.',168,'pyramidal process'),
 (11,'Передний верхний отросток над перпендикулярной пластинкой.',168,'orbital process'),
 (13,'Горизонтальная пластинка заднего отдела костного нёба.',167,'horizontal plate'),
 (14,'Верхняя сторона горизонтальной пластинки.',167,'superior surface of horizontal plate'),
 (15,'Нижняя сторона горизонтальной пластинки.',167,'inferior surface of horizontal plate'),
]:
    add('02.1.13',num,x,gray(page,locator),buch('The Palatine Bone',locator))
add('02.1.09',2,'Вертикальный гребень глазничной стороны слёзной кости.',buch('The Lacrimal Bones','lateral surface: lacrimal crest'),pal('o8','OS LACRIMALE: crista lacrimalis posterior'))
add('02.1.11',2,'Крыловидное расширение верхнего края сошника.',buch('The Vomer','superior border: everted alae'),pal('o7','VOMER: ala vomeris'))
for num,x,page,locator in [
 (2,'Изогнутая горизонтальная часть нижней челюсти.',172,'body'),
 (3,'Нижний край тела нижней челюсти.',173,'inferior border'),
 (5,'Срединный выступ передней поверхности подбородка.',172,'mental protuberance'),
 (6,'Выступ у нижнебокового края подбородочного выступа.',172,'mental tubercle'),
 (7,'Отверстие наружной поверхности тела в области премоляров.',172,'mental foramen'),
 (8,'Линия наружной поверхности тела, восходящая назад к ветви.',172,'oblique line'),
 (16,'Верхняя зубоносная часть тела нижней челюсти.',173,'alveolar border'),
 (17,'Изогнутый верхний край альвеолярной части.',173,'alveolar border'),
 (18,'Костные лунки для корней нижних зубов.',173,'sockets for teeth'),
 (21,'Наружные возвышения альвеолярной части, соответствующие зубным лункам.',172,'external surface; Fig. 176'),
 (24,'Восходящая часть нижней челюсти.',173,'ramus'),
 (25,'Область соединения нижнего и заднего краёв ветви.',173,'ramus; Fig. 177'),
 (26,'Шероховатая область наружной стороны угла и нижней части ветви.',173,'lateral surface of ramus: ridges'),
 (32,'Передний верхний отросток ветви.',173,'ramus; Fig. 177'),
 (34,'Вырезка верхнего края между венечным и мыщелковым отростками.',173,'ramus; Fig. 177'),
 (35,'Задний верхний отросток ветви.',173,'ramus; Fig. 177'),
 (36,'Суставная верхняя часть мыщелкового отростка.',173,'ramus; Fig. 177'),
 (37,'Суженная часть ниже головки нижней челюсти.',173,'ramus; Fig. 177'),
]:
    b_locator={25:'posterior border of ramus meeting inferior border',32:'coronoid process surmounts anterior border',34:'superior border: mandibular notch',35:'condyloid process surmounts posterior border',36:'oval convex condyloid process',37:'neck below condyloid process'}.get(num,locator)
    add('02.1.15',num,x,gray(page,locator),buch('The Mandible',b_locator))

# The old textbook's general body paragraph does not explicitly define juga;
# use two sources that actually identify this particular relief.
add('02.1.15',21,'Наружные возвышения альвеолярной части, соответствующие зубным лункам.',
    ref('Anatomy Standard, Mandibula','https://www.anatomystandard.com/ossa-et-juncturae/cranium/mandibula.html','Iso-view of mandible with teeth in situ/ex situ: Juga alveolaria'),
    ref('Стоян Казаков, OMFS.BG','https://omfs.bg/index.php?Itemid=391&catid=156%3Aosteologia&id=785%3Akostna-anatomia-na-dolnata-celust-mandibula&option=com_content&view=article','Особености на алвеоларния израстък, пункт 4: Юга (juga alveolaria)'))

assert all(len(v['refs'])>=2 for v in DESCRIPTIONS.values())

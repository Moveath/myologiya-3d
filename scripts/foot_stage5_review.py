"""Foot catalogue decisions. No inferred, reflected or transferred coordinates."""
from copy import deepcopy
from ta98 import T, BONE

REPORT='research/stage5-foot-report-2026-10-19.md'
GRAY='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
SOB='https://archive.org/download/atlastextbookofh01sobouoft/atlastextbookofh01sobouoft_djvu.txt'
TA='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1027%20A2F%20EN.htm'
NOTE='Тип описывает анатомическую сущность, а не точность старой точки. Границы, поверхности и объёмы на данном образце не размечены; близость к сетке не является анатомической приёмкой.'
LEFT_NOTE='Подтверждённой левой модели стопы в ресурсах проекта не найдено. Нужен лицензированный левый исходник с масштабом, осями и регистрацией. Координаты и геометрия справа не переносились.'

def ref(key,title,url,locator,access='full_text'):
    return dict(id='foot_'+key,title=title,url=url,locator=locator,access=access,checked='2026-10-19')

def refs():
    return [ref('gray','Gray / Lewis (1918), The Foot',GRAY,'6d.1–4: Tarsus, Metatarsus, Phalanges, Sesamoid bones; PDF pp.275–302'),
            ref('sobotta','Sobotta / McMurrich (1914), Vol. I',SOB,'Bones of the foot, printed pp.102–106, Figs.153–166'),
            ref('ta98','FIPAT / IFAA TA98 — bones of lower limb',TA,'A02.5.10–18; номенклатура, не координаты','official_list')]

# Each numbered decision corresponds to a reviewed TA entity. Grooves describe
# paths; their width/depth needs a surface annotation, never an arbitrary point.
TALUS={
 2:('volume','Головка — передний объёмный отдел таранной кости; суставные покрытия представлены отдельно.'),
 3:('area','Выпуклая суставная поверхность головки обращена к ладьевидной кости.'),
 4:('area','Участок нижней поверхности головки опирается на подошвенную пяточно-ладьевидную связку; костный меш не заменяет связку.'),
 5:('area','Участок головки, связанный с пяточно-ладьевидной частью раздвоенной связки по TA98; не отдельная кость.'),
 6:('area','Передняя пяточная суставная поверхность находится на нижней стороне головки.'),
 7:('volume','Шейка — суженный участок между головкой и телом, а не точка или измеренная ось.'),
 8:('area','Средняя пяточная суставная поверхность на нижней стороне шейки обращена к sustentaculum tali.'),
 9:('line','Борозда между средней и задней пяточными поверхностями — протяжённое костное ложе, участвующее в межкостном проходе.'),
 10:('volume','Тело — задний основной объём кости, несущий блок и суставные поверхности.'),
 11:('volume','Блок — суставной костный участок тела; верхняя и лодыжковые поверхности не тождественны всему блоку.'),
 12:('area','Верхняя суставная поверхность блока обращена к дистальной поверхности большеберцовой кости.'),
 13:('area','Латеральная лодыжковая поверхность сочленяется с малоберцовой костью.'),
 14:('volume','Латеральный отросток — костный выступ под латеральной лодыжковой поверхностью.'),
 15:('area','Медиальная лодыжковая поверхность обращена к медиальной лодыжке; известное расхождение электронной TA98 сохранено.'),
 16:('volume','Задний отросток включает два бугорка, разделённые сухожильной бороздой.'),
 17:('line','Борозда длинного сгибателя большого пальца проходит между бугорками заднего отростка; её полный профиль не задан.'),
 18:('volume','Латеральный бугорок — костный выступ заднего отростка, а не отдельный обязательный os trigonum.'),
 19:('volume','Медиальный бугорок — костный выступ с другой стороны борозды длинного сгибателя большого пальца.'),
 20:('area','Задняя пяточная поверхность снизу на теле участвует в подтаранном суставе.'),
 21:('volume','Os trigonum — вариант отдельной добавочной кости позади таранной кости; наличие на данном образце не установлено.')}
CALCANEUS={
 2:('volume','Пяточный бугор — задний объёмный отдел пяточной кости.'),
 3:('volume','Медиальный отросток — выступ подошвенной части пяточного бугра.'),
 4:('volume','Латеральный отросток — отдельный выступ подошвенной части бугра.'),
 5:('volume','Пяточный бугорок расположен впереди бугра на подошвенной стороне; не его синоним.'),
 6:('volume','Sustentaculum tali — медиальная костная опора со средней таранной поверхностью сверху и сухожильной бороздой снизу.'),
 7:('line','Борозда сухожилия длинного сгибателя большого пальца проходит под sustentaculum tali.'),
 8:('line','Борозда пяточной кости разделяет среднюю и заднюю таранные поверхности; не равна всему sinus tarsi.'),
 9:('space','Sinus tarsi — межкостное пространство между таранной и пяточной костями, латеральное расширение прохода. Не поверхность одной кости.'),
 10:('area','Передняя таранная поверхность сочленяется с головкой таранной кости; раздельность со средней вариабельна.'),
 11:('area','Средняя таранная поверхность покрывает верх sustentaculum tali.'),
 12:('area','Задняя таранная поверхность — выпуклая площадка подтаранного сустава.'),
 13:('line','Борозда длинной малоберцовой мышцы проходит на латеральной стороне ниже малоберцового блока.'),
 14:('volume','Малоберцовый блок — костный выступ между ходом короткой и длинной малоберцовых мышц; выраженность вариабельна.'),
 15:('area','Передняя кубовидная суставная поверхность пяточной кости обращена к кубовидной кости.')}
NAVICULAR={2:('volume','Бугристость — выступ медиально-подошвенной части ладьевидной кости, не вся её поверхность.')}
CUBOID={2:('line','Подошвенная борозда служит ложем сухожилия длинной малоберцовой мышцы; её профиль требует разметки.'),
        3:('volume','Бугристость и связанный с ней гребень расположены позади подошвенной сухожильной борозды.'),
        4:('volume','Пяточный отросток выступает назад от подошвенно-медиальной части кубовидной кости.')}
METATARSAL={2:('volume','Основание — проксимальный объёмный конец плюсневой кости; состав суставных фасеток зависит от номера.'),
 3:('volume','Тело — диафиз между основанием и головкой плюсневой кости.'),
 4:('volume','Головка — дистальный костный конец; суставное покрытие не равно всему объёму головки.'),
 5:('volume','Бугристость I плюсневой кости — подошвенно-латеральный выступ её основания.'),
 6:('volume','Бугристость V плюсневой кости — латеральный выступ основания, не гребень тела.')}
PHALANX={5:('volume','Бугристость дистальной фаланги — расширение её свободного конца; не суставная головка.'),
 6:('volume','Основание фаланги — проксимальный конец кости, включающий суставную поверхность.'),
 7:('volume','Тело фаланги — объёмный участок между концами кости.'),
 8:('volume','Головка — дистальный конец фаланги. У дистальной фаланги свободный конец не образует следующий сустав.'),
 9:('volume','Блок проксимальной или средней фаланги — костный суставной конец с блоковидным покрытием, не математическая точка.')}
TABLES={'talus':TALUS,'calcaneus':CALCANEUS,'navicular':NAVICULAR,'cuboid':CUBOID}
LABELS={
 'talus':('Таранная кость','talus','b_tarsus','Кость заднего отдела стопы, сочленяющаяся с большеберцовой, малоберцовой, пяточной и ладьевидной костями.'),
 'calcaneus':('Пяточная кость','calcaneus','b_tarsus','Кость заднего отдела стопы, сочленяющаяся с таранной и кубовидной костями.'),
 'navicular':('Ладьевидная кость','os naviculare','b_tarsus','Кость между головкой таранной и тремя клиновидными костями; суставная фасетка для кубовидной кости вариабельна.'),
 'cuboid':('Кубовидная кость','os cuboideum','b_tarsus','Латеральная кость предплюсны между пяточной и IV–V плюсневыми костями; также сочленяется с латеральной клиновидной.'),
 'cuneiform_med':('Медиальная клиновидная кость','os cuneiforme mediale','b_tarsus','Медиальная кость клиновидной группы; сочленяется с ладьевидной, промежуточной клиновидной, I и II плюсневыми костями.'),
 'cuneiform_int':('Промежуточная клиновидная кость','os cuneiforme intermedium','b_tarsus','Кость между медиальной и латеральной клиновидными; сочленяется с ладьевидной и II плюсневой костями.'),
 'cuneiform_lat':('Латеральная клиновидная кость','os cuneiforme laterale','b_tarsus','Кость между промежуточной клиновидной и кубовидной; сочленяется также с ладьевидной и II–IV плюсневыми костями.'),
 'sesamoid_pedis':('Сесамовидные кости большого пальца стопы','ossa sesamoidea','b_toes','Групповая карточка типичной медиальной и латеральной сесамовидных костей I плюснефалангового сустава. Варианты других суставов не включены в обязательную пару.')}
for i,roman in enumerate(('I','II','III','IV','V'),1):
    LABELS[f'metatarsal_{i}']=(roman+' плюсневая кость',f'os metatarsi {roman}','b_metatarsus',f'{roman} плюсневая кость: основание, тело и головка; дистально сочленяется с проксимальной фалангой соответствующего пальца.')
    for kind,ru,lat in [('prox','Проксимальная','proximalis'),('mid','Средняя','media'),('dist','Дистальная','distalis')]:
        if kind=='mid' and i==1:continue
        LABELS[f'toe_{kind}_{i}']=(f'{ru} фаланга {roman} пальца стопы',f'phalanx {lat} digiti {roman} pedis','b_toes',
            f'{ru} фаланга {roman} пальца стопы. У большого пальца две фаланги, у II–V пальцев типично три; сращения являются вариантами.')
OWNERS=set(LABELS)

def limits(p):
    p.update(educationAvailable=False,geometryRequirements=dict(status='unverified_extent',neededEvidence=LEFT_NOTE if p.get('side')=='left' else NOTE),
             footReview=dict(source=REPORT,scope='catalogue_and_representation',coordinateAcceptance=False,extentAcceptance=False))
    p['modelNote']=(p.get('modelNote','')+' '+(LEFT_NOTE if p.get('side')=='left' else NOTE)).strip()
    return p

def review(record):
    b=record['b']; root=b.removesuffix('_left')
    if root not in OWNERS:return record
    p=deepcopy(record); p['side']='left' if b.endswith('_left') else 'right'
    if p['t']=='ta':
        table=METATARSAL if root.startswith('metatarsal_') else PHALANX if root.startswith('toe_') else TABLES[root]
        kind,definition=table[int(p['c'].split('.')[-1])]
    else:kind,definition='area','Место прикрепления или начала — область. Одна точка не подтверждает несколько мышц, их части или всю площадь прикрепления.'
    p.update(geometryKind=kind,geometryKindReason=definition,anatomicalDefinition=definition)
    if p['side']=='left':p['x']=definition
    p.setdefault('refs',[]); p['refs']+=refs()
    if root=='calcaneus' and p.get('c')=='A02.5.11.009':
        from shared_landmarks import SINUS_SOURCES
        p.update(concept='tarsal-sinus',relations=[dict(bone=q+('_left' if p['side']=='left' else ''),role='boundaryContribution') for q in ('calcaneus','talus')],anchors=[],anchorStatus='unverified')
        p['refs']+=deepcopy(SINUS_SOURCES)
    if p.get('c')=='A02.5.10.021':
        p.update(anchorStatus='unverified',anchors=[],inc=1,anatomicalVariant=True)
        p['x']=definition+' Прежняя координата сохранена только для исследования и не показывается как подтверждённый пин.'
    if root=='metatarsal_2' and p.get('c')=='A02.5.17.002':
        p['x']='Основание II плюсневой кости сочленяется с тремя клиновидными и III плюсневой костями. Фасетка для I плюсневой непостоянна; соседство I–II не доказывает обязательный сустав.'
    if root=='metatarsal_5' and p.get('c')=='A02.5.17.002':
        p['x']='Основание V плюсневой кости сочленяется с кубовидной и IV плюсневой костями. На латеральной стороне расположена бугристость.'
    if p['t']=='att':
        p['attachmentReview']=dict(status='requires_verification',issue='DATA-MUSCLE-BONE-LINKS',scope='legacy muscle/part links; no area accepted')
        p['note']='Связи мышц и их частей сохранены как исходные: требуется отдельная сверка состава и прямого/сухожильного прикрепления. Тип «область» не подтверждает эти связи.'
    return limits(p)

LEFT_BONES={b+'_left':dict(ru=ru+' · слева',lat=lat,g=g,sub='foot',sec='leg',side='left',noModel=True,x=x,note=LEFT_NOTE,refs=refs()) for b,(ru,lat,g,x) in LABELS.items()}
RIGHT_PATCHES={b:dict(ru=ru+' · справа',side='right',x=x,refs=refs()) for b,(ru,lat,g,x) in LABELS.items()}
RIGHT_PATCHES['sesamoid_pedis']['note']='В существующем общем меше есть две раздельные компоненты. Индивидуальная анатомическая привязка и выделение медиальной/латеральной кости ещё не приняты; обе описаны отдельными дочерними карточками без координат.'

def left_records():
    for b in sorted(OWNERS):
        for c in BONE[b]:
            yield review(dict(id='context_'+b+'_left_'+c.replace('.','_'),b=b+'_left',t='ta',c=c,ru=T[c][1],lat=T[c][0],x=T[c][1]+'. '+LEFT_NOTE,p=None,n=None,m=[],**({'inc':1} if T[c][2]=='inc' else {})))

def extra(b,key,ru,kind,text,**fields):
    return limits(dict(id='extra_'+b+'_'+key,b=b,t='additional',ru=ru,lat=fields.pop('lat',''),x=text,p=None,n=None,m=[],
        side='left' if b.endswith('_left') else 'right',geometryKind=kind,geometryKindReason=text,anatomicalDefinition=text,
        g='Дополнительные образования',refs=refs(),nomenclatureStatus='descriptive_term_without_assigned_TA98_code',**fields))

def additional_records(left=False):
    s='_left' if left else ''; label=' · слева' if left else ' · справа'
    # Missing surface cards are subsets of bones, not new bones or guessed masks.
    surfaces=[('navicular','talar_surface','Задняя суставная поверхность для таранной кости','Вогнутая задняя поверхность ладьевидной кости принимает головку таранной.'),
      ('navicular','cuneiform_surfaces','Передние суставные фасетки для клиновидных костей','Передняя поверхность ладьевидной кости разделена на фасетки для трёх клиновидных костей.'),
      ('cuboid','calcaneal_surface','Суставная поверхность для пяточной кости','Задняя поверхность кубовидной кости сочленяется с передней поверхностью пяточной.'),
      ('cuboid','metatarsal_surfaces','Суставные фасетки для IV и V плюсневых костей','Передние суставные участки кубовидной кости обращены к основаниям IV и V плюсневых костей.')]
    for b,number in [('cuneiform_med','I'),('cuneiform_int','II'),('cuneiform_lat','III')]:
        surfaces += [(b,'navicular_surface','Задняя суставная поверхность для ладьевидной кости','Проксимальная суставная поверхность клиновидной кости обращена к соответствующей передней фасетке ладьевидной.'),
                     (b,'distal_surface',f'Дистальная суставная поверхность для {number} плюсневой кости',f'Передняя суставная поверхность обращена к основанию {number} плюсневой кости. Боковые фасетки для других костей учитываются отдельно от этой поверхности.')]
    for b,key,ru,text in surfaces:yield extra(b+s,key,ru+label,'area',text)
    for key,ru,lat in [('medial','Медиальная (большеберцовая)','mediale'),('lateral','Латеральная (малоберцовая)','laterale')]:
        p=extra('sesamoid_pedis'+s,key+'_hallux_sesamoid',ru+' сесамовидная кость большого пальца стопы'+label,'volume',
            'Одна из двух типичных сесамовидных костей на подошвенной стороне I плюснефалангового сустава. Медиальная и латеральная кости различаются относительно стопы, а не стороны экрана. Возможны варианты, включая врождённое отсутствие; типичная пара не означает универсальное наличие у каждого человека.',
            parentBone='sesamoid_pedis'+s,anatomicalEntity='bone',catalogueRole='typical',lat='os sesamoideum '+lat)
        p['refs'] += [ref('sesamoids','Srinivasan (2016), The Hallucal-Sesamoid Complex','https://pubmed.ncbi.nlm.nih.gov/27336456/','Abstract; PMID/DOI verified by NCBI EFetch; not full-text geometry','abstract'),
          ref('absence','Young et al. (2020), Congenital Absence of Tibial Sesamoids','https://pubmed.ncbi.nlm.nih.gov/32505726/','Abstract: bilateral congenital absence is a variant, not a typical omission','abstract')]
        yield p
    # A joint is a volume including soft tissues. Relations name bone participants,
    # not surfaces, independent duplicate landmarks or complete joint geometry.
    joints=[('ankle','talus','Голеностопный сустав','articulatio talocruralis',['talus','tibia','fibula']),
      ('subtalar','talus','Подтаранный сустав','articulatio subtalaris',['talus','calcaneus']),
      ('talocalcaneonavicular','talus','Таранно-пяточно-ладьевидный сустав','articulatio talocalcaneonavicularis',['talus','calcaneus','navicular']),
      ('calcaneocuboid','calcaneus','Пяточно-кубовидный сустав','articulatio calcaneocuboidea',['calcaneus','cuboid']),
      ('cuneonavicular','navicular','Клино-ладьевидный сустав','articulatio cuneonavicularis',['navicular','cuneiform_med','cuneiform_int','cuneiform_lat']),
      ('intercuneiform','cuneiform_int','Межклиновидные суставы','articulationes intercuneiformes',['cuneiform_med','cuneiform_int','cuneiform_lat']),
      ('cuneocuboid','cuboid','Клино-кубовидный сустав','articulatio cuneocuboidea',['cuboid','cuneiform_lat']),
      ('intermetatarsal','metatarsal_2','Межплюсневые суставы II–V','articulationes intermetatarsales',[f'metatarsal_{i}' for i in range(2,6)]),
      ('tarsometatarsal','cuneiform_med','Предплюсне-плюсневые суставы','articulationes tarsometatarsales',['cuneiform_med','cuneiform_int','cuneiform_lat','cuboid']+[f'metatarsal_{i}' for i in range(1,6)])]
    for i in range(1,6):
        joints.append((f'mtp_{i}',f'metatarsal_{i}',f'Плюснефаланговый сустав {i} пальца','articulatio metatarsophalangea',[f'metatarsal_{i}',f'toe_prox_{i}']+(['sesamoid_pedis'] if i==1 else [])))
        pairs=[('ip','prox','dist')] if i==1 else [('pip','prox','mid'),('dip','mid','dist')]
        for key,a,b in pairs:joints.append((f'{key}_{i}',f'toe_{a}_{i}',('Межфаланговый' if i==1 else 'Проксимальный межфаланговый' if key=='pip' else 'Дистальный межфаланговый')+f' сустав {i} пальца','articulatio interphalangea',[f'toe_{a}_{i}',f'toe_{b}_{i}']))
    for key,b,ru,lat,owners in joints:
        text='Суставное образование; в связях перечислены участвующие кости. Костные поверхности не заменяют хрящи, капсулу и связки; сустав не является точкой.'
        if key=='subtalar':text+=' Здесь термин относится к заднему таранно-пяточному сочленению; передние/средние фасетки входят в таранно-пяточно-ладьевидный сустав.'
        if key=='talocalcaneonavicular':text+=' В опоре головки участвует также подошвенная пяточно-ладьевидная связка; её достоверная геометрия здесь не заявляется.'
        if key=='tarsometatarsal':text+=' Это группа сочленений, а не все попарные контакты перечисленных костей. Она не утверждает существование сустава между I и II плюсневыми.'
        if key in {'intercuneiform','intermetatarsal'}:text+=' Группа сочленений соседних костей; общий список участников не означает все попарные контакты или изолированную полость для каждой фасетки.'
        p=extra(b+s,key+'_joint',ru+label,'volume',text,lat=lat,anatomicalEntity='joint_group' if key in {'tarsometatarsal','intercuneiform','intermetatarsal'} else 'joint',
            relations=[dict(bone=o+s,role='component') for o in owners],anchors=[],catalogueBones=[])
        p['refs'] += [ref('sobotta_joints','Sobotta / McMurrich (1914) — joints of foot',SOB,'Printed pp.137–139, Figs.224–226: ankle, tarsal and digital joints'),
          ref('ncbi_joints','Manganaro et al. (2023) — Foot Joints','https://www.ncbi.nlm.nih.gov/sites/books/NBK536941/','Introduction; Structure and Function. Only participants adopted; broad subtalar wording is not used to merge distinct joints.')]
        yield p

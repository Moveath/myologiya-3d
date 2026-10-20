"""Explicit pelvic entity review. Types are display requirements, never mesh masks."""
from copy import deepcopy
from lumbopelvic_targeted_review import review as targeted_review, extra_records as targeted_records

REPORT='research/stage5-pelvis-report-2026-10-18.md'
GRAY='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
FIPAT='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1027%20A2F%20EN.htm'
OPEN='https://openstax.org/books/anatomy-and-physiology-2e/pages/8-3-the-pelvic-girdle-and-pelvis'
DAR='https://humananatomy.host.dartmouth.edu/BHA/public_html/part_7/chapter_39.html'
STANDARD='https://www.anatomystandard.com/ossa-et-juncturae/extremitas-inferior/os-coxae.html'
def ref(key,title,url,locator,group,**kw):
    return dict(id='pelvis_'+key,title=title,url=url,locator=locator,authorGroup=group,checked='2026-10-18',**kw)
HIP_REFS=[ref('gray_hip','Gray / Lewis (1918)',GRAY,'PDF pp.226–234: The Hip Bone; Figs.235–236. Historic pubic body terminology differs from TA98.','gray_1918'),
 ref('openstax','OpenStax Anatomy & Physiology 2e',OPEN,'Hip Bone; Ilium; Ischium; Pubis; Pelvis.','openstax'),
 ref('standard','Anatomy Standard — Hip bone',STANDARD,'Acetabulum; anterior/posterior and medial aspects; note on corpus ossis pubis.','anatomy_standard')]
SAC_REFS=[ref('gray_sac','Gray / Lewis (1918)',GRAY,'PDF pp.37–46: Sacral and Coccygeal Vertebrae; Figs.95–100.','gray_1918'),
 ref('dartmouth','Dartmouth — Basic Human Anatomy, Chapter 39',DAR,'Sacrum and Coccyx; Figs.39-10 and 39-11.','dartmouth_bha')]
COC_REF=ref('indiran','Indiran V, Sivakumar V, Maduraimuthu P (2017). Coccygeal Morphology on Multislice Computed Tomography in a Tertiary Hospital in India.',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5662850/','Introduction; Results: variable segments and fusion, not a measurement of BP3D.','indiran_2017',pmid='29093777',doi='10.4184/asj.2017.11.5.694',access='full_text')
JOINT_REFS=[HIP_REFS[1],ref('joints','NCBI Bookshelf NBK538523 — Pelvic Joints','https://www.ncbi.nlm.nih.gov/books/NBK538523/',
 'Indexed text: SI, pubic symphysis, S5–Co1 and intervening disc. Full page blocked by reCAPTCHA.','statpearls_pelvic_joints',access='indexed_text')]
PASS_REFS=[HIP_REFS[0],ref('passways','Semmelweis University — Dorsal regions',
 'https://semmelweis.hu/anatomia/files/2016/08/hj-dorsreg-eng.pdf',
 'Greater and lesser sciatic foramina: conversion of notches by sacrotuberous and sacrospinous ligaments.','semmelweis')]
CANAL_REFS=[HIP_REFS[0],ref('obturator','NCBI Bookshelf NBK554529 — Obturator Hernia',
 'https://www.ncbi.nlm.nih.gov/books/NBK554529/','Anatomy: obturator canal at superior aspect of foramen and relation to membrane.','statpearls_obturator',access='indexed_text')]
PELVIS_REFS=[ref('gray_pelvis','Gray / Lewis (1918)',GRAY,'PDF pp.236–239: The Pelvis; superior/inferior circumference and pubic arch.','gray_1918'),HIP_REFS[1]]
RING_REF=ref('ao_ring','AO Research Institute — AOTK System Innovations 2017',
 'https://media.aofoundation.org/innovations/-/media/project/aocd/innovations/files/20170120tk20innovations.pdf?rev=e61b252603084e45a107784498b5345b',
 'Printed p.54 / PDF p.56: A CT-based anatomical evaluation of the pelvic ring; Fig.1 three ring-building bones. No individual geometry transferred.','ao_ari_2017',access='full_text')

# Code -> representation and anatomical definition. Bilateral records reuse facts,
# never coordinates. A line here denotes a crest path; width still needs a mask.
HIP={
 2:('space','Впадина на наружной стороне тазовой кости; включает суставную полулунную поверхность и несуставную ямку.'),
 3:('line','Костный край впадины прерывается её вырезкой; не тождествен мягкотканной вертлужной губе.'),
 4:('area','Несуставная углублённая поверхность центрального отдела вертлужной впадины.'),
 5:('space','Разрыв нижнего отдела костного края впадины; поперечная связка не является костным мешем.'),
 6:('area','Подковообразная суставная площадка вокруг ямки; костная основа и суставной хрящ различаются.'),
 7:('volume','Костная перекладина из ветви седалищной и нижней ветви лобковой части одной тазовой кости.'),
 8:('space','Отверстие между лобковой и седалищной частями; в живом теле в основном закрыто мембраной.'),
 9:('space','Выемка заднего края между нижней задней подвздошной и седалищной остями; без связок не замкнутое отверстие.'),
 102:('volume','Утолщённая часть подвздошной кости у вертлужной впадины, ниже крыла.'),
 103:('area','Неглубокое бороздчатое поле над вертлужным краем; требуется полоса поверхности, а не произвольный центр.'),
 104:('volume','Расширенная верхняя костная часть с внутренней и наружной поверхностями и толщиной.'),
 105:('line','Валик внутренней поверхности между подвздошной ямкой и малым тазом; часть пограничной линии.'),
 106:('area','Широкий верхний край крыла с наружной и внутренней губами и промежуточной полосой; одной кривой вся поверхность не задаётся.'),
 107:('line','Наружный край подвздошного гребня; для ширины губы нужна отдельная разметка.'),
 108:('volume','Утолщение наружной губы подвздошного гребня; не математическая точка.'),
 109:('area','Промежуточная полоса гребня между двумя губами; термин «линия» не отменяет ширины площадки.'),
 110:('line','Внутренний край подвздошного гребня; линия не определяет ширину губы.'),
 111:('volume','Костный выступ на переднем конце подвздошного гребня.'),
 112:('volume','Передний выступ ниже верхней передней ости, над вертлужной впадиной.'),
 113:('volume','Костный выступ на заднем конце подвздошного гребня.'),
 114:('volume','Задний выступ ниже верхней задней ости и выше большой седалищной вырезки.'),
 115:('area','Вогнутая внутренняя поверхность крыла над дугообразной линией.'),
 116:('area','Наружная поверхность крыла, на которой проходят три ягодичные линии.'),
 117:('line','Протяжённый передний ягодичный валик на наружной поверхности крыла; ход должен быть размечен на данном экземпляре.'),
 118:('line','Задний ягодичный валик на наружной поверхности крыла; выраженность изменчива.'),
 119:('line','Нижний ягодичный валик над вертлужным отделом; может быть слабо выражен.'),
 120:('area','Задний отдел внутренней поверхности подвздошной кости, включающий ушковидную поверхность и бугристость.'),
 121:('area','Собственная суставная площадка подвздошной части, обращённая к крестцу; это не весь SI-сустав.'),
 122:('area','Шероховатая площадка над и позади ушковидной поверхности.'),
 202:('volume','Массивный седалищный отдел у задненижней части вертлужной впадины.'),
 203:('volume','Костная ветвь, соединяющая седалищный отдел с нижней ветвью лобковой части.'),
 204:('volume','Объёмное нижнее утолщение седалищной части с несколькими поверхностями.'),
 205:('volume','Костный выступ между большой и малой седалищными вырезками.'),
 206:('space','Выемка между седалищной остью и бугром; связочные границы малого отверстия отдельно.'),
 302:('volume','В принятой здесь иерархии TA98 тело лобковой кости включает симфизиальную поверхность, лобковый бугорок и гребень. В атласах встречается иная граница тела; её нельзя автоматически переносить на сетку.'),
 303:('volume','Выступ лобкового отдела у латерального конца лобкового гребня.'),
 304:('area','Медиальная площадка лобкового тела; межлобковый диск и весь симфиз не принадлежат одной этой поверхности.'),
 305:('line','Верхний край лобкового тела между бугорком и симфизиальным отделом.'),
 306:('volume','Верхняя костная ветвь лобковой части между телом и вертлужным отделом.'),
 307:('volume','Возвышение у соединения подвздошной и лобковой частей; это части одной взрослой тазовой кости.'),
 308:('line','Гребень верхней лобковой ветви, продолжающий дугообразную линию в направлении лобкового бугорка.'),
 309:('line','Костный гребень верхней лобковой ветви у запирательного отверстия; не весь гребень лобковой кости.'),
 310:('area','Бороздчатая поверхность снизу верхней лобковой ветви; образует костную часть стенки запирательного канала.'),
 311:('volume','Передний костный бугорок у запирательного края; требуется проверка самого выступа.'),
 312:('volume','Непостоянный задний запирательный бугорок. Скобки TA98 обозначают вариабельность; наличие на данном меше не подтверждено.'),
 313:('volume','Нижняя ветвь лобковой части, продолжающаяся в седалищную ветвь.'),
}
SAC={
 2:('area','Верхний отдел крестца: площадка тела S1, крылья и задние элементы вокруг входа в канал. Основание не ограничивается площадкой тела S1.'),
 3:('line','Выступающий передний край основания тела S1; часть границы входа в малый таз.'),
 4:('area','Верхняя поверхность латеральной массы по обе стороны тела S1; две стороны требуют отдельной разметки.'),
 5:('volume','Парные костные отростки S1, несущие суставные площадки для нижних отростков L5.'),
 6:('volume','Парные латеральные массы крестца по бокам отверстий; это объёмные костные части.'),
 7:('area','Парные ушковидные площадки боковых частей крестца для сочленения с тазовыми костями.'),
 8:('area','Парные шероховатые поверхности позади ушковидных площадок.'),
 9:('area','Передняя вогнутая поверхность крестца; обычные поперечные линии и отверстия не гарантируют их числа у любого варианта.'),
 10:('line','Несколько поперечных валиков между сросшимися крестцовыми телами; одна точка не представляет весь набор.'),
 11:('space','Внутрикостные межпозвоночные проходы крестца, связанные с крестцовым каналом и передними/задними выходами. Это не отверстие L5–S1.'),
 12:('space','Обычно четыре пары выходов на тазовой поверхности крестца; отдельная проверка каждой стороны и уровня.'),
 13:('area','Задняя поверхность крестца с продольными гребнями и задними отверстиями.'),
 14:('line','Срединный ряд сросшихся остистых элементов; протяжённый гребень, не единственная вершина.'),
 15:('space','Обычно четыре пары выходов на дорсальной поверхности крестца.'),
 16:('line','Парные гребни сросшихся суставных элементов медиальнее задних отверстий.'),
 17:('line','Парные гребни поперечных элементов латеральнее задних отверстий.'),
 18:('volume','Два костных рога по сторонам крестцовой щели; одна исходная точка не подтверждает оба.'),
 19:('space','Продолжение позвоночного канала внутри крестца; поверхность задней стенки не является его просветом.'),
 20:('space','Дефект нижней задней стенки крестцового канала между рогами; форма и уровень вариабельны.'),
 21:('volume','Нижний суженный конец крестца, несущий поверхность соединения с копчиком; не только её центр.'),
}
COC={1:('volume','Копчик обычно состоит из 3–5 рудиментарных сегментов, чаще четырёх; число и степень сращения изменчивы. Сращение всех сегментов не обязательно. Копчик анатомически отличается от крестца, даже при объединённой модели.'),
     2:('volume','Парные верхние костные выступы первого копчикового сегмента, обращённые к крестцовым рогам.')}
PAIRED={4,5,6,7,8,11,12,15,16,17,18}

def requirement(p):
    needs={'point':'Независимо принятая точечная локализация.', 'line':'Принятая линия на конкретном меше; ширина отдельно.',
           'area':'Принятая маска всей поверхности, а не только поверхностный маркер.',
           'space':'Принятые границы и просвет; костные стенки отличать от хрящей и связок.',
           'volume':'Принятая сегментация костной части или пространственного комплекса.'}[p['geometryKind']]
    if p.get('anatomicalMultiplicity') in ('paired','multiple','paired_multiple'):
        needs+=' Каждую сторону/уровень принимать отдельно.'
    if p.get('anatomicalOwner')=='coccyx' or p.get('requiresCoccyxBoundary'):
        needs+=' Нужны граница крестца/копчика и сегментация того же образца (GEO-007).'
    p['geometryRequirements']=dict(status='unverified_extent',coordinateReuse=False,neededEvidence=needs,source=REPORT)
    p['geometryReview']=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False)
    p['modelNote']=(p.get('modelNote','')+' '+needs).strip()
    return p

def review(p):
    if p['b'] not in ('sacrum','hip_bone','hip_bone_left') or p['t']!='ta':return p
    code=p['c'];n=int(code.rsplit('.',1)[1]);hip=code.startswith('A02.5.01.');coc=code.startswith('A02.2.06.')
    kind,definition=(HIP if hip else COC if coc else SAC)[n]
    p.update(geometryKind=kind,geometryKindReason=definition,anatomicalDefinition=definition)
    refs=deepcopy(HIP_REFS if hip else SAC_REFS)
    if coc:refs.append(deepcopy(COC_REF));p['anatomicalOwner']='coccyx'
    p['refs']=p.get('refs',[])+refs
    p['evidenceScope']='Источники проверяют определение, тип и каталог; не принимают старые p/n, все прежние прикрепления мышц или точные размеры.'
    p['anatomicalMultiplicity']='single' if hip else ('paired_multiple' if n in (11,12,15) and not coc else 'paired' if (n in PAIRED and not coc) or (coc and n==2) else 'multiple' if n==10 and not coc else 'single')
    if hip:
        p['side']='left' if p['b'].endswith('_left') else 'right'
        if n>=102:
            part='ilium' if n<200 else 'ischium' if n<300 else 'pubis'
            # Keep TA98 grouping for 312; atlas differences are explicit, not a guessed mask.
            p['partOf']=f'extra_{p["b"]}_{part}'
        if p['b']=='hip_bone_left':p['x']=definition+' Левый экземпляр: координаты правой стороны не переносились.'
        if n==312:
            p['applicability']='variant_presence_unverified';p.pop('partOf',None)
            p['modelNote']='TA98 помещает термин в лобковую группу; Gray описывает задний бугорок на седалищном крае. Группа каталога не принимается за сегментацию части.'
        if n==302:p['modelNote']='Разные атласы по-разному проводят границу тела лобковой кости; здесь сохранена иерархия TA98.'
    if p['id']=='sac_basis':p['x']=definition
    if p['id']=='cox_acetabulum':p['x']=p['x'].replace('Её образуют тела трёх костей — подвздошной, седалищной и лобковой','Её образуют подвздошная, седалищная и лобковая части тазовой кости')
    if p['id']=='coc_os_coccygis':
        p['x']=p['x'].replace('Копчик — 3–5 сросшихся рудиментарных позвонков ниже крестца.',definition)
    if coc and n==2:p['partOf']='coc_os_coccygis'
    if p.get('p'):
        p['modelNote']=p.get('modelNote','')+' Сохранён исходный обзорный маркер; его анатомическая точность и полнота покрытия не приняты.'
    return requirement(targeted_review(p))

def extra(b,key,ru,lat,kind,text,refs,**kw):
    return requirement(targeted_review(dict(id='extra_'+b+'_'+key,b=b,t='additional',ru=ru,lat=lat,g='Дополнительные образования',m=[],p=None,n=None,
        geometryKind=kind,geometryKindReason=text,x=text,refs=deepcopy(refs),educationAvailable=False,
        nomenclatureStatus='descriptive_term_without_assigned_TA98_code',**kw)))

def additional_records(bones):
    for p in targeted_records(bones):yield requirement(p)
    for bone in ('hip_bone','hip_bone_left'):
        if bone not in bones:continue
        side='left' if bone.endswith('_left') else 'right';label='слева' if side=='left' else 'справа'
        for key,ru,lat,code in [('ilium','Подвздошная часть тазовой кости','os ilium','A02.5.01.101'),('ischium','Седалищная часть тазовой кости','os ischii','A02.5.01.201'),('pubis','Лобковая часть тазовой кости','os pubis','A02.5.01.301')]:
            p=extra(bone,key,ru+' '+label,lat,'volume','Одна из трёх частей взрослой тазовой кости. Самостоятельная карточка части не означает отдельный меш или отдельную взрослую кость.',HIP_REFS,side=side,educationCode=code)
            p['nomenclatureStatus']='TA98_part_term';p['refs'].append(ref('ta_'+code,'FIPAT TA98',FIPAT,code,'fipat'));yield p
        for key,ru,lat,description in [
          ('obturator_canal','Запирательный канал','canalis obturatorius','Проход у верхнего края запирательного отверстия; костная борозда и запирательная мембрана участвуют в его стенках. Не всё запирательное отверстие.'),
          ('greater_sciatic_foramen','Большое седалищное отверстие','foramen ischiadicum majus','Проход у большой седалищной вырезки, замкнутый с участием крестцово-остистой и крестцово-бугорной связок. Вырезка и отверстие различаются.'),
          ('lesser_sciatic_foramen','Малое седалищное отверстие','foramen ischiadicum minus','Проход у малой седалищной вырезки с участием крестцово-остистой и крестцово-бугорной связок. Одной костной сетки недостаточно.')]:
            yield extra(bone,key,ru+' '+label,lat,'space',description,CANAL_REFS if key=='obturator_canal' else PASS_REFS,side=side,softTissueBoundaryRequired=True)
    if 'sacrum' not in bones:return
    for side,label in [('right','справа'),('left','слева')]:
        yield extra('sacrum','superior_articular_surface_'+side,'Верхняя суставная поверхность крестца '+label,'facies articularis superior','area',
            'Суставная площадка верхнего отростка S1 для нижней суставной поверхности L5. Отдельно от объёма отростка.',SAC_REFS,side=side,partOf='sac_processus_articularis_superior')
    for key,ru,lat,kind,text in [
        ('coccyx_base','Основание копчика','basis ossis coccygis','area','Верхний отдел копчика с площадкой соединения с верхушкой крестца.'),
        ('coccyx_apex','Верхушка копчика','apex ossis coccygis','volume','Нижний конец копчика; форма и направление изменчивы, сегмент по одной точке не определяется.')]:
        yield extra('sacrum',key,ru,lat,kind,text,SAC_REFS+[COC_REF],anatomicalOwner='coccyx',partOf='coc_os_coccygis')
    yield extra('sacrum','sacrococcygeal_joint','Крестцово-копчиковое соединение','junctura sacrococcygea','volume',
        'Соединение верхушки крестца и основания копчика, обычно с межпозвоночным диском; степень сращения изменчива. Это соединение двух анатомических костей, а не собственный выступ крестца.',
        [SAC_REFS[0],JOINT_REFS[1],COC_REF],entityKind='joint',requiresCoccyxBoundary=True,
        anatomicalParticipants=['sacrum','coccyx'],relatedLandmarks=['sac_apex','coc_os_coccygis','extra_sacrum_coccyx_base'])

def shared_records():
    definitions=[
      ('sacroiliac_right','Правый крестцово-подвздошный сустав','articulatio sacroiliaca','volume',['hip_bone','sacrum'],'joint','Соединение правой подвздошной кости и крестца. Собственные ушковидные поверхности — участники, но не весь сустав; хрящи и связки отдельно.',JOINT_REFS),
      ('sacroiliac_left','Левый крестцово-подвздошный сустав','articulatio sacroiliaca','volume',['hip_bone_left','sacrum'],'joint','Соединение левой подвздошной кости и крестца. Костные площадки не определяют суставную щель и связочный комплекс.',JOINT_REFS),
      ('pubic_symphysis','Лобковый симфиз','symphysis pubica','volume',['hip_bone','hip_bone_left'],'joint','Соединение симфизиальных поверхностей обеих лобковых частей с межлобковым диском и связками. Это не поверхность только одной стороны.',JOINT_REFS),
      ('pubic_arch','Лобковая дуга','arcus pubicus','line',['hip_bone','hip_bone_left'],'bony_boundary','Дуга под лобковым симфизом, образованная нижними ветвями лобковых и ветвями седалищных частей обеих сторон.',HIP_REFS[:2]),
      ('subpubic_angle','Подлобковый угол','angulus subpubicus','space',['hip_bone','hip_bone_left'],'angular_region','Угол между правой и левой сторонами лобковой дуги. Численное значение для этого образца не назначено.',HIP_REFS[:2]),
      ('pelvic_brim','Пограничная линия таза','linea terminalis','line',['hip_bone','hip_bone_left','sacrum'],'bony_boundary','Общая граница через мыс и передние края крыльев крестца, дугообразные линии, гребни лобковых костей и верхний край симфиза. Локальные линии сохраняют собственные ID.',HIP_REFS[:2]),
      ('pelvic_inlet','Вход в малый таз','apertura pelvis superior','space',['hip_bone','hip_bone_left','sacrum'],'space','Пространство внутри пограничной линии таза; отличается от самой линии и от одной дугообразной линии.',HIP_REFS[:2]),
      ('pelvic_outlet','Выход из малого таза','apertura pelvis inferior','space',['hip_bone','hip_bone_left','sacrum'],'space','Нижняя апертура ограничена лобковой дугой/нижним краем симфиза, седалищными буграми, крестцово-бугорными связками и верхушкой копчика. Запись крестца даёт доступ к копчику объединённой модели, но не подменяет его вклад.',HIP_REFS[:2]),
      ('pelvic_ring','Тазовое кольцо','','volume',['hip_bone','hip_bone_left','sacrum'],'osteoligamentous_complex','Комплекс двух тазовых костей, крестца и соединяющих их SI-сочленений и симфиза. Это не отдельная кость, не только линия входа и не готовая костная маска.',JOINT_REFS),
    ]
    codes={'pubic_arch':'A02.5.02.003','subpubic_angle':'A02.5.02.004','pelvic_brim':'A02.5.02.007','pelvic_inlet':'A02.5.02.008','pelvic_outlet':'A02.5.02.009'}
    for key,ru,lat,kind,bones,entity,text,refs in definitions:
        refs=deepcopy(PELVIS_REFS if key in codes else refs);role='component' if entity in ('joint','osteoligamentous_complex') else 'boundaryContribution'
        if key=='pelvic_ring':refs.append(deepcopy(RING_REF))
        relations=[dict(bone=b,role='adjacentContext' if key=='pelvic_outlet' and b=='sacrum' else role,refs=[r['id'] for r in refs]) for b in bones]
        p=dict(id='shared_pelvis_'+key,b=bones[0],t='additional',ru=ru,lat=lat,x=text,g='Общие образования таза',m=[],p=None,n=None,
            refs=refs,geometryKind=kind,geometryKindReason=text,entityKind=entity,relations=relations,catalogueBones=[],anchors=[],educationAvailable=False,
            nomenclatureStatus='descriptive_term_without_assigned_TA98_code',softTissueBoundaryRequired=True)
        if key in codes:
            p.update(educationCode=codes[key],nomenclatureStatus='TA98_term');p['refs'].append(ref('ta_'+key,'FIPAT TA98',FIPAT,codes[key],'fipat'))
        if key=='pelvic_outlet':p.update(requiresCoccyxBoundary=True,relatedLandmarks=['coc_os_coccygis','extra_sacrum_coccyx_apex'])
        if key=='pelvic_inlet':p['relatedLandmarks']=['shared_pelvis_pelvic_brim']
        if key=='pelvic_ring':p['relatedLandmarks']=['shared_pelvis_sacroiliac_right','shared_pelvis_sacroiliac_left','shared_pelvis_pubic_symphysis']
        if key=='pubic_symphysis':p['relatedLandmarks']=['cox_facies_symphysialis','context_hip_bone_left_A02_5_01_304']
        if key.startswith('sacroiliac_'):
            p['side']=key.split('_')[-1];p['relatedLandmarks']=['sac_facies_auricularis','cox_facies_auricularis' if p['side']=='right' else 'context_hip_bone_left_A02_5_01_121']
        yield requirement(p)

# Published through the existing context generator, leaving hand-authored regional
# data and all unrelated bone fields intact.
BONE_PATCHES={
 'hip_bone':dict(ru='Правая тазовая кость',side='right',x='Правая тазовая кость взрослого объединяет подвздошную, седалищную и лобковую части. Сращение происходит в ходе созревания; единую точную возрастную границу для всех образований не назначаем.',refs=HIP_REFS),
 'hip_bone_left':dict(side='left'),
 'sacrum':dict(x='Крестец обычно образован пятью сросшимися позвонками; возможны варианты. Сочленяется с L5, обеими тазовыми костями и копчиком. Копчиковая область включена в существующую объединённую модель, но её точная граница и число сегментов не приняты (GEO-007).',refs=SAC_REFS+[COC_REF])}

"""Thigh/knee/leg catalogue: explicit anatomical decisions, never reflected coordinates."""
from copy import deepcopy
from left_lower_proximal_stage6 import admit as admit_left_models, NOTE as EDUCATIONAL_LEFT_NOTE
from ta98 import T, BONE

REPORT='research/stage5-lower-proximal-report-2026-10-19.md'
OWNERS={'femur','patella','tibia','fibula'}
GRAY='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
SOB='https://archive.org/download/atlastextbookofh01sobouoft/atlastextbookofh01sobouoft_djvu.txt'
TA='https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1027%20A2F%20EN.htm'
def ref(key,title,url,locator,access='full_text'):
    return dict(id='lower_proximal_'+key,title=title,url=url,locator=locator,access=access,checked='2026-10-19')

def refs(b):
    loc={'femur':('6c.3: upper extremity, shaft, lower extremity; PDF pp.242–249','Femur, printed pp.95–99, Figs.137–141'),
         'patella':('6c.4: surfaces, borders, apex; PDF pp.260–262','Patella, printed p.99, Figs.142–143'),
         'tibia':('6c.5: extremities, shaft borders/surfaces; PDF pp.262–270','Tibia, printed pp.99–101, Figs.144–147,150–152'),
         'fibula':('6c.6: extremities, borders/surfaces; PDF pp.270–273','Fibula, printed p.101, Figs.148–152')}[b]
    return [ref('gray_'+b,'Gray / Lewis (1918) — '+b,GRAY,loc[0]),
            ref('sobotta_'+b,'Sobotta / McMurrich (1914), Vol. I — '+b,SOB,loc[1]),
            ref('ta98','FIPAT / IFAA — TA98, bones of lower limb',TA,'A02.5.04–07; names, not specimen geometry','official_list')]

# Keys are individual TA entries, not name-based rules. Types describe the entity;
# a trace represents a ridge/groove path, never its complete cross-section.
FEMUR={
2:('volume','Головка — объёмная проксимальная часть бедренной кости; её суставное покрытие не тождественно всей головке.'),
3:('area','Ямка головки — ограниченное углубление её поверхности, а не математическая точка.'),
4:('volume','Шейка соединяет головку с телом; это объёмный участок кости, а не ось или угол.'),
5:('volume','Большой вертел — латеральный костный выступ проксимального конца.'),
6:('area','Вертельная ямка — углублённая поверхность медиально у основания большого вертела.'),
7:('volume','Малый вертел — заднемедиальный выступ ниже шейки.'),
8:('volume','Третий вертел — непостоянный выступ верхнего отдела ягодичной бугристости. Его наличие у этого образца не установлено.'),
9:('line','Межвертельная линия проходит спереди у перехода шейки в тело; нужна трасса, а не одна точка.'),
10:('line','Межвертельный гребень соединяет вертелы сзади; линейная трасса не определяет высоту гребня.'),
11:('volume','Квадратный бугорок — локальное утолщение межвертельного гребня.'),
12:('volume','Тело — диафиз между проксимальным и дистальным концами.'),
13:('line','Шероховатая линия — продольный гребень сзади тела; её губы имеют собственные записи.'),
14:('line','Латеральная губа составляет латеральную границу шероховатой линии.'),
15:('line','Медиальная губа составляет медиальную границу шероховатой линии.'),
16:('line','Гребенчатая линия идёт от области малого вертела к шероховатой линии сзади.'),
17:('area','Ягодичная бугристость — протяжённое шероховатое поле под большим вертелом; отдельный третий вертел является вариантом.'),
18:('area','Подколенная поверхность — заднее дистальное поле между надмыщелковыми линиями.'),
19:('line','Медиальная надмыщелковая линия ограничивает подколенную поверхность медиально.'),
20:('line','Латеральная надмыщелковая линия ограничивает подколенную поверхность латерально.'),
21:('volume','Медиальный мыщелок — объёмная часть дистального конца, включающая суставную поверхность.'),
22:('volume','Медиальный надмыщелок — внесуставной костный выступ над медиальным мыщелком.'),
23:('volume','Приводящий бугорок — локальный выступ над медиальным надмыщелком.'),
24:('volume','Латеральный мыщелок — объёмная часть дистального конца, включающая суставную поверхность.'),
25:('volume','Латеральный надмыщелок — внесуставной выступ над латеральным мыщелком.'),
26:('line','Подколенная борозда — ход сухожилия на латеральном мыщелке; трасса не заменяет полную поверхность борозды.'),
27:('area','Надколенниковая поверхность — передний суставной участок дистального конца бедренной кости.'),
28:('space','Межмыщелковая ямка — выемка между мыщелками сзади; нужна граница пространства, а не точка на стенке.'),
29:('line','Межмыщелковая линия отделяет межмыщелковую ямку от подколенной поверхности.')}
PATELLA={
2:('line','Основание — широкий верхний край надколенника; для прикрепления сухожилия нужна отдельная площадь.'),
3:('point','Верхушка обозначает нижний полюс надколенника. Точка полюса не обозначает всю площадь прикрепления связки.'),
4:('area','Суставная поверхность занимает верхнюю часть задней поверхности надколенника; нижний задний участок несуставной. Продольный гребень разделяет суставную поверхность на медиальную и более широкую латеральную части, соприкасающиеся с бедренной костью.'),
5:('area','Передняя поверхность — шероховатая выпуклая поверхность надколенника.')}
TIBIA={
2:('area','Верхняя суставная поверхность включает медиальную и латеральную площадки. Мениски покрывают их частично, а не разделяют полностью все контактные поверхности.'),
3:('volume','Медиальный мыщелок — медиальная объёмная часть проксимального конца.'),
4:('volume','Латеральный мыщелок — латеральная часть проксимального конца; малоберцовая суставная поверхность выделена отдельно.'),
5:('area','Малоберцовая суставная поверхность расположена сзади и латерально на латеральном мыщелке.'),
6:('area','Переднее межмыщелковое поле лежит перед межмыщелковым возвышением между суставными площадками.'),
7:('area','Заднее межмыщелковое поле лежит позади межмыщелкового возвышения.'),
8:('volume','Межмыщелковое возвышение состоит из костных выступов между площадками; это не вся область прикрепления крестообразных связок.'),
9:('volume','Медиальный межмыщелковый бугорок — медиальная составляющая межмыщелкового возвышения.'),
10:('volume','Латеральный межмыщелковый бугорок — латеральная составляющая межмыщелкового возвышения.'),
11:('volume','Тело большеберцовой кости — диафиз с тремя поверхностями и тремя краями.'),
12:('area','Бугристость большеберцовой кости — протяжённое шероховатое поле спереди ниже мыщелков; точка не задаёт площадь прикрепления связки.'),
13:('area','Медиальная поверхность тела лежит между передним и медиальным краями.'),
14:('area','Задняя поверхность тела лежит между медиальным и межкостным краями.'),
15:('line','Линия камбаловидной мышцы — косой гребень верхней части задней поверхности тела.'),
16:('area','Латеральная поверхность тела лежит между передним и межкостным краями.'),
17:('line','Передний край идёт от бугристости к медиальной лодыжке: выражен в верхних двух третях, дистально сглаживается.'),
18:('line','Медиальный край разделяет медиальную и заднюю поверхности тела.'),
19:('line','Межкостный край обращён к малоберцовой кости и ограничивает место прикрепления перепонки; сам край не является перепонкой.'),
20:('volume','Медиальная лодыжка — дистальный выступ большеберцовой кости.'),
21:('line','Лодыжковая борозда проходит сзади медиальной лодыжки; нужны трасса и границы сухожильного ложа.'),
22:('area','Суставная поверхность медиальной лодыжки обращена латерально к таранной кости.'),
23:('area','Малоберцовая вырезка — вогнутая латеральная поверхность дистального конца, участвующая в межберцовом соединении; не самостоятельный сустав.'),
24:('area','Нижняя суставная поверхность обращена к блоку таранной кости; отличается от лодыжковой поверхности.')}
FIBULA={
2:('volume','Головка — проксимальное утолщение малоберцовой кости; она сочленяется с большеберцовой, а не с бедренной костью.'),
3:('area','Суставная поверхность головки обращена к малоберцовой поверхности латерального мыщелка большеберцовой кости.'),
4:('volume','Верхушка головки — выступ проксимального конца; её нельзя подменять всем объёмом головки.'),
5:('volume','Шейка — суженная часть непосредственно ниже головки.'),
6:('volume','Тело малоберцовой кости — длинный диафиз; TA98 различает три именованные поверхности, края и отдельно медиальный гребень.'),
7:('area','Латеральная поверхность диафиза находится между передним и задним краями; её направление изменяется дистально.'),
8:('area','Медиальная поверхность по TA98 находится между передним и межкостным краями. Историческое именование поверхностей отличается.'),
9:('area','Задняя поверхность по TA98 находится между межкостным и задним краями; медиальный гребень делит её на участки.'),
10:('line','Медиальный гребень — отдельная продольная граница на задней поверхности; не дубликат межкостного края.'),
11:('line','Передний край разделяет латеральную и медиальную поверхности диафиза.'),
12:('line','Межкостный край обращён к большеберцовой кости и служит костной границей прикрепления перепонки.'),
13:('line','Задний край отделяет латеральную поверхность диафиза от задней.'),
14:('volume','Латеральная лодыжка — дистальный конец малоберцовой кости; суставная поверхность и ямка выделены отдельно.'),
15:('area','Суставная поверхность латеральной лодыжки обращена медиально к таранной кости.'),
16:('area','Ямка латеральной лодыжки — несуставное углубление позади её суставной поверхности.'),
17:('line','Лодыжковая борозда — заднее ложе сухожилий малоберцовых мышц; трасса не подтверждает её полный контур.')}
TABLES={'femur':FEMUR,'patella':PATELLA,'tibia':TIBIA,'fibula':FIBULA}
NOTE='Координата старого маркера, если есть, не подтверждает анатомическую локализацию или протяжённость. Нужны разметка конкретного образца и анатомическая приёмка; для сустава также хрящи, капсула и связки.'
LEFT_NOTE=EDUCATIONAL_LEFT_NOTE

def limits(p):
    left=p.get('side')=='left'
    p.update(educationAvailable=False,geometryRequirements=dict(status='unverified_extent',neededEvidence=LEFT_NOTE if left else NOTE),
             geometryReview=dict(coordinateAcceptance=False,extentAcceptance=False,report=REPORT),
             lowerProximalReview=dict(source=REPORT,scope='catalogue_and_representation',geometryAccepted=False),
             modelNote=(p.get('modelNote','')+' '+(LEFT_NOTE if left else NOTE)).strip())
    return p

def review(record):
    b=record['b']; root=b.removesuffix('_left')
    if root not in OWNERS:return record
    p=deepcopy(record); p['side']='left' if b.endswith('_left') else 'right'
    if p['t']=='ta':kind,definition=TABLES[root][int(p['c'].split('.')[-1])]
    else:kind,definition='area','Место начала или прикрепления — область, а не точка. Тип не подтверждает полный состав прикрепления или границы на этом образце.'
    p.update(geometryKind=kind,geometryKindReason=definition,anatomicalDefinition=definition)
    p.setdefault('refs',[])
    for r in refs(root):
        if r['id'] not in {q.get('id') for q in p['refs']}:p['refs'].append(r)
    # Correct overgeneralised descriptions without reauthoring unrelated attachments.
    if p.get('c') in {'A02.5.05.004','A02.5.06.002','A02.5.06.017'}:p['x']=definition
    if p.get('c') in {'A02.5.04.021','A02.5.04.024'}:
        p['x']=definition+' Соответствующий мениск покрывает большеберцовую суставную площадку частично; не весь контакт с большеберцовой костью осуществляется через мениск.'
    if p.get('c')=='A02.5.04.008':
        p.update(anatomicalVariant=True,specimenPresence='unverified',anchorStatus='unverified',x=definition)
        p['refs'] += [ref('third_trochanter','Bolanowski et al. (2005) — third trochanter', 'https://pubmed.ncbi.nlm.nih.gov/16228951/', 'Abstract; PMID verified by EFetch; occurrence in an independent skeletal sample, not this GLB.', 'indexed_abstract')]
    if root=='fibula' and p.get('c','').endswith(('.006','.007','.008','.009','.010','.011','.012','.013')):
        p['note']='Номенклатура TA98 сохранена. Gray (1918) описывает четыре поверхности/края, Sobotta (1914) — три поверхности и дополнительный межкостный гребень; исторические названия не перенесены как новые дубликаты.'
    return limits(p)

LEFT_BONES={}
for b,ru,code,fma in [('femur','бедренная кость','A02.5.04.001','FMA24475'),('patella','надколенник','A02.5.05.001','FMA24487'),('tibia','большеберцовая кость','A02.5.06.001','FMA24478'),('fibula','малоберцовая кость','A02.5.07.001','FMA24481')]:
    LEFT_BONES[b+'_left']=dict(ru=('Левый ' if b=='patella' else 'Левая ')+ru,lat=b,code=code,g='b_limb',sec='leg',side='left',
        sub='thigh' if b in {'femur','patella'} else 'shank',noModel=True,candidateSourceId=fma,
        x={'femur':'Кость левого бедра; проксимально сочленяется с тазовой костью, дистально — с большеберцовой костью и надколенником.',
           'patella':'Сесамовидная кость в сухожилии четырёхглавой мышцы перед левым коленным суставом; сочленяется с бедренной костью.',
           'tibia':'Медиальная опорная кость левой голени; сочленяется с бедренной, малоберцовой и таранной костями.',
           'fibula':'Латеральная кость левой голени; головка сочленяется с большеберцовой костью, латеральная лодыжка — с таранной.'}[b],note=LEFT_NOTE,refs=refs(b))

RIGHT_PATCHES={b:dict(side='right',ru=v['ru'].replace('Левая','Правая').replace('Левый','Правый'),refs=refs(b)) for b in OWNERS for v in [LEFT_BONES[b+'_left']]}

admit_left_models(LEFT_BONES)

def left_records():
    for b in sorted(OWNERS):
        for c in BONE[b]:
            definition=TABLES[b][int(c.split('.')[-1])][1]
            yield review(dict(id='context_'+b+'_left_'+c.replace('.','_'),b=b+'_left',t='ta',c=c,ru=T[c][1],lat=T[c][0],
                x=definition,p=None,n=None,m=[],**({'inc':1} if T[c][2]=='inc' else {})))

def extra(b,key,ru,kind,text,source_refs,**fields):
    return limits(dict(id='extra_'+b+'_'+key,b=b,t='additional',ru=ru,lat=fields.pop('lat',''),x=text,p=None,n=None,m=[],
        geometryKind=kind,geometryKindReason=text,anatomicalDefinition=text,side='left' if b.endswith('_left') else 'right',
        g='Дополнительные образования',refs=deepcopy(source_refs),nomenclatureStatus='descriptive_term_without_assigned_TA98_code',**fields))

def additional_records(left=False):
    suffix='_left' if left else ''; side='слева' if left else 'справа'
    for b in ('femur','tibia','fibula'):
        yield extra(b+suffix,'nutrient_foramina','Питательные отверстия '+side,'space',
            'Входы сосудистых каналов в диафизе. Число, размеры и точные положения индивидуальны; карточка не задаёт единственного обязательного отверстия.',refs(b))
    yield extra('patella'+suffix,'posterior_nonarticular','Задний несуставной участок надколенника '+side,'area',
        'Нижний участок задней поверхности надколенника, ниже суставной поверхности. Не является дополнительной костью или суставной фасеткой.',refs('patella'))
    sob_joint=ref('sob_joints','Sobotta / McMurrich (1914) — Lower limb articulations',SOB,'Hip-joint; Knee-joint; Tibiofibular articulation; Tibiofibular syndesmosis, Figs.212–226.')
    ncbi=ref('ncbi_leg','Cantrell, Imonugo, Varacallo (2023) — Leg Bones','https://www.ncbi.nlm.nih.gov/sites/books/NBK537024/',
        'Introduction; Structure and Function: joint participants only. Muscle origin/insertion wording in this source is not adopted.')
    for key,owner,ru,lat,bones,text in [
        ('hip_joint','femur','Тазобедренный сустав','articulatio coxae',['femur','hip_bone'],'Синовиальное сочленение головки бедренной кости и вертлужной впадины тазовой кости. Костные меши не представляют всю капсулу, губу или хрящ.'),
        ('knee_joint','femur','Коленный сустав','articulatio genus',['femur','tibia','patella'],'Сустав бедренной, большеберцовой костей и надколенника. Малоберцовая кость не образует его суставных поверхностей; связь с коллатеральной связкой не превращает её в четвёртую суставную кость.'),
        ('proximal_tibiofibular_joint','tibia','Межберцовый сустав','articulatio tibiofibularis',['tibia','fibula'],'Проксимальное синовиальное сочленение головки малоберцовой кости с латеральным мыщелком большеберцовой. Отличается от дистального синдесмоза.'),
        ('distal_tibiofibular_syndesmosis','tibia','Межберцовый синдесмоз','syndesmosis tibiofibularis',['tibia','fibula'],'Дистальное фиброзное соединение большеберцовой и малоберцовой костей. Не отдельная кость и не синовиальный межберцовый сустав.')]:
        source=[sob_joint,ncbi] if key!='hip_joint' else [sob_joint,ref('ta_hip','FIPAT — Hip joint','https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/03.6.07%20TA98%20EN.htm','A03.6.07.001; nomenclature','official_list'),ref('openstax','OpenStax A&P 2e — Bones of the Lower Limb','https://openstax.org/books/anatomy-and-physiology-2e/pages/8-4-bones-of-the-lower-limb','Femur: head articulates with hip acetabulum.')]
        code={'hip_joint':'A03.6.07.001','knee_joint':'A03.6.08.001','proximal_tibiofibular_joint':'A03.6.09.001','distal_tibiofibular_syndesmosis':'A03.6.05.001'}[key]
        source += [ref('ta_joints','FIPAT / IFAA — TA98 joints of lower limb','https://ifaa.unifr.ch/Public/EntryPage/TAH1510%20Part98A3%20EN.htm',code,'official_list')]
        p=extra(owner+suffix,key,ru+' '+side,'volume',text,source,lat=lat,
            anatomicalEntity='fibrous_joint' if 'syndesmosis' in key else 'joint',catalogueBones=[],anchors=[],
            relations=[dict(bone=b+suffix,role='component') for b in bones])
        p.update(educationCode=code,nomenclatureStatus='TA98_term')
        yield p

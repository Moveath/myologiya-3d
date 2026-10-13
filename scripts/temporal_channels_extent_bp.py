"""Native multiview extent audit for the two BodyParts3D temporal bones.

Screenshots use explicit vectors and preserve each side independently. The audit
is separate from point localization and never rewrites the primary markers.
"""
from pathlib import Path
import json
import hashlib
import argparse
from collections import Counter
import ta98,head_terms
from head_temporal_evidence import DESCRIPTIONS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/temporal_channels/extent-bp'
VIEWS={'ant':{'d':[0,0,1],'up':[0,1,0]},'post':{'d':[0,0,-1],'up':[0,1,0]},
       'xminus':{'d':[-1,0,0],'up':[0,1,0]},'xplus':{'d':[1,0,0],'up':[0,1,0]},
       'sup':{'d':[0,1,0],'up':[0,0,-1]},'inf':{'d':[0,-1,0],'up':[0,0,1]},
       'oblique_sup':{'d':[.5,1,.5],'up':[0,0,-1]},'oblique_inf':{'d':[.5,-1,.5],'up':[0,0,1]},
       'oblique_sup_opposite':{'d':[-.5,1,.5],'up':[0,0,-1]},'oblique_inf_opposite':{'d':[-.5,-1,.5],'up':[0,0,1]}}

# Independent whole-bone views were read for both meshes. These are extent
# decisions, not a copy of the existing 'surface' localization classification.
# Each tuple is status, required macro-extent, observed geometry, preferred views.
DECISIONS={
2:('complete','Наружная макроформа пирамиды: три поверхности, края и верхушка; внутренние каналы оцениваются отдельными терминами.','Треугольная каменистая часть прослеживается от основания к верхушке, её наружные поверхности доступны с нескольких направлений.',['sup','inf','ant','post']),
3:('complete','Весь затылочный край сосцевидной области.','Задний контур прослеживается между верхним и нижним окончаниями, без обрезанного конца сетки.',['post','inner']),
4:('complete','Весь выступ от основания до вершины с наружной и внутренней сторон.','Сосцевидный выступ и его вершина присутствуют, видимы с четырёх направлений.',['outer','inner','post','inf']),
5:('complete','Продольное дно и оба борта сосцевидной вырезки в пределах названного углубления.','На нижней стороне видна продольная вырезка медиальнее сосцевидного выступа; её макроконтур осмотрен снизу и косо.',['inf','inferior_oblique']),
6:('complete','Непрерывный макропрофиль костной борозды от её верхнего до нижнего участка на данной кости.','Широкий изогнутый желоб внутренней сосцевидной области прослеживается целиком на собственной поверхности каждой стороны.',['inner','post','sup']),
12:('complete','Терминальная верхушка пирамиды и переход в её соседние поверхности.','Переднемедиальный конец пирамиды не обрезан и доступен сверху, снизу и спереди.',['sup','inf','ant']),
21:('complete','Всё наружное поле передней поверхности пирамиды между её краями; мелкие борозды и отверстия оцениваются отдельно.','Обращённая вверх поверхность прослеживается от основания до верхушки; макрограницы доступны.',['sup','superior_oblique','ant']),
22:('partial','Полная костная пластинка крыши барабанной полости с наружной и обращённой в полость сторонами.','Видна наружная область крыши; её внутренняя сторона и толщина не отделены уверенно от сглаженного массива.',['sup','superior_oblique']),
23:('partial','Целиком различимое локальное дугообразное возвышение, включая границы перехода к окружающей поверхности.','Невысокое возвышение различимо, но его края сглажены; отдельная точка не подтверждает полный контур.',['sup','superior_oblique']),
28:('partial','Дно и наружный контур тройничного вдавления у верхушки.','Мелкое вдавление видно только как сглаженный участок передней поверхности; полный контур уверенно не отделён.',['sup','ant']),
29:('complete','Верхнее ребро пирамиды от основания до верхушки.','Непрерывное ребро между передней и задней поверхностями прослеживается по всей длине.',['sup','inner','superior_oblique']),
31:('complete','Всё наружное поле задней поверхности пирамиды между краями; детали проходов оцениваются отдельно.','Задняя поверхность присутствует от основания до верхушки и осмотрена с внутренней и задней сторон.',['inner','post','sup']),
32:('partial','Полный естественный край внутреннего слухового отверстия с подтверждённым входом в проход.','Различим край углубления; открытый переход в полный костный проход этой поверхностью не подтверждён.',['inner','post']),
37:('complete','Задний край пирамиды между основаниями соседних участков, включая макроочертание вырезки.','Нижний контур задней поверхности прослеживается на нижнем и внутреннем видах.',['inner','inf','post']),
39:('complete','Полное макроочертание яремной вырезки на заднем крае.','Выемка соответствующего края и оба её перехода в соседние участки видны снизу и изнутри.',['inner','inf','inferior_oblique']),
40:('complete','Всё наружное поле нижней поверхности пирамиды; внутрикостные ходы и малые апертуры проверяются отдельно.','Нижняя поверхность сохранена от верхушки до сосцевидно-яремной области; макрограницы доступны в нижнем и косом видах.',['inf','inferior_oblique','ant']),
41:('complete','Дно и макрокрай яремной ямки; отверстия малых канальцев не включены.','Углубление яремной области с окружающими возвышениями доступно снизу и косо; это оценка широкой ямки, не всех её микродеталей.',['inf','inferior_oblique','inner']),
45:('complete','Полное макроочертание той же яремной вырезки при описании нижней поверхности.','Видна та же выемка, что у A02.1.06.039; повтор TA98 сохранён, отдельное новое образование не выдумано.',['inf','inner','inferior_oblique']),
47:('complete','Весь шиловидный выступ от корня до собственного конца.','Удлинённый отросток и его закруглённый терминальный контур целиком присутствуют в исходной сетке.',['outer','inner','ant','post']),
52:('partial','Барабанная часть с наружной и внутренней стенкой прохода и её естественными краями.','Наружная нижняя стенка узнаваема; внутренняя граница, кольцо и полный костный просвет не разрешены этой сеткой.',['outer','inf','inferior_oblique']),
54:('partial','Полный естественный край наружного слухового отверстия с открытым продолжением в костный проход.','Входной контур и углубление различимы; полный открытый просвет не подтверждён.',['outer','ant','inf']),
60:('partial','Оболочка основания шиловидного отростка по всей окружности и её граница с соседней барабанной частью.','Виден участок костного охвата корня; вся окружность и её точная граница не отделены на сглаженной сетке.',['outer','inf','inferior_oblique']),
61:('complete','Вся чешуйчатая пластинка с обеими поверхностями и наружным краем; сосудистые борозды отдельно.','Тонкая широкая пластинка полностью представлена с двух сторон и в боковом профиле.',['outer','inner','ant','post']),
62:('complete','Весь верхний теменной край чешуйчатой части.','Зубчатый верхний контур прослеживается от переднего до заднего перехода.',['outer','inner','ant','post']),
63:('complete','Вся выемка края между чешуйчатой и сосцевидной областями.','Широкая выемка задневерхнего края видна на наружной и внутренней сторонах обеих самостоятельных сеток.',['outer','inner','post']),
64:('complete','Весь передний клиновидный край чешуйчатой части.','Передний контур чешуи виден с наружной и внутренней сторон; его протяжённость не выводилась из одной точки.',['outer','inner','ant']),
65:('complete','Всё наружное поле височной поверхности чешуйчатой части; тонкие сосудистые следы отдельно.','Наружная поверхность чешуи доступна целиком в боковом и косом видах.',['outer','ant','post']),
67:('complete','Скуловой отросток от корней до переднего суставного конца.','Весь вытянутый отросток и его передний конец видны в боковом, верхнем и нижнем видах.',['outer','sup','inf','ant']),
68:('complete','Макропуть надсосцевидного гребня от заднего корня скулового отростка к сосцевидной области.','Широкое продолжение заднего корня над сосцевидной областью прослеживается на наружном рельефе.',['outer','post','sup']),
71:('complete','Дно и наружный макроконтур нижнечелюстной ямки позади суставного бугорка.','Впадина снизу позади бугорка видна в нижнем и косом видах с обеими её сторонами.',['inf','inferior_oblique','ant']),
72:('partial','Всё поле костной суставной поверхности в передней части нижнечелюстной ямки с различимой задней границей; хрящ отдельно.','Передняя область ямки и переход к бугорку видимы, но граница суставной части с остальной ямкой на сглаженной сетке не отделена уверенно; полная ямка не доказывает полный отдельный суставной участок.',['inf','inferior_oblique','ant']),
73:('complete','Полный макроконтур суставного бугорка перед нижнечелюстной ямкой.','Переднее выпуклое возвышение у корня скулового отростка и его переходы в соседние поверхности видимы снизу и косо.',['inf','inferior_oblique','ant']),
78:('complete','Всё внутреннее поле мозговой поверхности чешуйчатой части; мелкие сосудистые борозды отдельно.','Внутренняя широкая вогнутая поверхность чешуи доступна целиком на медиальном и косом видах.',['inner','post','superior_oblique']),
}

def required(row):
    code=row['code'];lat=row['lat'];num=int(code.split('.')[-1])
    if num in DECISIONS:return {'type':'macro_surface_or_border','criterion':DECISIONS[num][1]}
    if num==8:return {'type':'variant_passage','criterion':'На реально содержащем вариант образце: естественный костный край и просвет сосцевидного отверстия; иллюстрация типичного места не считается геометрией.'}
    if num in (9,13,17,18,19,33,35,42,44,49,55,11,16):return {'type':'channel','criterion':'Весь именованный костный ход между анатомическими концами, его доступные стенки и сообщения; поверхность нерва/сосуда не заменяет стенки.'}
    if num in (14,15,24,26,36,43,48):return {'type':'aperture','criterion':'Полный естественный край данного устья и его открытый переход в соответствующий костный проход; точка на одном краю недостаточна.'}
    if num in (7,25,27,30,38,66):return {'type':'groove','criterion':'Весь различимый путь именно названной борозды с дном и её бортами, а не ожидаемая топографическая область.'}
    if num in (74,75,76,77):return {'type':'fissure','criterion':'Непрерывная естественная граница названных частей кости по всей различимой протяжённости; не искусственный край сегментации.'}
    if num==10:return {'type':'channel_bend','criterion':'Костные стенки первого коленца и соединение лабиринтного с барабанным сегментом; изгиб нерва недостаточен.'}
    if num==20:return {'type':'thin_septum','criterion':'Сохранившаяся пластинка между двумя полуканалами с обеими сторонами и всей протяжённостью.'}
    if num==51:return {'type':'cavity','criterion':'Вся барабанная полость с доступными костными стенками, границами и естественными сообщениями; одно поле стенки недостаточно.'}
    if num==53:return {'type':'ring','criterion':'Всё костное барабанное кольцо до его верхних концов; форма мембраны не заменяет костной границы.'}
    return {'type':'small_surface_feature','criterion':'Целиком различимое образование с собственным контуром, дном или вершиной и переходом к соседней кости; не одна выбранная точка.'}

def audit():
    source=json.loads((OUT/'view-inputs.json').read_text(encoding='utf-8'))
    lookup={}
    for v in source['views']:
        p=ROOT/v['screenshot'];assert p.exists(),p
        lookup[(v['bone'],v['key'])]={**{k:v[k] for k in ('d','up','parts','screenshot','clipping')},'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    primary=json.loads((ROOT/'pins_head/temporal-extra.json').read_text(encoding='utf-8'))
    prior=json.loads((ROOT/'research/temporal-feature-review.json').read_text(encoding='utf-8'))
    prior={r['code']:r for r in prior['outcomes']}
    native=json.loads((ROOT/'pins_head/temporal-native-features.json').read_text(encoding='utf-8'))
    native={r['c']:r for r in native['markers']}
    channels=json.loads((ROOT/'pins_head/temporal-channels.json').read_text(encoding='utf-8'))
    channels={r['ta98']:r for r in channels['structures']}
    rows=[]
    for p in primary:
        b=p['bone'];side=b.split('_')[-1];c=p['code'];num=int(c.split('.')[-1]);lat,ru,_=ta98.T[c]
        views={'outer':'xminus' if side=='right' else 'xplus','inner':'xplus' if side=='right' else 'xminus',
               'superior_oblique':'oblique_sup' if side=='right' else 'oblique_sup_opposite','inferior_oblique':'oblique_inf' if side=='right' else 'oblique_inf_opposite'}
        if num in DECISIONS:
            status,criterion,observed,keys=DECISIONS[num]
            limitations=['Исходная форма сглажена; полнота заявлена только для указанного макрообъёма проверки. Микродетали не включены.'] if status=='complete' else [observed,'Дальнейшая проверка требует исходника, в котором виден весь указанный объём.']
        else:
            status='not_demonstrated';observed=p['modelNote'];keys=['outer','inner','sup','inf']
            limitations=[prior[c]['remaining_work']] if c in prior else ['Вариант не подтверждён на этой сетке; типичное место не доказывает его наличие.']
        assessment={'source':'BodyParts3D 3.0','mesh':source['mesh'],'meshSha256':source['mesh_sha256'],
                    'views':[lookup[(b,views.get(k,k))] for k in keys],'status':status,'confirmedExtent':observed,'limitations':limitations,
                    'scope':'same-source-and-side; external macrogeometry at author model scale',
                    'viewer':{'mode':'main','part':b,'view':{k:lookup[(b,views.get(keys[0],keys[0]))][k] for k in ('d','up')}}}
        assessments=[assessment]
        if side=='right' and c in native:
            m=native[c];ev=m['evidence'];nv=[]
            for vk,sk in [('view','screenshot'),('crossView','crossScreenshot')]:
                if vk in ev and sk in ev:
                    path=ROOT/ev[sk];nv.append({**ev[vk],'parts':['temporal_bone'],'screenshot':ev[sk],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'clipping':None})
            assessments.append({'source':'OpenEar ZETA; independent right specimen','mesh':'site/skull-openear.glb','views':nv,'status':'partial','confirmedExtent':m['modelNote'],'limitations':['Самостоятельный препарат; не регистрация на BodyParts3D и не замена его координат.','Маркер подтверждает только локальный участок стенки или края.'],'scope':'independent-specimen-example',
                                'viewer':{'mode':'openear','part':'temporal_bone','marker':m['id'],'view':m['view']}})
        if side=='right' and c in channels:
            m=channels[c]
            assessments.append({'source':'OpenEar ZETA; independent right specimen','mesh':'site/skull-temporal-channels.glb','views':[{**m['view'],'parts':[m['id']],'screenshot':'build_head/temporal_channels/'+m['id']+'-view1.png','clipping':None}],
                                'status':'partial','confirmedExtent':m['modelNote'],'limitations':['Полные конечные апертуры и тонкая стенка не завершены.','Самостоятельный препарат, не совмещение с BodyParts3D.'],'scope':'independent-specimen-example','evidenceReport':'research/temporal-channel-review.json',
                                'viewer':{'mode':'channels','part':m['id'],'view':m['view']}})
        for a in assessments:
            for v in a['views']:
                if 'sha256' not in v:
                    path=ROOT/v['screenshot']
                    if path.exists():v['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
                    else:v['screenshot']=None;v['screenshotLimitation']='Ракурс сохранён в исходной метаинформации; снимок см. reviewed-views.json.'
        best='complete' if any(a['status']=='complete' for a in assessments) else 'partial' if any(a['status']=='partial' for a in assessments) else 'not_demonstrated'
        rows.append({'bone':b,'code':c,'side':side,'ru':ru,'lat':lat,'originalLocalization':p['localization'],
                     'requiredExtent':required({'code':c,'lat':lat}),'assessments':assessments,'bestStatus':best,
                     'completeFeatureGeometry':best=='complete',
                     'refs':[{**r,'locator':r.get('locator',r['title']+'; '+lat)} for r in DESCRIPTIONS[c]['refs'][:2]],
                     'reviewMethod':'Independent multiview inspection of both source meshes; extent criterion chosen per feature; original point flags not used as completeness proof.'})
    assert len(rows)==154
    for b in ('temporal_right','temporal_left'):assert {r['code'] for r in rows if r['bone']==b}==set(ta98.BONE[b])
    additional_checks=[]
    variant_path=ROOT/'research/temporal-variant-geometry-review.json'
    if variant_path.exists():
        variant_review=json.loads(variant_path.read_text(encoding='utf-8'))
        additional_checks.append({'report':'research/temporal-variant-geometry-review.json',
                                  'sha256':hashlib.sha256(variant_path.read_bytes()).hexdigest(),
                                  'codes':['A02.1.06.008','A02.1.03.024','A02.1.04.035'],
                                  'newConfirmedGeometry':variant_review['new_confirmed_variant_meshes'],
                                  'statusEffect':'None: no named complete passage or new qualified variant specimen confirmed.',
                                  'datasetLicenseFinding':'Schaeper et al. XPCT article is CC BY 4.0; GRO DOI10.25625/V3YSYD volumes are CC BY-NC 4.0 and were not imported.'})
        for row in rows:
            if row['code']=='A02.1.06.008':
                row['additionalSourceChecks']=[{'report':additional_checks[0]['report'],
                                               'conclusion':'Два Halle CT-кандидата и три другие сетки проверены; собственный ход к sigmoid sulcus не подтверждён. Это не доказательство отсутствия варианта.',
                                               'statusEffect':'unchanged'}]
    result={'schema':'skull-extent-review-v1','sourceRegion':'temporal','scope':'154 BodyParts3D records; declared whole macrogeometry, separate native examples and limits',
            'completeMeans':'Whole explicitly defined macrofeature is visible in the reviewed source. Not microscopic accuracy, automatic promotion of surface markers, or external expert certification.',
            'externalAnatomistSignoff':False,'noLocalizationChanges':True,'counts':dict(Counter(r['bestStatus'] for r in rows)),'additionalSourceChecks':additional_checks,'rows':rows}
    (ROOT/'research/temporal-feature-extent-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result['counts'])

def jobs():
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for side in ('right','left'):
        bone='temporal_'+side
        for key,v in VIEWS.items():
            name=bone+'-'+key
            cmd=f'show({json.dumps(bone)},{json.dumps(v)},{json.dumps(bone+" · "+key)});true'
            (OUT/(name+'.job')).write_text(cmd,encoding='utf-8')
            records.append({'bone':bone,'key':key,**v,'parts':[bone],'screenshot':str((OUT/(name+'.png')).relative_to(ROOT)).replace('\\','/'),'command':cmd,'clipping':None})
    (OUT/'view-inputs.json').write_text(json.dumps({'source':'BodyParts3D 3.0','mesh':'build_head/head_hi.glb','mesh_sha256':hashlib.sha256((ROOT/'build_head/head_hi.glb').read_bytes()).hexdigest(),'views':records},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--jobs',action='store_true');parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    if args.jobs:jobs()
    if args.audit:audit()

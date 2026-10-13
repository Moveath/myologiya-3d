"""Build independent, dimensionless teaching diagrams for missing head muscles.

No donor surface, copyrighted illustration or commercial atlas is traced. The
control points below are layout choices encoding cited qualitative relations;
they are NOT anatomical measurements, segmented contours, or BodyParts3D pins.
Each entry has its own scene at the origin and must be viewed independently.
Run with the project Python environment. The original atlas files are untouched.
"""
from pathlib import Path
import hashlib
import json
import math
from copy import deepcopy

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from head_muscles import MUSCLE_TEMPLATES
import manifest_head

ROOT = Path(__file__).resolve().parents[1]
DEGUM = 'https://www.degum.de/fileadmin/dokumente/sektionen/kopf-hals/Informationen_zum_Fach/Instruction_for_the_sonography_of_facial_muscles_v06a.pdf'
TA98 = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1673%20A2F%20EN.htm'

def ref(title, url, locator, family):
    return dict(title=title, url=url, locator=locator, independentSource=family)

EAR_REFS = [
    ref('DEGUM: анатомия мимических мышц', DEGUM,
        'PDF с. 6, таблица Muscles in the range of the outer ear: три строки auricularis, Origin / Approach.', 'degum-zilles-table'),
    ref('Liugan, Zhang, Cakmak, 2018', 'https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2017.00752/full',
        'Innervation of the Auricular Muscles, первый абзац; Fig. 1A: положение трёх наружных ушных мышц относительно раковины.', 'liugan-zhang-cakmak-2018'),
    ref('Rüschenschmidt и соавт., 2022: исследование ушных мышц', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8775077/',
        '3.1 Cadaver Preparations; Fig. 1A–C; Supplementary Fig. S3: отдельные передняя, верхняя и задняя ушные мышцы. Общий соавтор Volk с руководством DEGUM; не засчитывается как дополнительная независимая редакция таблицы.', 'degum-zilles-table'),
]
DS_REFS = [
    ref('Cook, Lucarelli, Lemke, 2001', 'https://pubmed.ncbi.nlm.nih.gov/11766019/',
        'Abstract, Results: frontal process of maxilla; dermal insertion above medial canthal tendon. Вариабельность числа головок.', 'cook-lucarelli-lemke'),
    ref('Hur и соавт., 2022', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264148',
        'Introduction, абзац с DS; Results; Fig. 1: верхнечелюстное начало, медиальная часть брови и неодинаковые связи с соседними мышцами.', 'hur-lee-jung-schneider-2022'),
]
DEEP_REFS = [
    ref('Kakizaki и соавт., 2010', 'https://pubmed.ncbi.nlm.nih.gov/20719297/',
        'Abstract, Results: начало мышцы Horner от заднего слёзного гребня и передней области медиальной стенки глазницы.', 'kakizaki-2010'),
    ref('Location and tension of the medial palpebral ligament, 2013', 'https://pubmed.ncbi.nlm.nih.gov/24220420/',
        'Abstract: от заднего слёзного гребня латерально к хрящу века, глубже поверхностного слоя медиальной связки.', 'mpl-location-2013'),
    ref('DEGUM: слёзная часть круговой мышцы глаза', DEGUM,
        'PDF с. 4: M. orbicularis oculi / Pars lacrimalis, Origin и Approach.', 'degum-zilles-table'),
]
CILIARY_REFS = [
    ref('Lipham, Tawfik, Dutton, 2002', 'https://pubmed.ncbi.nlm.nih.gov/11897949/',
        'Abstract, Purpose / Results / Conclusions: histologic relations of Riolan muscle in the eyelid margin.', 'lipham-tawfik-dutton-2002'),
    ref('Wulc и соавт., 1987: Where is the gray line?', 'https://pubmed.ncbi.nlm.nih.gov/3632419/',
        'Abstract: гистологическое соответствие серой линии поверхностной части orbicularis / Riolan.', 'wulc-1987'),
    ref('Knop и соавт., 2011: анатомия мейбомиевых желёз', 'https://pubmed.ncbi.nlm.nih.gov/21450915/',
        'Fig. 5–6, гистологические срезы свободного края века: краевые волокна Riolan.', 'knop-workshop-2011'),
]
TRANSVERSE_REFS = [
    ref('DEGUM: носовая мышца', DEGUM,
        'PDF с. 5: M. nasalis / Pars transversa, Origin и Approach.', 'degum-zilles-table'),
    ref('Anderson, Henneberg, Norris, 2008: Anatomy of the nasal profile', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2526105/',
        'Results, раздел мышц; Fig. 3b и Fig. 4: начало на верхней челюсти, поперечное продолжение над носом, индивидуальная изменчивость.', 'anderson-henneberg-norris-2008'),
    ref('Hur и соавт., 2010', 'https://pubmed.ncbi.nlm.nih.gov/20512646/',
        'Abstract, Results: transverse nasalis от maxilla восходит; описаны варианты двух брюшек и соединений.', 'hur-nasalis-2010'),
]
ALAR_REFS = [
    ref('DEGUM: носовая мышца', DEGUM,
        'PDF с. 5: M. nasalis / Pars alaris, Origin и Approach.', 'degum-zilles-table'),
    ref('Park, Hur, 2024: крыльная часть носовой мышцы', 'https://pubmed.ncbi.nlm.nih.gov/39136748/',
        'Abstract, Results / Conclusion: верхнечелюстное начало; область крыла; дополнительные волокна к соседним мышцам присутствуют не во всех препаратах.', 'park-hur-2024'),
    ref('Sonoanatomy of the Nasal Ala, 2025', 'https://pubmed.ncbi.nlm.nih.gov/40152086/',
        'Fig. 2B caption и Fig. 4: maxilla — alar facial crease / deeper external ala skin. Fig. 2 переработана по Hur и не считается третьим независимым наблюдением границ.', 'nasal-ala-ultrasound-2025'),
]
ORIS_REFS = [
    ref('TA98: части круговой мышцы рта', TA98,
        'A04.1.03.024 Pars marginalis; A04.1.03.025 Pars labialis — номенклатура, не геометрия.', 'ifaa-ta98'),
    ref('DEGUM: круговая мышца рта', DEGUM,
        'PDF с. 5: M. orbicularis oris, перечислены pars marginalis и pars labialis; пространственная граница не задана.', 'degum-zilles-table'),
    ref('Rogers и соавт., 2009: микроанатомия orbicularis oris', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2631558/',
        'Results / Discussion: исследование различает marginalis и peripheralis; эти слова нельзя автоматически приравнять к паре TA98 marginalis / labialis.', 'rogers-2009'),
    ref('Anatomy, Head and Neck, Orbicularis Oris Muscle', 'https://www.ncbi.nlm.nih.gov/books/NBK545169/',
        'Muscles: авторы перечисляют несколько разных систем названий слоёв; точной карты к паре TA98 здесь нет.', 'statpearls-oris'),
]

RED = [195, 76, 81, 255]
FIBER = [248, 167, 151, 255]
GRAY = [164, 176, 181, 255]
PALE = [207, 219, 219, 255]
ORIGIN = [113, 130, 197, 255]
INSERT = [221, 158, 71, 255]

def tube(points, radius=.035, flatten=1., color=RED):
    """Closed elliptical tube; paths encode qualitative direction only."""
    points = np.array(points, dtype=float)
    n = len(points)
    tangent = np.gradient(points, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    binormal = np.cross(tangent, np.tile([0., 0., 1.], (n, 1)))
    tiny = np.linalg.norm(binormal, axis=1) < 1e-6
    binormal[tiny] = np.cross(tangent[tiny], [0., 1., 0.])
    binormal /= np.linalg.norm(binormal, axis=1)[:, None]
    normal = np.cross(tangent, binormal)
    theta = np.linspace(0, 2*math.pi, 12, endpoint=False)
    radii = np.broadcast_to(np.asarray(radius), (n,))
    verts = (points[:, None, :] + radii[:, None, None] * (
        np.cos(theta)[None, :, None]*binormal[:, None, :] +
        flatten*np.sin(theta)[None, :, None]*normal[:, None, :])).reshape(-1, 3)
    faces = []
    for i in range(n-1):
        for j in range(12):
            a, b = i*12+j, i*12+(j+1)%12
            faces += [[a,b,a+12],[b,b+12,a+12]]
    verts = np.vstack([verts, points[0], points[-1]])
    for j in range(12):
        faces += [[len(verts)-2,(j+1)%12,j], [len(verts)-1,(n-1)*12+j,(n-1)*12+(j+1)%12]]
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    mesh.fix_normals()
    mesh.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=color, metallicFactor=0, roughnessFactor=.78, doubleSided=True))
    return mesh

def curve(control, steps=32):
    a,b,c,d = np.asarray(control,dtype=float)
    t=np.linspace(0,1,steps)[:,None]
    return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d

def ellipse(center, radii, z=.0, start=0, end=2*math.pi, steps=70):
    a=np.linspace(start,end,steps)
    return np.array([center[0]+radii[0]*np.cos(a),center[1]+radii[1]*np.sin(a), np.full_like(a,z)]).T

def disk(center, scale, color):
    mesh=trimesh.creation.icosphere(subdivisions=2, radius=1)
    mesh.apply_scale(scale);mesh.apply_translation(center)
    mesh.visual=trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=color, metallicFactor=0, roughnessFactor=.8, doubleSided=True))
    return mesh

SCENE=trimesh.Scene()
ENTRIES=[]

def add_mesh(entry, suffix, mesh, context=False):
    name=entry['id']+'__'+suffix
    if entry.get('side')=='left':
        # An explicit schematic reflection, NOT a checked contralateral specimen.
        mesh.apply_transform(np.diag([-1.,1.,1.,1.]))
    SCENE.add_geometry(mesh,node_name=name,geom_name=name)
    entry['contextNodes' if context else 'nodes'].append(name)
    return name

def label(entry, ru, p, role='context'):
    p=list(p)
    if entry.get('side')=='left':p[0]=-p[0]
    entry['labels'].append(dict(ru=ru,p=p,role=role))

def bundle(entry, name, controls, width=.11):
    meshes=[]
    for c in controls:
        pts=curve(c)
        taper=.55+.45*np.sin(np.linspace(0,math.pi,len(pts)))
        meshes.append(tube(pts,width*taper,.30))
        # Striation is an orientation guide, not counted/mapped muscle fibres.
        meshes.append(tube(pts+[0,0,width*.33],.008,.8,FIBER))
    add_mesh(entry,name,trimesh.util.concatenate(meshes))

def base_entry(muscle, part=None, refs=()):
    base=muscle.removesuffix('_right').removesuffix('_left')
    m=MUSCLE_TEMPLATES[base]
    p=m['parts'][part] if part else m
    side='right' if muscle.endswith('_right') else 'left' if muscle.endswith('_left') else None
    side_ru={'right':'правая сторона','left':'левая сторона'}.get(side,'')
    e=dict(id=muscle+('__'+part if part else ''),muscle=muscle,part=part,
        ru=p['ru']+(' · '+side_ru if side else ''),lat=p['lat'],ta98=p['code'],side=side,
        status='educational_reconstruction',representation='independent_spatial_diagram',
        asset='skull-muscle-reconstructions.glb',nodes=[],contextNodes=[],labels=[],
        camera=dict(position=[2.4,1.4,6],target=[0,.25,0],up=[0,1,0]),
        refs=deepcopy(list(refs)),demonstrates=[],unknown=[],
        limitations=['Все размеры, толщина и контуры условные; показана пространственная связь, а не измеренная форма мышцы.',
          'Серые формы — условные ориентиры. Они не заменяют модели костей, хрящей или органов.',
          'Не совмещено с BodyParts3D. Реконструкция не меняет статус отсутствующей исходной модели.',
          'Независимая проверка анатомом не проведена; схема не используется для проверки точной формы в тесте.'],
        method='Авторские параметрические ленты по описанным в источниках отношениям. Контрольные точки заданы в независимом учебном пространстве; изображения и сетки источников не копировались.',
        coordinateSystem=dict(units='educational_unit',registeredTo=None,measured=False,
            axes='X — горизонталь схемы, Y — вверх, Z — к наблюдателю; анатомические стороны подписаны в сцене.'),
        license=dict(name='CC BY 4.0',url='https://creativecommons.org/licenses/by/4.0/',attribution='Миология 3D — авторские параметрические учебные схемы, 2026',
            sourceGeometry='Новые сетки из открытого кода scripts/head_muscle_reconstructions.py; сторонние сетки и иллюстрации не включены.'),
        review=dict(literatureChecked=True,technicalChecked=False,independentAnatomist=False,eligibleForGeometryQuiz=False))
    if side:
        e['limitations'].append('Правая и левая схемы используют явно симметричное учебное построение; индивидуальная асимметрия не воспроизведена.')
    ENTRIES.append(e)
    return e

def ear(e, kind):
    # Lateral diagram: +X anterior, +Y superior. An ear outline is orientation only.
    add_mesh(e,'auricle_outline',tube(ellipse((0,0),(.38,.65),.12),.045,.6,GRAY),True)
    add_mesh(e,'auricle_context',disk((0,0,0),(.28,.52,.07),PALE),True)
    label(e,'Ушная раковина · условный контур',[0,-.66,.1])
    label(e,'Кпереди',[1.48,-.72,0]);label(e,'Кзади',[-1.1,-.72,0])
    # Preserve already reviewed two-family attachment evidence as well as
    # the independently observed overall position. Study coauthors overlap.
    template=MUSCLE_TEMPLATES['auricularis_'+kind]
    for field in ('o','i'):
        for r in template['fieldRefs'][field]:
            if r not in e['refs']:e['refs'].append(deepcopy(r))
    if kind=='anterior':
        origins=[[1.3,y,0] for y in np.linspace(.05,.65,7)]
        ends=[[.25,.25+.035*i,.14] for i in range(7)]
        origin=[1.33,.4,0];ins=[.25,.36,.14]
        e['summary']='Схема связи височной фасциальной области с передней областью завитка ушной раковины.'
        e['demonstrates']=['Переднее положение мышцы относительно раковины.','Общее направление от височной фасциальной области к раковине.']
        e['unknown']=['Точная ширина, толщина, протяжённость начала и индивидуальные ответвления в исходном наборе отсутствуют.']
        origin_label='Височная фасция / край сухожильного шлема';ins_label='Область ости завитка'
    elif kind=='superior':
        origins=[[x,1.48,.0] for x in np.linspace(-.65,.65,9)]
        ends=[[x,.58,.10] for x in np.linspace(-.16,.16,9)]
        origin=[0,1.48,0];ins=[0,.58,.1]
        e['summary']='Схема связи сухожильного шлема с верхней областью ушной раковины.'
        e['demonstrates']=['Верхнее положение относительно раковины.','Схождение направлений к верхней области раковины.']
        e['unknown']=['Площадь апоневротического начала и индивидуальное распределение пучков не измерены.']
        origin_label='Сухожильный шлем · область начала';ins_label='Верхняя область раковины'
    else:
        origins=[[-1.15,y,-.16] for y in np.linspace(-.15,.15,4)]
        ends=[[-.12,y,-.06] for y in np.linspace(-.12,.12,4)]
        origin=[-1.15,0,-.16];ins=[-.12,0,-.06]
        e['summary']='Схема связи сосцевидной области с задней поверхностью ушной раковины.'
        e['demonstrates']=['Заднее положение мышцы.','Связь с задней поверхностью раковины в области её выпуклости.']
        e['unknown']=['Число брюшек и их точные границы изменчивы; на схеме число лент не обозначает число брюшек.']
        origin_label='Сосцевидная область · начало';ins_label='Задняя поверхность раковины'
        e['camera']['position']=[-2.4,1.1,-6]
    controls=[[o,(np.array(o)*.72+np.array(t)*.28+[0,0,.08]).tolist(),(np.array(o)*.28+np.array(t)*.72+[0,0,.08]).tolist(),t] for o,t in zip(origins,ends)]
    bundle(e,'muscle',controls,.075)
    add_mesh(e,'origin',disk(origin,(.10,.13,.055),ORIGIN),True)
    add_mesh(e,'insertion',disk(ins,(.08,.12,.045),INSERT),True)
    label(e,origin_label,origin,'origin');label(e,ins_label,ins,'insertion')

def eye_context(e):
    for direction in (1,-1):
        pts=curve([[1.05,0,.03],[.55,direction*.58,.03],[-.55,direction*.58,.03],[-1.05,0,.03]])
        add_mesh(e,'lid_'+str(direction),tube(pts,.025,.5,GRAY),True)
    label(e,'Медиально · к носу',[1.28,-.48,0]);label(e,'Латерально',[-1.2,-.48,0])

def ds(e):
    eye_context(e)
    brow=curve([[1.05,.82,.1],[.5,1.05,.1],[-.5,1.05,.1],[-1.05,.82,.1]])
    add_mesh(e,'brow',tube(brow,.04,.4,GRAY),True)
    controls=[]
    for s in np.linspace(-.07,.07,5):
        controls.append([[1+s,.20,-.06],[.95+s,.45,.03],[.76+s,.64,.09],[.67+s,.90,.13]])
    bundle(e,'muscle',controls,.055)
    origin=[1,.20,-.06];ins=[.67,.90,.13]
    add_mesh(e,'origin',disk(origin,(.12,.11,.06),ORIGIN),True)
    add_mesh(e,'insertion',disk(ins,(.17,.065,.05),INSERT),True)
    label(e,'Лобный отросток верхней челюсти · область начала',origin,'origin')
    label(e,'Кожа медиальной части брови',ins,'insertion')
    e['summary']='Условная восходящая связь верхнечелюстного начала с кожей медиальной части брови.'
    e['demonstrates']=['Положение у медиального участка брови.','Общее направление между костным началом и кожным прикреплением.']
    e['unknown']=['Границы и число головок не восстановлены; возможные соединения с соседними мышцами не показаны.']
    e['limitations'].append('В таблице DEGUM началом названа лобная кость; в исследованиях Cook и Hur — лобный отросток верхней челюсти. Схема следует двум исследованиям, расхождение сохранено.')

def oculi_deep(e):
    eye_context(e)
    origin=[1.2,0,-.4]
    add_mesh(e,'posterior_crest',tube([[1.2,y,-.4] for y in np.linspace(-.3,.3,20)],.06,.5,ORIGIN),True)
    controls=[]
    for branch in (-1,1):
        for s in np.linspace(-.045,.045,3):
            controls.append([[1.2,s,-.4],[1.05,branch*.12+s,-.31],[.77,branch*.22+s,-.12],[.58,branch*.24+s,-.02]])
    bundle(e,'muscle',controls,.04)
    label(e,'Задний слёзный гребень · условная линия',origin,'origin')
    label(e,'Переход к медиальной области век',[.58,.24,-.02],'insertion')
    e['summary']='Схема глубокого хода от заднего слёзного гребня к медиальной области век.'
    e['demonstrates']=['Медиальное глубокое положение.','Направление от гребня латерально к тканям век.']
    e['unknown']=['Точное окружение слёзных канальцев, границы пучков и взаимоотношения всех связочных слоёв не восстановлены.']
    e['limitations'].append('Верхняя и нижняя ленты обозначают направления к векам; это не сегментация отдельных брюшек и не полная модель слёзного насоса.')
    e['camera']['position']=[2.8,.8,5]

def oculi_ciliary(e):
    eye_context(e)
    meshes=[]
    for direction in (1,-1):
        path=curve([[1.0,0,.06],[.53,direction*.52,.09],[-.53,direction*.52,.09],[-1.0,0,.06]],50)
        meshes.append(tube(path,.048,.55))
    add_mesh(e,'margin_region',trimesh.util.concatenate(meshes))
    label(e,'Краевая область верхнего века',[0,.4,.09],'region')
    label(e,'Краевая область нижнего века',[0,-.4,.09],'region')
    e['summary']='Условно выделена краевая область век, соответствующая ресничному пучку.'
    e['demonstrates']=['Положение пучка у края века.','Региональная принадлежность к круговой мышце глаза.']
    e['unknown']=['Не показаны отдельные волокна вокруг железистых протоков, ресничных фолликулов и микроскопические границы.']
    e['limitations'].append('Цветная лента — обозначение области, а не сплошной изолированный цилиндр мышцы. Название fasciculus ciliaris относится к TA98; в исследованиях используется имя Riolan.')
    e['representation']='educational_region'

def nasalis(e,kind):
    # A deliberately wire-like contextual nose. No anatomical surface is claimed.
    nose=curve([[0,1.0,0],[0,.7,.4],[0,.0,.8],[0,-.1,.62]])
    add_mesh(e,'dorsum_context',tube(nose,.04,.5,GRAY),True)
    for s in (-1,1):
        ala=curve([[0,-.1,.62],[s*.35,-.5,.66],[s*.75,-.3,.30],[s*.67,.03,.20]])
        add_mesh(e,'ala_context_'+str(s),tube(ala,.04,.6,GRAY),True)
    label(e,'Спинка носа · условный ориентир',[0,.82,.3])
    if kind=='transverse':label(e,'Крыло носа · условный контур',[-.62,-.16,.35])
    if kind=='transverse':
        controls=[]
        for s in np.linspace(-.12,.12,7):
            controls.append([[-.98,-.38+s,.0],[-.8,.1+s,.08],[-.38,.43+s,.46],[0,.39+s,.49]])
        origin=[-.98,-.38,0];ins=[0,.39,.49]
        e['summary']='Направление поперечной части от верхней челюсти к апоневрозу над спинкой носа.'
        e['demonstrates']=['Восходящее и медиальное направление от боковой области основания носа.','Продолжение к апоневрозу спинки носа.']
        e['unknown']=['Границы апоневроза и соединения с соседними мышцами индивидуальны и здесь не сегментированы.']
        inslabel='Апоневроз спинки носа · область'
    else:
        controls=[]
        for s in np.linspace(-.06,.06,5):
            controls.append([[-.7+s,-.67,0],[-.67+s,-.48,.10],[-.58+s,-.25,.3],[-.52+s,-.14,.4]])
        origin=[-.7,-.67,0];ins=[-.52,-.14,.4]
        e['summary']='Направление крыльной части от верхнечелюстной области к тканям крыла носа.'
        e['demonstrates']=['Положение у основания крыла носа.','Связь верхнечелюстной области с крылом.']
        e['unknown']=['Дополнительные волокна к соседним мышцам и коже изменчивы; они не добавлены как обязательная норма.']
        inslabel='Ткани крыла носа · область'
    bundle(e,'muscle',controls,.042)
    add_mesh(e,'origin',disk(origin,(.12,.09,.04),ORIGIN),True)
    add_mesh(e,'insertion',disk(ins,(.12,.09,.04),INSERT),True)
    label(e,'Верхняя челюсть · область начала',origin,'origin');label(e,inslabel,ins,'insertion')
    e['camera']['position']=[-2.8,1.1,5]

def explain(e,summary,unknown):
    e.update(status='explanation',representation='explanation',asset=None,summary=summary,unknown=unknown,
        method='Сопоставление номенклатуры, текстов и доступной исходной геометрии; новая поверхность не создавалась.')
    e['limitations']=['Объяснение ограничения не подтверждает отсутствующую форму.','Существующая карточка и исходные модели сохранены.']

def build():
    for kind in ('anterior','superior','posterior'):
        for side in ('right','left'):
            ear(base_entry('auricularis_'+kind+'_'+side,refs=EAR_REFS),kind)
    for side in ('right','left'):
        ds(base_entry('depressor_supercilii_'+side,refs=DS_REFS))
    m=MUSCLE_TEMPLATES['transversus_menti']
    refs=[]
    for field in ('o','i','a','s'):
        for r in m['fieldRefs'][field]:
            if r not in refs: refs.append(deepcopy(r))
    e=base_entry('transversus_menti',refs=refs)
    explain(e,'Непостоянный поперечный пучок описан в литературе; отдельной подтверждённой формы в исходных моделях нет.',
        ['Границы пучка и его выраженность у данного человека неизвестны.','Отдельная функция не подтверждена двумя независимыми исследованиями.','Источники расходятся в конкретных питающих ветвях; общий сосуд не выбран произвольно.'])
    e['demonstrates']=['Карточка сохраняет сведения и разногласия источников.','Реконструкция постоянной мышцы могла бы создать ошибочное представление о норме.']
    for side in ('right','left'):
        oculi_deep(base_entry('orbicularis_oculi_'+side,'deep',DEEP_REFS))
        oculi_ciliary(base_entry('orbicularis_oculi_'+side,'ciliary',CILIARY_REFS))
        for kind in ('transverse','alar'):
            nasalis(base_entry('nasalis_'+side,kind,TRANSVERSE_REFS if kind=='transverse' else ALAR_REFS),kind)
    for part in ('marginal','labial'):
        e=base_entry('orbicularis_oris',part,ORIS_REFS)
        explain(e,'Название части сохранено по TA98. Однозначная пространственная граница этой части на исходной сетке не установлена.',
            ['В исследованиях применяются разные пары названий: marginalis / peripheralis, superficial / deep; они не приравнены автоматически к TA98 marginalis / labialis.',
             'Нет размеченного исходного образца, связывающего границы именно этой части с принятым термином TA98.'])
        e['demonstrates']=['Вся круговая мышца рта доступна в основном атласе.','Описание целой мышцы не выдано за отдельные доказанные прикрепления этой части.']
    expected_whole={base+suffix for base in MUSCLE_TEMPLATES for suffix in ([''] if base in ('orbicularis_oris','transversus_menti') else ['_right','_left']) if base+suffix not in manifest_head.MUSCLES}
    expected_parts={(base+suffix,p) for base,m in MUSCLE_TEMPLATES.items() for suffix in ([''] if base in ('orbicularis_oris','transversus_menti') else ['_right','_left']) for p in m.get('parts',{}) if p not in {part for _,part in manifest_head.MUSCLES.get(base+suffix,[])}}
    assert {e['muscle'] for e in ENTRIES if not e['part']}==expected_whole
    assert {(e['muscle'],e['part']) for e in ENTRIES if e['part']}==expected_parts
    assert len(ENTRIES)==19 and len(expected_whole)==9 and len(expected_parts)==10
    for e in ENTRIES:
        assert len({r['independentSource'] for r in e['refs']})>=2
        assert all(r['locator'] for r in e['refs'])
        assert bool(e['nodes']) == (e['status']=='educational_reconstruction')
        if e['side']=='left':e['camera']['position'][0]*=-1
        e['review']['technicalChecked']=True
    for name,mesh in SCENE.geometry.items():
        assert mesh.is_watertight and mesh.is_winding_consistent,name
        assert np.isfinite(mesh.vertices).all() and np.all(mesh.area_faces>1e-12),name
    path=ROOT/'site/skull-muscle-reconstructions.glb'
    path.write_bytes(SCENE.export(file_type='glb'))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    data=dict(version=1,created='2026-10-13',title='Мышцы: учебные реконструкции и ограничения',
        asset=path.name,sha256=digest,
        coordinateSystem=dict(units='educational_unit',registeredTo=None,measured=False),
        counts=dict(whole=9,parts=10,educational_reconstruction=16,explanation=3),
        notice='Самостоятельные объёмные схемы. Размеры и контуры условные. Они объясняют указанные отношения и не заменяют геометрию исходного препарата.',
        legend=[dict(color='#c34c51',ru='Учебное обозначение мышцы или области'),dict(color='#7182c5',ru='Область начала · условно'),dict(color='#dd9e47',ru='Область прикрепления · условно'),dict(color='#a4b0b5',ru='Контекст · условный ориентир')],
        originalGeometryStatusesChanged=False,independentAnatomistReview=False,entries=ENTRIES)
    (ROOT/'site/skull-muscle-reconstructions.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    review=dict(date='2026-10-13',status='literature_and_mesh_checks_complete',counts=data['counts'],
        authorization='User authorized source-based labelled reconstructions and explicit explanations where reconstruction is unsupported.',
        boundaries='Independent dimensionless diagrams only; no donor-model overlay, no measured volumes, no anatomical expert certification.',
        source_meshes_inspected='Existing manifest_head identifies absent objects. No source mesh contains the missing structures as separately verified objects; no bounding-box location was used.',
        geometry_checks=dict(nodes=len(SCENE.geometry),vertices=sum(len(m.vertices) for m in SCENE.geometry.values()),triangles=sum(len(m.faces) for m in SCENE.geometry.values()),
             finite=True,watertight=True,winding_consistent=True,nondegenerate=True,sha256=digest),
        entries=[{k:e[k] for k in ('id','muscle','part','status','representation','summary','demonstrates','unknown','limitations','refs','method','review')} for e in ENTRIES],
        visual_review=dict(status='pending',method='Render every independent entry from its saved view and inspect overview; no human anatomist review implied.'))
    review_path=ROOT/'research/muscle-reconstruction-review.json'
    if review_path.exists():
        old=json.loads(review_path.read_text(encoding='utf-8'))
        if old.get('geometry_checks',{}).get('sha256')==digest:
            # Keep dated visual observations of the unchanged mesh. A new
            # label/UI change still needs its own dated inspection record.
            for key in ('visual_review','shared_ui_review','visual_inspection'):
                if key in old:review[key]=old[key]
    review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(counts=data['counts'],bytes=path.stat().st_size,nodes=len(SCENE.geometry),sha256=digest)))

if __name__=='__main__':build()

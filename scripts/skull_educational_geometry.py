"""Independent teaching diagrams and explicit dispositions for skull geometry gaps.

No source mesh, marker or source-geometry verdict is changed. Coordinates below
are dimensionless diagram layout, never specimen landmarks or measurements.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
LICENSE = dict(name='CC BY 4.0', url='https://creativecommons.org/licenses/by/4.0/',
               attribution='Миология 3D — авторские учебные схемы, 2026')
COLORS = {'context': [197, 183, 154, 255], 'feature': [64, 176, 184, 255],
          'variant': [165, 106, 215, 255], 'secondary': [230, 159, 80, 255],
          'relation': [95, 145, 191, 255]}
DISCLAIMER = ('Самостоятельная учебная схема, не препарат и не результат КТ. '
              'Показано только указанное взаиморасположение или сообщение. '
              'Размеры, контуры, кривизна и расстояния условные; по схеме нельзя измерять анатомию. '
              'Она не совмещена с основным черепом и не подтверждает наличие образования у его донора.')


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf8'))


def unique_refs(refs):
    out = {}
    for r in refs:
        assert r.get('url') and r.get('locator'), r
        out[(r['url'], r['locator'])] = r
    return list(out.values())


def ellipsoid(p, radii):
    mesh = trimesh.creation.icosphere(subdivisions=2)
    mesh.vertices *= np.array(radii)
    mesh.apply_translation(p)
    return mesh


def block(p, size):
    mesh = trimesh.creation.box(extents=size)
    mesh.apply_translation(p)
    return mesh


def line(points, radius=.035):
    """Rounded solid diagram connector; never a lumen or a measured bony wall."""
    pieces = [trimesh.creation.cylinder(radius=radius, segment=[a, b], sections=12)
              for a, b in zip(points, points[1:]) if np.linalg.norm(np.array(b)-a) > 1e-8]
    pieces += [ellipsoid(p, [radius]*3) for p in points]
    return trimesh.util.concatenate(pieces)


def ring(p, radius=.32, thickness=.065, scale=(1, 1, 1)):
    mesh = trimesh.creation.torus(major_radius=radius, minor_radius=thickness,
                                  major_sections=40, minor_sections=12)
    mesh.vertices *= np.array(scale)
    mesh.apply_translation(p)
    return mesh


def curved_sheet(p, height=.8, width=.8):
    """Curled plate symbol, not a reconstruction of turbinate dimensions."""
    theta = np.linspace(-.15, 2.2, 24)
    verts = [[x, math.sin(t)*height, math.cos(t)*height]
             for x in [-width/2, width/2] for t in theta]
    faces = []
    for i in range(len(theta)-1):
        faces += [[i, i+1, i+len(theta)], [i+1, i+len(theta)+1, i+len(theta)]]
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    mesh.apply_translation(p)
    return mesh


class Diagram:
    def __init__(self, scene, id, codes, terms, known, refs, category):
        self.scene = scene
        self.data = dict(id=id, ru=terms[0], lat=terms[1], codes=codes,
                         kind='topological_diagram', category=category,
                         status='educational_reconstruction', nodeNames=[], labels=[],
                         known=known, unknown='Индивидуальная форма, размеры и наличие в основном образце не установлены.',
                         modelLimit=DISCLAIMER, refs=unique_refs(refs),
                         method='Авторская процедурная схема по текстовым анатомическим сведениям. '
                                'Чужие сетки, изображения и контуры не копировались. '
                                'Координаты заданы для читаемости схемы, без миллиметрового масштаба.',
                         camera=dict(d=[0, .3, 1], up=[0, 1, 0]), license=LICENSE,
                         completeFeatureGeometry=False, expertValidated=False,
                         allowMorphometry=False, quizEligible=False)

    def add(self, key, mesh, color='context', label=None, p=None, lat=None):
        name = f'edu|{self.data["id"]}|{key}'
        mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name=color, baseColorFactor=COLORS[color], metallicFactor=0, roughnessFactor=.78,
            doubleSided=True))
        self.scene.add_geometry(mesh, node_name=name, geom_name=name)
        self.data['nodeNames'].append(name)
        if label:
            self.data['labels'].append(dict(ru=label, lat=lat or '', p=list(p if p is not None else mesh.centroid), node=name))


def build():
    extent = read('site/skull-geometry-review.json')
    evidence = read('research/head-evidence.json')['bone_features']
    whole = read('site/skull-whole.json')['rows']
    variants = read('site/skull-study-variants.json')
    examples = {r['c']: r for r in read('site/skull-variant-examples.json')['examples']}
    by_code = defaultdict(list)
    for row in extent['rows']:
        by_code[row['c']].append(row)
    whole_code = {r['c']: r for r in whole}
    scene = trimesh.Scene()
    models = []

    def describe(c):
        if c in evidence:
            e = evidence[c]
            return e['russian'], e['latin'], e['x'], by_code[c][0]['refs']
        e = whole_code[c]
        return e['ru'], e['lat'], e['description'], e['refs']

    def diagram(id, codes, category, title=None):
        descriptions = [describe(c) for c in codes]
        d = Diagram(scene, id, codes, (title or descriptions[0][0], descriptions[0][1]),
                    ' '.join(dict.fromkeys(x[2] for x in descriptions)),
                    [r for x in descriptions for r in x[3]], category)
        d.data['claims'] = [dict(c=c, text=x[2], refs=x[3]) for c, x in zip(codes, descriptions)]
        models.append(d.data)
        return d

    # Connection diagrams represent adjacency, never a proposed true canal path.
    connections = [
        ('optic', ['A02.1.05.021'], ['Полость черепа', 'Зрительный канал', 'Глазница']),
        ('pterygoid', ['A02.1.05.053'], ['Основание крыловидного отростка', 'Крыловидный канал', 'Крылонёбная ямка']),
        ('facial', ['A02.1.06.009'], ['Дно внутреннего слухового прохода', 'Канал лицевого нерва', 'Шилососцевидное отверстие']),
        ('chorda', ['A02.1.06.011'], ['Нисходящая часть лицевого канала', 'Каналец барабанной струны', 'Барабанная полость']),
        ('carotid', ['A02.1.06.013', 'A02.1.06.014', 'A02.1.06.015'], ['Наружная апертура · снизу', 'Сонный канал', 'Внутренняя апертура · у верхушки пирамиды']),
        ('caroticotympanic', ['A02.1.06.016'], ['Сонный канал', 'Сонно-барабанные канальцы', 'Барабанная полость']),
        ('vestibular', ['A02.1.06.035', 'A02.1.06.036'], ['Преддверие внутреннего уха', 'Каналец преддверия', 'Апертура на задней поверхности пирамиды']),
        ('mastoid-canaliculus', ['A02.1.06.044'], ['Яремная ямка', 'Сосцевидный каналец', 'Барабанно-сосцевидная щель']),
        ('tympanic', ['A02.1.06.049'], ['Каменистая ямочка', 'Барабанный каналец', 'Барабанная полость']),
        ('infraorbital', ['A02.1.12.005', 'A02.1.12.004', 'A02.1.12.003'], ['Подглазничная борозда', 'Подглазничный канал', 'Подглазничное отверстие']),
        ('incisive', ['A02.1.00.061'], ['Носовая поверхность нёба', 'Резцовые каналы', 'Область резцовой ямки']),
        ('lesser-palatine', ['A02.1.13.008'], ['Пирамидальный отросток', 'Малые нёбные каналы', 'Малые нёбные отверстия']),
    ]
    for id, codes, labels in connections:
        d = diagram(id, codes, 'connections')
        d.data['unknown'] = ('Схема подтверждает только перечисленные связи. Полный трёхмерный ход, '
                             'ветвление, диаметр и стенки в выбранном препарате по ней не установлены.')
        d.data['modelLimit'] += (' Шары означают области, цветная перемычка — связь между ними, '
                                 'а не форму полостей, костных стенок или нерва. '
                                 'Одна перемычка для названия во множественном числе не задаёт число каналов.')
        d.add('start', ellipsoid([-1.5, 0, 0], [.35]*3), label=labels[0], p=[-1.5, -.55, 0])
        d.add('connection', line([[-1.2, 0, 0], [1.2, 0, 0]], .11), 'feature', labels[1], [0, .48, 0])
        d.add('end', ellipsoid([1.5, 0, 0], [.35]*3), 'secondary', labels[2], [1.5, -.55, 0])

    d = diagram('musculotubarius', ['A02.1.06.017', 'A02.1.06.018', 'A02.1.06.019', 'A02.1.06.020'],
                'relations', 'Два полуканала и перегородка')
    d.add('superior', line([[-1.2, .42, 0], [1.2, .42, 0]], .16), 'feature',
          'Полуканал мышцы, напрягающей барабанную перепонку', [0, .82, 0])
    d.add('inferior', line([[-1.2, -.42, 0], [1.2, -.42, 0]], .16), 'secondary', 'Полуканал слуховой трубы', [0, -.9, 0])
    d.add('septum', block([0, 0, 0], [2.7, .12, .75]), 'context', 'Перегородка', [1.7, 0, 0])
    d.data['modelLimit'] += ' Две цветные оси означают полуканалы; их сечение и общая наружная стенка не восстановлены.'

    # Variants: local relation examples, not transplanted onto an ordinary skull.
    for c in dict.fromkeys(v['c'] for v in variants):
        id = 'variant-' + c.replace('.', '-')
        d = diagram(id, [c], 'variants')
        d.data['example'] = {k: examples[c][k] for k in ('image', 'caption', 'url', 'locator', 'license')}
        d.data['unknown'] = ('Не установлены наличие этого варианта у донора основного черепа и его '
                             'индивидуальные размеры, число, форма и степень выраженности. '
                             'Схема показывает один условный пример, а не частоту встречаемости.')
        if c == 'A02.1.03.007':
            for sign, name in [(-1, 'Одна половина лобной чешуи'), (1, 'Другая половина лобной чешуи')]:
                d.add('half'+str(sign), ellipsoid([sign*.76, 0, -.12], [.73, 1.15, .22]), label=name,
                      p=[sign*1.25, -.9, .12])
            points = [[.035*math.sin(i*1.7), -1+i*.1, .14] for i in range(21)]
            d.add('suture', line(points, .035), 'variant', 'Сохраняющийся срединный шов', [0, 1.4, .15])
        elif c == 'A02.1.04.013':
            d.add('lower', ellipsoid([0, -.45, 0], [1.3, .65, .2]), label='Остальная затылочная чешуя', p=[0, -1.35, 0])
            d.add('separate', ellipsoid([0, .65, 0], [1.05, .42, .2]), 'variant', 'Отдельная верхняя часть', [0, 1.35, 0])
            d.data['modelLimit'] += ' Контур разделения условный; схема не воспроизводит конкретный тип швов межтеменной кости.'
        elif c in ['A02.1.03.024', 'A02.1.04.035', 'A02.1.05.008', 'A02.1.05.054']:
            contexts = {'A02.1.03.024': 'Переднемедиальная область глазницы',
                        'A02.1.04.035': 'Нижняя сторона яремного отростка',
                        'A02.1.05.008': 'Латеральный край бугорка седла',
                        'A02.1.05.054': 'Задний край латеральной крыловидной пластинки'}
            d.add('surface', block([0, -.32, 0], [2.8, .35, .8]), label=contexts[c], p=[0, -.95, 0])
            cone = trimesh.creation.cone(radius=.22, height=.75, sections=32)
            cone.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [0, 1, 0]))
            cone.apply_translation([0, -.15, 0])
            d.add('projection', cone, 'variant', d.data['ru'], [0, .98, 0])
            d.data['modelLimit'] += ' Выступ и участок поверхности показаны условными фигурами; направление на экране не задаёт оси черепа.'
        elif c in ['A02.1.05.037', 'A02.1.05.039']:
            if c == 'A02.1.05.037':
                d.add('ovale', ring([.85, 0, 0], .42, scale=[.75, 1, 1]), label='Овальное отверстие', p=[.95, -.8, 0])
                d.add('variant', ring([-.85, .18, 0], .18), 'variant', 'Венозное отверстие · медиальнее', [-.9, .85, 0])
            else:
                for key, p, r, label, color in [('ovale', [-1, 0, 0], .38, 'Овальное отверстие', 'context'),
                                              ('petrosum', [0, 0, 0], .16, 'Каменистое отверстие', 'variant'),
                                              ('spinosum', [1, 0, 0], .22, 'Остистое отверстие', 'secondary')]:
                    d.add(key, ring(p, r), color, label, [p[0], .8 if key == 'petrosum' else -.8, 0])
            d.data['modelLimit'] += ' Кольца обозначают отверстия; расстояния, диаметры и внутренние каналы не воспроизведены.'
        elif c == 'A02.1.07.012':
            d.add('superior', curved_sheet([0, -.7, 0], .38, 1.7), label='Верхняя носовая раковина', p=[0, -.95, .3])
            d.add('supreme', curved_sheet([0, .4, 0], .3, 1.4), 'variant', 'Наивысшая носовая раковина · выше', [0, 1.05, .3])
        elif c == 'A02.1.15.013':
            d.add('body', block([0, -.1, 0], [2.9, 1.2, .35]), label='Язычная поверхность тела · область премоляров', p=[0, -1, .2])
            d.add('torus', ellipsoid([0, 0, .22], [.85, .32, .42]), 'variant', 'Нижнечелюстной валик', [0, .75, .5])
        elif c == 'A02.1.06.008':
            d.add('posterior', line([[-1.05, -.9, 0], [-1.05, .9, 0]], .09), 'context', 'Задний край сосцевидной области', [-1, 1.25, 0])
            d.add('foramen', ring([-.4, 0, 0], .2), 'variant', 'Пример положения сосцевидного отверстия', [.35, -.65, 0])
        elif c == 'A02.1.12.032':
            d.add('incisive', ellipsoid([-1, .15, 0], [.45, .5, .18]), 'context', 'Резцовая область', [-1.2, -.7, 0])
            d.add('interval', ellipsoid([1, -.15, 0], [.2]*3), 'secondary', 'Промежуток: боковой резец — клык', [1.1, -.7, 0])
            d.add('suture', line([[-.6, .15, .12], [-.2, .02, .12], [.3, -.05, .12], [.8, -.15, .12]], .045),
                  'variant', 'Резцовый шов', [0, .65, .1])

    d = diagram('cranial-tables', ['A02.1.00.034', 'A02.1.00.035', 'A02.1.00.037'], 'relations', 'Пластинки свода и диплоэ')
    d.add('outer', block([0, .75, 0], [2.7, .18, 1.5]), label='Наружная пластинка', p=[1.7, .85, .25])
    d.add('inner', block([0, -.75, 0], [2.7, .18, 1.5]), 'secondary', 'Внутренняя пластинка', [1.7, -.85, .25])
    lattice = []
    for x in [-1, -.5, 0, .5, 1]:
        for z in [-.5, 0, .5]:
            lattice += [line([[x, -.55, z], [x+.1, .05, z+.08], [x, .55, z]], .038)]
    for y in [-.3, .3]:
        for z in [-.5, 0, .5]:
            lattice += [line([[-1, y, z], [1, y, z]], .038)]
    d.add('diploe', trimesh.util.concatenate(lattice), 'feature', 'Диплоэ · условная сеть', [-1.8, 0, .25])
    d.data['modelLimit'] += ' Расстояния между пластинками и регулярная сеть условные. Реальные трабекулы, их ориентация, пористость и каналы не восстановлены.'

    d = diagram('sutural-bone', ['A02.1.00.043'], 'variants')
    d.add('bone-a', block([-.85, 0, -.05], [1, 1.5, .25]), label='Одна кость', p=[-1, -.95, 0])
    d.add('bone-b', block([.85, 0, -.05], [1, 1.5, .25]), label='Соседняя кость', p=[1, -.95, 0])
    d.add('accessory', ellipsoid([0, 0, 0], [.22, .36, .2]), 'variant', 'Кость шва', [0, .95, 0])
    d = diagram('palatine-torus', ['A02.1.00.063'], 'variants')
    d.add('palate', block([0, 0, 0], [2.8, .25, 1.8]), label='Костное нёбо · условный участок', p=[0, -.65, .6])
    d.add('torus', ellipsoid([0, .15, 0], [.35, .35, .72]), 'variant', 'Нёбный валик · средняя линия', [0, .85, .25])

    model_map = defaultdict(list)
    for m in models:
        for c in m['codes']:
            model_map[c].append(m['id'])
    records = []
    for r in extent['rows']:
        e = evidence[r['c']]
        model_ids = model_map[r['c']]
        complete = r['status'] == 'complete'
        missing = list(dict.fromkeys(a['confirmedExtent'] for a in r['assessments'] if a['status'] != 'complete'))
        unknown = ('Выполнен критерий макроформы: '+r['criterion']+' Микродетали и независимая экспертная приёмка этим не подтверждены.'
                   if complete else 'Полностью не подтверждён критерий: '+r['criterion']+' '+ ' '.join(missing))
        status = 'source_model' if complete else 'educational_reconstruction' if model_ids else 'explanation'
        records.append(dict(id=r['id'], kind='variant' if r['localization']=='variant' else 'bone',
                            bone=r['bone'], boneRu=r['boneRu'], c=r['c'], ru=r['ru'], lat=r['lat'],
                            status=status, originalLocalization=r['localization'], originalExtentStatus=r['status'],
                            originalCompleteFeatureGeometry=r['completeFeatureGeometry'],
                            known=e['x'] + (' '+e['note'] if e.get('note') else ''), unknown=unknown,
                            modelLimit=DISCLAIMER if model_ids else
                                ('На исходной модели проверена указанная макроформа; это не заявление о микрогеометрии.' if complete else
                                 'Показанный маркер и общий вид не восполняют отсутствующий рельеф. Форма не дорисована, поскольку имеющиеся сведения не задают её достаточно точно.'),
                            learningGuidance=('Сопоставьте схему с исходным образцом и источниками; запомните только подписанную связь или расположение.' if model_ids else
                                              'Откройте доступный ракурс и сопоставьте видимую форму с описанием и критерием проверки.' if complete else
                                              'Изучите подтверждённое описание и доступный ракурс. Не используйте условную позицию маркера для определения точных границ, диаметра или хода.'),
                            refs=r['refs'], modelIds=model_ids, sourceViews=r['assessments'], pinId=r['pinId'],
                            disposition='represented' if complete else 'schematic_support' if model_ids else 'explicit_limitation',
                            quizEligible=complete, independentExpertValidation=False))
    for r in whole:
        status = r['geometry']['status']
        m = model_map[r['c']]
        module_ru = {'developmental_anatomy': 'развитие и возрастная анатомия',
                     'joints_connective_tissues': 'соединительная ткань и соединения костей',
                     'skull_osteology': 'кости черепа'}[r['ownerModule']]
        records.append(dict(id='whole:'+r['c'], kind='whole', c=r['c'], ru=r['ru'], lat=r['lat'],
                            status='future_scope' if not r['current'] else 'educational_reconstruction' if m else
                                   'source_model' if status in ('verified_view','verified_composition') else 'explanation',
                            originalExtentStatus=status, originalCompleteFeatureGeometry=r['geometry']['completeFeatureGeometry'],
                            known=r['description'], unknown=r['geometry']['modelNote'],
                            modelLimit=DISCLAIMER if m else r['geometry']['modelNote'],
                            learningGuidance=('Сравните обозначенные отношения в самостоятельной схеме с описанием TA98.' if m else
                                              'Этот термин относится к будущему модулю «'+module_ru+'». Название сохранено в общем перечне.' if not r['current'] else
                                              'Используйте выбранный ракурс как обзор области; проверку отдельных образований смотрите в карточках соответствующих костей.'),
                            refs=r['refs'], modelIds=m, sourceViews=[], sourceLaunch=r.get('launch'),
                            disposition='future_module' if not r['current'] else 'schematic_support' if m else
                                        'represented' if status in ('verified_view','verified_composition') else 'explicit_limitation',
                            quizEligible=False, independentExpertValidation=False))
    assert len(records)==618 and len({r['id'] for r in records})==618
    assert Counter(r.get('originalLocalization') for r in records if r['kind']!='whole') == dict(surface=325,projection=182,variant=14)
    assert len({v['c'] for v in variants})==12
    for r in records:
        assert all(r.get(k) for k in ['known','unknown','modelLimit','learningGuidance','refs']),r['id']
        assert len({x['url'] for x in r['refs']})>=2 and all(x.get('locator') for x in r['refs']),r['id']
    for m in models:
        assert len({r['url'] for r in m['refs']})>=2 and m['nodeNames'] and m['labels'],m['id']
    asset = ROOT/'site/skull-educational-bones.glb'
    asset.write_bytes(scene.export(file_type='glb'))
    exported = trimesh.load(asset, force='scene')
    expected_nodes={n for m in models for n in m['nodeNames']}
    assert expected_nodes==set(exported.graph.nodes_geometry)
    for mesh in exported.geometry.values():
        assert np.isfinite(mesh.vertices).all() and len(mesh.faces)>0
    counts=dict(records=len(records), boneRecords=521, wholeRecords=97, wholeCurrent=89, wholeFuture=8,
                projections=182, variantPlaces=14, variantTypes=12, diagrams=len(models),
                diagramNodes=len(expected_nodes), status=dict(Counter(r['status'] for r in records)),
                disposition=dict(Counter(r['disposition'] for r in records)),
                originalExtent=dict(Counter(r['originalExtentStatus'] for r in records if r['kind']!='whole')))
    result=dict(version=1, kind='bones', title='Образования черепа: схемы и ограничения',
                modelFile=asset.name, coordinateSystem='independent_dimensionless_diagrams',
                originalGeometryChanged=False, completeSkullGeometry=False, expertValidated=False,
                license=LICENSE, notice=DISCLAIMER, records=records, models=models, counts=counts)
    (ROOT/'site/skull-educational-bones.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report=dict(version=1,counts=counts,originalGeometryChanged=False,completeSkullGeometry=False,
                provenance='Original algorithmic diagrams using existing two-source anatomical descriptions; no third-party mesh or image copying.',
                asset=dict(file=str(asset.relative_to(ROOT)),sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),bytes=asset.stat().st_size),
                inputHashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in
                             ['site/skull-geometry-review.json','research/head-evidence.json','site/skull-whole.json','site/skull-study-variants.json','site/skull-variant-examples.json']},
                tests=dict(uniqueRecords=True,allRequiredFields=True,minimumTwoSourceURLsWithLocators=True,
                           originalLocalizationPreserved=True,allVariantTypesRepresented=True,
                           nodesMatchMetadata=True,finiteVertices=True),
                visualReview='Pending independent browser render inspection; scientific expert review not performed.',
                reviewedNewSource=dict(url='https://semmelweis.hu/anatomia/files/2014/04/Connections-of-the-Skull.pdf',
                                       locator='pp.2, 3, 5, 6, 8: canal connections, compared with existing independent sources; accessed 2026-10-13'))
    visual_path=ROOT/'research/skull-educational-bones-visual-review.json'
    if visual_path.exists():
        visual=json.loads(visual_path.read_text(encoding='utf8'))
        current_metadata=hashlib.sha256((ROOT/'site/skull-educational-bones.json').read_bytes()).hexdigest()
        if visual['assetSha256']==report['asset']['sha256'] and visual['metadataSha256']==current_metadata:
            report['visualReview']=visual
    (ROOT/'research/skull-educational-bones-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(counts,ensure_ascii=False)); print('Asset:',asset.stat().st_size,'bytes')


if __name__=='__main__':
    build()

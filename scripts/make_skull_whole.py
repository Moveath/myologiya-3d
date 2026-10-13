"""Build the complete 97-row TA98 skull-as-whole teaching catalogue.

The source-model views are an assessed presentation of the existing geometry;
they do not turn a contextual view into verified full feature geometry.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

from skull_whole_terms import TERMS, REFS, FUTURE, VIEWS, VARIANTS, GROUPS, NOTES, KOLESNIKOV_URL

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/skull-whole-scope-audit.json'
OUTPUT = ROOT / 'site/skull-whole.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(name):
    return [name + '_left', name + '_right']


def main():
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    source_rows = sorted(audit['rows'], key=lambda row: row['code'])
    assert len(source_rows) == 97
    assert [r['code'] for r in source_rows] == [f'A02.1.00.{n:03}' for n in range(1, 98)]
    cached_inventory = ROOT / audit['source_cache']
    # Research caches are intentionally not published. The reviewed inventory is
    # committed; when its source cache is available, also verify the frozen hash.
    if cached_inventory.exists():
        assert sha(cached_inventory) == audit['source_cache_sha256']
    z = json.loads((ROOT / 'site/skull-z-detail.json').read_text(encoding='utf-8'))
    review = json.loads((ROOT / 'research/skull-whole-model-review.json').read_text(encoding='utf-8'))
    assert review['modelSha256'] == sha(ROOT / review['model']), 'Geometry changed: repeat anatomical view review'
    all_bones = [b['id'] for b in z['bones']]
    assert len(all_bones) == len(set(all_bones)) == 22
    brain = ['frontal', 'occipital', 'sphenoid', 'ethmoid'] + pair('temporal') + pair('parietal')
    face = ['vomer', 'mandible'] + sum((pair(n) for n in ['maxilla', 'zygomatic', 'palatine', 'nasal', 'lacrimal', 'inferior_concha']), [])
    assert set(brain).isdisjoint(face) and set(brain + face) == set(all_bones)
    base = ['frontal', 'occipital', 'sphenoid', 'ethmoid'] + pair('temporal')
    palate = pair('maxilla') + pair('palatine')
    orbit = ['frontal', 'sphenoid', 'ethmoid'] + pair('maxilla') + pair('zygomatic') + pair('lacrimal') + pair('palatine')
    nose = ['ethmoid', 'vomer'] + pair('inferior_concha') + pair('palatine')
    no_mandible = [b for b in all_bones if b != 'mandible']
    view_directions = {
        'ant': ([0, 0, 1], [0, 1, 0]), 'sup': ([0, 1, .001], [0, 0, -1]),
        'post': ([0, 0, -1], [0, 1, 0]), 'right': ([-1, 0, 0], [0, 1, 0]),
        'inf': ([0, -1, .001], [0, 0, 1]),
    }
    observations = {
        'ant': 'Видны обе глазницы и передняя носовая апертура; лоб сверху, нижняя челюсть снизу.',
        'sup': 'Вид свода снаружи: сагиттальная граница между теменными костями; спереди венечная, сзади ламбдовидная. Передний отдел внизу изображения.',
        'post': 'В центре затылочная кость, над ней ламбдовидная граница и теменные кости; лицевые поверхности обращены от наблюдателя.',
        'right': 'Видна наружная поверхность правой височной области, скуловая дуга и правая ветвь нижней челюсти; передний отдел справа на изображении. Сторона проверена по именованным правым узлам и знаку их bounds.x.',
        'inf': 'При скрытой нижней челюсти видны костное нёбо, задние носовые отверстия и основание вокруг большого отверстия. Передний отдел вверху изображения.',
    }
    for name, direction in view_directions.items():
        result = next(r for r in review['norms'] if r['view'] == name)
        expected_parts = no_mandible if name == 'inf' else all_bones
        assert result['parts'] == expected_parts and result['d'] == direction[0] and result['up'] == direction[1]
    # A serrated midline boundary can cross x=0; the side is checked by its centre.
    assert all(b['bounds'][0][0] + b['bounds'][1][0] < 0 for b in z['bones'] if b['id'].endswith('_right'))

    def launch(parts, view='antlat', region='whole', preset='all', cut=None):
        assert parts and set(parts).issubset(all_bones)
        value = dict(mode='z', region=region, preset=preset, parts=parts, view=view)
        if cut:
            value['cut'] = cut
        return value

    inside = lambda parts=base: launch(parts, 'sup', 'base', 'inside', dict(plane='axial', value=.59, reverse=True))
    launch_by_number = {
        1: launch(all_bones), 7: launch(brain, region='whole', preset='brain'),
        8: launch(face, region='whole', preset='face'), 12: inside(),
        13: launch(['frontal'], 'ant'), 14: launch(['occipital'], 'post'),
        15: launch(['frontal'] + pair('nasal'), 'ant'),
        16: launch(['frontal'] + pair('parietal'), 'sup'),
        17: launch(['occipital'] + pair('parietal'), 'post'),
        18: launch(['occipital'], 'post'),
        19: launch(brain, 'right'), 20: launch(['occipital'] + pair('parietal') + pair('temporal'), 'right'),
        21: launch(['mandible'], 'right'), 22: launch(all_bones, 'right'),
        23: launch(pair('temporal') + pair('zygomatic'), 'right'),
        24: launch(no_mandible, 'right'), 25: launch(['sphenoid'] + pair('maxilla') + pair('palatine'), 'right'),
        26: launch(['sphenoid'] + pair('maxilla'), 'right'),
        32: launch(brain, 'sup'), 33: launch(brain, 'sup'),
        38: launch(pair('parietal'), 'inf'), 39: launch(pair('parietal'), 'inf'),
        40: inside(), 41: inside(), 42: launch(pair('parietal'), 'inf'),
        44: launch(no_mandible, 'inf'), 45: inside(), 46: inside(),
        47: inside(), 48: inside(), 49: inside(), 50: inside(),
        51: inside(['occipital', 'sphenoid'] + pair('temporal')),
        52: inside(['occipital'] + pair('temporal')),
        53: launch(no_mandible, 'inf'),
        54: launch(['occipital'] + pair('temporal'), 'inf'),
        55: launch(['occipital', 'sphenoid'] + pair('temporal'), 'inf'),
    }
    for number, view in VIEWS.items():
        launch_by_number[number] = launch(no_mandible if number == 6 else all_bones, view)
    for number in range(56, 63):
        launch_by_number[number] = launch(palate, 'inf')
    for number in (64, 65, 66):
        launch_by_number[number] = launch(['sphenoid', 'vomer'] + pair('palatine'), 'inf')
    for number in range(67, 86):
        launch_by_number[number] = launch(orbit, 'ant', 'face', 'front')
    for number in range(86, 98):
        launch_by_number[number] = launch(nose, 'antlat', 'face', 'nose')
    launch_by_number[88] = launch(['frontal'] + pair('maxilla') + pair('nasal'), 'ant')
    launch_by_number[96] = launch(['sphenoid', 'vomer'] + palate, 'post')
    rows = []
    for number, original in enumerate(source_rows, 1):
        current = number not in FUTURE
        owner = 'skull_osteology' if current else ('joints_connective_tissues' if number == 11 else 'developmental_anatomy')
        requirement = 'view' if number in VIEWS else 'variant' if number in VARIANTS else 'group' if number in GROUPS else 'landmark'
        target = launch_by_number.get(number)
        scope = 'context'
        status = 'context_view' if target else 'not_available'
        note = 'Показаны существующие кости Z-Anatomy и область изучения. Отдельный контур, вся поверхность или полный ход этого образования здесь не выделены и не подтверждены; обзор не заменяет проверку его геометрии.'
        if number in VIEWS:
            status, scope = 'verified_view', 'view_orientation'
            note = 'Проверены направление камеры и набор отображаемых костей. Это стандартный обзор исходной модели; он не подтверждает полноту мелкого рельефа, отверстий и каналов.'
            if number == 6:
                note += ' Нижняя челюсть скрыта, чтобы не перекрывать наружное основание и костное нёбо.'
        elif number in (1, 7, 8):
            status, scope = 'verified_composition', 'bone_group'
            note = 'Проверен состав группы существующих костных объектов Z-Anatomy. Слуховые косточки доступны в отдельном образце OpenEar; отсутствие их наложения на этот череп не означает отсутствия карточек. Мелкая геометрия каждой кости оценивается отдельно.'
        elif number in FUTURE:
            status, scope = 'future_module', 'not_modelled'
            note = 'Термин сохранён в полном списке TA98. По границам учебных модулей это отдельная будущая тема; костная модель взрослого не изображает данную структуру.'
        elif number in VARIANTS:
            status, scope = 'variant_not_verified', 'variant'
            note = 'Название и тип варианта подтверждены источниками. Отдельный образец с подтверждённой геометрией этого варианта пока не выбран; обычный череп не выдан за его демонстрацию.'
        elif number in (34, 35, 36, 37):
            scope = 'bone_microstructure'
            note = 'Наружная сетка Z-Anatomy не разделяет компактные пластинки, диплоэ и его каналы. Для этой карточки требуется отдельно проверенная КТ или костный срез; общий вид поверхности не выдан за их геометрию.'
        if number in range(57, 67) or number in (79, 80, 85, 92, 97):
            note += ' Костные стенки и непрерывность просвета этой структуры в данном обзоре не подтверждены.'
        if target and status == 'context_view':
            if number in (38, 39, 42):
                note += ' Выбран обзор внутренней стороны двух теменных костей; другие участки свода в этом виде скрыты.'
            elif target.get('cut'):
                note += ' Показано внутреннее основание на экранном срезе; срез скрывает верхнюю часть сетки, не является КТ и не открывает отсутствующую микрогеометрию.'
            elif 56 <= number <= 62:
                note += ' В кадре две верхние челюсти и две нёбные кости снизу; зубы не включены.'
            elif 64 <= number <= 66:
                note += ' В кадре клиновидная кость, сошник и нёбные кости снизу; показано их соседство, а не изолированный просвет канала.'
            elif 67 <= number <= 85:
                note += ' Фронтальный обзор включает кости обеих глазниц. Мелкая структура внутри глазницы может перекрываться её стенками; её отдельного маркера в этой карточке нет.'
            elif 86 <= number <= 97 and number not in (88, 96):
                note += ' Учебная группа показывает решётчатую кость, сошник, нижние носовые раковины и нёбные кости; остальные стенки скрыты для обзора. Отдельной сетки воздуха носового хода нет.'
        page = 9 if number <= 37 else 10 if number <= 83 else 11
        refs = REFS[number]
        assert len(refs) >= 2 and len({ref['authorGroup'] for ref in refs}) >= 2
        assert all(ref['url'].startswith('https://') and ref['locator'] for ref in refs)
        row = dict(
            id=f'skull-whole-{number:03}', c=original['code'], lat=original['latin'],
            **TERMS[number], ownerModule=owner, current=current, requirementType=requirement,
            refs=refs, nomenclatureRefs=[
                dict(title='IFAA: TA98, череп как целое', url=original['source_entry_url'], locator=original['code'], kind='nomenclature'),
                dict(title='Международная анатомическая терминология, под ред. Л. Л. Колесникова (2003)', url=KOLESNIKOV_URL + f'#page={page}', locator=f'Печатная с. {page}, строка {original["code"]}' + ('; повтор с. 17' if number == 61 else ''), kind='nomenclature'),
            ],
            geometry=dict(status=status, scope=scope, modelNote=note, completeFeatureGeometry=False),
            launch=target, presentInMainPins=original['present_in_current_pins'],
            mainPinInstances=original['current_pin_instances'],
        )
        if number in NOTES:
            row['note'] = NOTES[number]
        if number in VIEWS:
            row['geometry']['review'] = dict(
                screenshot=f'build_head/skull_whole/jobs/{VIEWS[number]}.png',
                observation=observations[VIEWS[number]], d=view_directions[VIEWS[number]][0], up=view_directions[VIEWS[number]][1],
            )
        rows.append(row)
        original.update(russian=row['ru'], russian_status='checked_kolesnikov_2003_printed_page',
                        russian_source_page=page, scope_status='assigned_module', owner_module=owner,
                        current_module=current, requirement_type=requirement, geometry_status=status)
    assert sum(r['current'] for r in rows) == 89
    assert sum(not r['current'] for r in rows) == 8
    assert not any(r['geometry']['completeFeatureGeometry'] for r in rows)
    output = dict(
        version=1, title='Череп как целое', total=97, current=89, future=8,
        description='Полный список TA98 A02.1.00.001–A02.1.00.097. Пять стандартных видов и состав костных групп проверены на исходной модели. Обзор области и подтверждение всей геометрии образования учитываются отдельно.',
        modelSource=dict(title=z['source'], file=z['file'], sha256=sha(ROOT / 'site' / z['file']),
                         coordinateFrame=z['coordinateFrame'], license=z['license']),
        sourceInventory=dict(url=audit['source_url'], cacheSha256=audit['source_cache_sha256']),
        counts=dict(requirementTypes=dict(Counter(r['requirementType'] for r in rows)), geometryStatuses=dict(Counter(r['geometry']['status'] for r in rows)), launchTargets=sum(bool(r['launch']) for r in rows)),
        rows=rows,
    )
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    audit['reconciliation'] = dict(total=97, current=89, future=8, generated_file='site/skull-whole.json',
                                   term_source='scripts/skull_whole_terms.py', description_sources_per_row=2,
                                   no_unverified_geometry_promotions=True)
    audit['russian_policy'] = 'Все 97 названий визуально сверены с Колесниковым, 2003, печатные с. 9–11; е/ё нормализовано. Расхождение числа A02.1.00.061 отмечено отдельно.'
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(output=str(OUTPUT), **output['counts'], total=97, current=89, future=8), ensure_ascii=False))


if __name__ == '__main__':
    main()

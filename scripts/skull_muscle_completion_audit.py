"""Record this source-file review without changing the atlas completion flags.

Run after skull_muscle_completion_artisynth.py. Cached human donor data and
the unaccepted FE preview remain local; no new surface is accepted by this audit.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from new_muscle_source_audit import inventory

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/new-muscles'
OUT = ROOT / 'build_head/muscle_completion'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def artifact(path):
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
            'sha256': digest}


def main():
    whole, parts = inventory()
    assert len(whole) == 9 and len(parts) == 10, 'Re-review changed inventory'
    arti = read(OUT / 'artisynth-review.json')
    assert arti['missing_atlas_records_closed'] == 0 and not arti['published']
    z = read(OUT / 'z-target-inventory.json')
    relevant = [x for x in z if any(k in x['name'].lower() for k in
                ['auricular muscles', 'supercilii', 'nasalis muscle',
                 'orbicularis oris', 'part of orbicularis'])]
    for x in relevant:
        x.pop('properties', None)  # Blender runtime addresses have no evidential value.
    vap = []
    for uid in ['22dbb37977304b5aab9db083b51026d2', 'e454a6e1c3f14982b0597f34a236dc85']:
        j = read(CACHE / (uid + '.json'))
        vap.append({'uid': uid, 'name': j['name'], 'url': j['viewerUrl'],
                    'license': j['license'], 'downloadable': j['isDownloadable'],
                    'official_download_status_2026_10_13': 401,
                    'mesh_obtained': False, 'metadata': artifact(CACHE / (uid + '.json'))})
    candidates = [
        {'id': 'z_anatomy', 'license': 'CC BY-SA 4.0',
         'source': 'research/cache/Z-Anatomy/Startup.blend',
         'objects': relevant, 'evidence': artifact(OUT / 'z-target-inventory.json'),
         'method': 'Исходный .blend открыт через bpy с use_scripts=False; проверены имена, типы объектов, число вершин и коллекции.',
         'decision': 'target_surfaces_not_identified',
         'finding': 'Ушные названия — FONT и линии MESH из двух вершин. Отдельных целевых ушных мышц, depressor supercilii и transversus menti не найдено в проверенной именованной сцене. Nasalis и orbicularis oris представлены целыми правой/левой поверхностями; суффиксы .ol/.or относятся к коллекции Muscular insertions. У orbicularis oculi отдельно выделены только orbital/palpebral. Не выдавать эти объекты за отсутствующие части.'},
        {'id': 'bodyparts43', 'license': 'CC BY-SA 2.1 Japan (данные), MIT (код зеркала)',
         'url': 'https://github.com/olivercase/body_parts_3d_api',
         'evidence': [artifact(ROOT / 'research/cache/bp43' / n) for n in ['MANIFEST.csv', 'FMA2Obj.txt', 'obj2FMA.html']],
         'decision': 'target_object_mapping_not_identified',
         'finding': 'Проверены манифест и опубликованное соответствие FMA→OBJ версии 4.3. Новые целевые поверхности не идентифицированы по доступному перечню. Это проверка перечня, а не визуальный осмотр каждой сетки 4.3 и не доказательство отсутствия анатомического образования вообще.'},
        {'id': 'visible_ape', 'author': 'José Saúl Martín / Visible Ape Project',
         'url': 'https://www.visibleapeproject.com/3d-human-head-and-neck',
         'locator': 'Labeled human reconstruction, muscle 5 Depressor supercilii; Download this model links',
         'files': vap, 'decision': 'authorized_source_download_requires_authentication',
         'finding': 'Авторская человеческая реконструкция с лицензией CC BY 4.0 — конкретный кандидат для depressor supercilii. Оба официальных download API вернули 401. В проверенных страницах проекта, авторской статье и поиске репозитория Aveiro другой разрешённый исходный файл не найден. Отдельность объектов и обе стороны пока не проверены. Закрытые ресурсы просмотрщика не извлекались.'},
        {'id': 'artisynth', 'decision': 'not_confirmed_ta98_parts',
         'evidence': artifact(OUT / 'artisynth-review.json'),
         'model': artifact(OUT / 'artisynth-authored-elements.glb'),
         'license': arti['license'], 'source_commit': arti['source_commit'],
         'anatomical_references': arti['anatomical_references'],
         'shared_OOM_OOP_solid_elements': len(arti['shared_solid_element_ids']),
         'objects': [{k: x[k] for k in ['id', 'vertices', 'triangles', 'watertight',
                      'winding_consistent', 'max_difference_from_same_reference_node_mm']}
                     for x in arti['objects']],
         'finding': arti['finding'], 'published': False,
         'review_image_files': [artifact(OUT / n) for n in arti['visual_review']['images']],
         'visual_review': arti['visual_review'],
         'restriction': 'Техническая модель сохранена для проверки источника. Не заменяет две отсутствующие TA98-части orbicularis oris и не добавляется в публичный атлас.'},
        {'id': 'jena_3d_face', 'license': 'CC BY 4.0',
         'url': 'https://doi.org/10.6084/m9.figshare.32324658',
         'paper': 'https://doi.org/10.3390/jimaging12090459',
         'locator': 'Methods 2.4 Segmentation; dataset donor 01, MRI mask_*.nii.gz',
         'evidence': artifact(CACHE / '01.zip'), 'decision': 'group_masks_do_not_define_target_parts',
         'finding': 'Реальный архив 01.zip получен; проверены маски AR, HS, KJ, sub, X3, XX и их метки. Авторы сегментировали общие мышечные пласты/группы, намеренно не проводили границы каждой лицевой мышцы. Доступная ресэмплированная сетка маски около 0,318×0,318×0,320 мм не означает такую исходную разрешающую способность МРТ (0,640 мм).',
         'mask_XX_values_and_voxel_counts': {'0': 309643693, '2': 2850016, '3': 4700531},
         'mask_KJ_values_and_voxel_counts': {'0': 309731686, '1': 7462554},
         'accepted_individual_muscle_labels': []},
        {'id': 'hudeca', 'license': 'Данные CC BY-NC 4.0; статья CC BY-NC-ND 4.0',
         'url': 'https://hudeca.com/?page_id=590',
         'paper': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10783631/',
         'locator': 'A tridimensional atlas of the developing human head, Fig.S5K–M; author repository VR and raw imaging pages',
         'decision': 'excluded_noncommercial_license',
         'finding': 'В эмбриональном исследовании различимы наружные ушные мышцы. Авторские download-ссылки ведут к объёмам syGlass/исходным изображениям, а не проверенному комплекту отдельных целевых поверхностей. Пользователь не разрешил NC; данные не включены в сайт.',
         'downloaded_target_meshes': 0},
        {'id': 'li_toronto_2015', 'url': 'https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/OTU/TC-OTU-69552.pdf',
         'locator': 'Table 5.1, печатная стр.54; title-page copyright',
         'decision': 'underlying_source_and_redistribution_license_not_obtained',
         'finding': 'Работа действительно описывает измеренную 3D-архитектуру transversus menti и правой auricularis. Диссертация не предоставляет открыто лицензированных исходных геометрий. Число волокон и иллюстрации не заменяют координаты.'},
        {'id': 'lacrimal_pump_2020', 'url': 'https://doi.org/10.1016/j.jtos.2020.07.013',
         'institution': 'https://cris.fau.de/publications/241742781/',
         'locator': 'Methods: four serial-histology reconstructions by HiD; publisher/institutional record',
         'decision': 'source_geometry_and_open_license_not_obtained',
         'finding': 'Авторы выполнили реальные реконструкции слёзной части orbicularis oculi. В проверенных доступных материалах не найден свободно распространяемый исходный меш или маска для повторного экспорта; опубликованная иллюстрация не доказывает доступность 3D-данных.'},
        {'id': 'baseline_face_2023', 'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10294925/',
         'locator': 'Methods, muscle network; Data Availability Statement',
         'decision': 'action_lines_not_target_volumes_and_data_on_request',
         'finding': 'Мышечные сети — авторские линии действия между ориентирами статистической формы головы; не сегментированные объёмы целевых мышц. Данные указаны как доступные по запросу.'},
        {'id': 'anatomytool_artificial_head',
         'url': 'https://anatomytool.org/content/artificial-3d-head-mimic-muscles-and-facial-nerve',
         'license': 'CC BY-NC-SA 4.0', 'decision': 'excluded_noncommercial_license',
         'finding': 'Проверена актуальная карточка, лицензия несовместима с выбранным пользователем условием. Геометрия не включена.'}
    ]
    rows = []
    for record in whole + parts:
        row = dict(record)
        row['kind'] = 'part' if 'part' in row else 'whole'
        row['instance'] = row.get('id', row.get('muscle', '') + ':' + row.get('part', ''))
        row['accepted_source_geometry'] = False
        row['status'] = 'unresolved_source_geometry'
        if row['ta98'] == 'A04.1.03.019':
            row['candidate_ids'] = ['visible_ape', 'z_anatomy', 'bodyparts43', 'jena_3d_face']
            row['next_requirement'] = 'Разрешённый исходный download Visible Ape, затем проверка отдельного объекта и своей стороны.'
        elif row['ta98'] in ['A04.1.03.020', 'A04.1.03.021', 'A04.1.03.022']:
            row['candidate_ids'] = ['z_anatomy', 'bodyparts43', 'hudeca', 'li_toronto_2015']
            row['next_requirement'] = 'Отдельная человеческая поверхность/маска именно этой ушной мышцы и стороны с лицензией, разрешающей коммерческое распространение.'
        elif row['ta98'] == 'A04.1.03.027':
            row['candidate_ids'] = ['li_toronto_2015', 'z_anatomy', 'bodyparts43']
            row['next_requirement'] = 'Исходные координаты измеренной transversus menti и открытое разрешение на перераспространение.'
        elif row.get('muscle') == 'orbicularis_oris':
            row['candidate_ids'] = ['artisynth', 'z_anatomy', 'jena_3d_face']
            row['next_requirement'] = 'Источник с отдельно заданной полной частью TA98; OOM/OOP конечных элементов не заменяют подтверждение границы и номенклатуры.'
        elif row.get('part') == 'deep':
            row['candidate_ids'] = ['lacrimal_pump_2020', 'z_anatomy', 'jena_3d_face']
            row['next_requirement'] = 'Разрешённая геометрия глубокой части с подтверждением соответствия TA98, стороны и исходных границ.'
        else:
            row['candidate_ids'] = ['z_anatomy', 'bodyparts43', 'jena_3d_face', 'baseline_face_2023']
            row['next_requirement'] = 'Исходная отдельная часть со своими границами; нельзя разделить имеющуюся целую мышцу произвольным срезом.'
        rows.append(row)
    report = {'date': '2026-10-13', 'scope': 'Повторная проверка реальных источников 9 целых экземпляров мышц и 10 экземпляров частей.',
              'commercially_compatible_sources_required': True,
              'speculative_reconstruction_allowed': False,
              'counts': {'whole_instances': len(whole), 'part_instances': len(parts),
                         'accepted_new_instances': 0, 'unresolved_instances': len(rows)},
              'complete_muscle_geometry_claim': False,
              'local_review_glb_not_a_published_anatomical_completion': 'build_head/muscle_completion/artisynth-authored-elements.glb',
              'general_limitation': 'Не найден в проверенном наборе источников не означает, что такой модели нигде не существует. Анатомическая статья и 3D-рисунок не заменяют полученный проверенный исходный файл.',
              'instances': rows, 'candidates': candidates}
    assert len({x['instance'] for x in rows}) == 19
    target = ROOT / 'research/muscle-completion-review.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['counts']))


if __name__ == '__main__':
    main()

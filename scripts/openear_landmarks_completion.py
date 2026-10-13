"""Reproducible review inputs for five additional native OpenEar landmarks.

The mesh is never edited. Screen rays only pick already visually identified
surfaces; neither a ray hit nor closeness to an adjacent ossicle proves a name.
Run --jobs while the native review driver is running, then --collect.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/openear_landmarks_completion'

FEATURES = {
    'stapes_anterior_limb': {
        'b': 'stapes', 'c': 'A15.3.02.035', 'ru': 'Передняя ножка стремени',
        'lat': 'crus anterius',
        'x': 'Передняя из двух ножек, соединяющих область головки с основанием стремени.',
        'v': {'d': [0, 0, 1], 'up': [0, 1, 0]}, 'uv': [.303, .43],
        'observed': 'Отдельная непрерывная ножка по передней стороне межножкового отверстия; менее изогнута, чем противоположная. Имя проверено по форме и исходному положению наковальни и улитки: сторона задней короткой ножки наковальни противоположна. Оси сканера не приняты за анатомические оси.',
        'modelNote': 'Отмечена поверхность различимой передней ножки исходной модели стремени OpenEar ZETA. Модель сохраняет собственную форму этого препарата; точка не делит всю косточку на отдельные сегменты.',
        'images': ['09-stapes-z.png', '10-stapes-nz.png', '24-stapes-pins-context.png'],
    },
    'stapes_posterior_limb': {
        'b': 'stapes', 'c': 'A15.3.02.036', 'ru': 'Задняя ножка стремени',
        'lat': 'crus posterius',
        'x': 'Задняя из двух ножек, соединяющих область головки с основанием стремени.',
        'v': {'d': [0, 0, 1], 'up': [0, 1, 0]}, 'uv': [.779, .492],
        'observed': 'Дугообразная непрерывная ножка на противоположной стороне межножкового отверстия. Заднее направление проверено в исходном взаимном положении косточек по короткой ножке наковальни; противоположная ножка менее изогнута.',
        'modelNote': 'Отмечена поверхность различимой задней ножки исходной модели стремени OpenEar ZETA. Это ориентир на авторской костной поверхности, не реконструкция недостающей ткани.',
        'images': ['09-stapes-z.png', '10-stapes-nz.png', '24-stapes-pins-context.png'],
    },
    'malleus_lateral_process': {
        'b': 'malleus', 'c': 'A15.3.02.047', 'ru': 'Латеральный отросток молоточка',
        'lat': 'processus lateralis',
        'x': 'Выступ у основания рукоятки молоточка, направленный к барабанной перепонке.',
        'v': {'d': [1, 0, 0], 'up': [0, 0, -1]}, 'uv': [.64, .605],
        'observed': 'Конический выступ непосредственно у начала рукоятки. Видим с противоположных сторон и в косых видах. Направление к верхнему участку барабанной перепонки проверено в исходной взаимной позе её авторской сегментации и молоточка.',
        'modelNote': 'Отмечен реально выступающий участок у корня рукоятки исходного молоточка. Связки и складки барабанной перепонки этим маркером не сегментированы.',
        'images': ['21-malleus-pins-x.png', '22-malleus-pins-oblique.png', '23-malleus-pins-context.png', '19-malleus-oblique2.png'],
    },
    'malleus_anterior_process': {
        'b': 'malleus', 'c': 'A15.3.02.048', 'ru': 'Передний отросток молоточка',
        'lat': 'processus anterior',
        'x': 'Передний выступ, отходящий от области шейки молоточка.',
        'v': {'d': [1, 1, -1], 'up': [0, 0, -1]}, 'uv': [.445, .465],
        'observed': 'Небольшой самостоятельный выступ на передней стороне шейки, выше латерального отростка. Он видим в двух разнесённых косых видах и со стороны +X препарата. Его переднее положение сопоставлено с задней короткой ножкой наковальни и улиткой, а не выведено из знака координаты.',
        'modelNote': 'В исходной модели различим короткий выступ переднего отростка. Тонкое длинное продолжение, изображаемое в некоторых анатомических рисунках, на этой сетке не подтверждено и не достроено. Маркер относится только к видимому выступу.',
        'images': ['21-malleus-pins-x.png', '22-malleus-pins-oblique.png', '30-malleus-neck.png', '31-malleus-anteriorcontext.png'],
    },
    'incus_lenticular_process': {
        'b': 'incus', 'c': 'A15.3.02.041', 'ru': 'Чечевицеобразный отросток наковальни',
        'lat': 'processus lenticularis',
        'x': 'Терминальная часть длинной ножки наковальни со стороны сочленения с головкой стремени.',
        'v': {'d': [1, 0, 0], 'up': [0, 0, -1]}, 'uv': [.19, .923],
        'observed': 'Отмечено дистальное закруглённое расширение на изгибе длинной ножки. В изолированной наковальне просмотрены четыре стороны и два увеличенных косых вида; в исходном суставном положении эта область обращена к головке стремени. Тонкая соединительная ножка и край отдельной пластинки на сглаженной авторской сетке не разделяются.',
        'modelNote': 'Отмечен видимый терминальный участок чечевицеобразного отростка в авторской модели наковальни. Тонкая ножка и граница пластинки здесь сглажены и не представлены отдельной подтверждённой микрогеометрией. Маркер не означает, что эти детали полностью восстановлены.',
        'images': ['25-incus-pins-x.png', '26-incus-pins-oblique.png', '27-incus-z.png', '28-incus-tip-medial.png', '29-incus-tip-lateral.png'],
    },
}

EXPECTED_CODES = {f'A15.3.02.{n:03d}' for n in (34, 35, 36, 37, 39, 40, 41, 42, 44, 45, 46, 47, 48)}


def refs(key):
    b = FEATURES[key]['b']
    gray, sobotta = {'malleus': (916, 793), 'incus': (917, 796), 'stapes': (918, 798)}[b]
    out = [{'title': 'Gray, Anatomy of the Human Body (1918)',
            'url': f'https://commons.wikimedia.org/wiki/File:Gray{gray}.png',
            'locator': f'Рис. {gray}: {FEATURES[key]["ru"]}; сопоставлены два вида косточки, если они присутствуют на рисунке.',
            'scope': 'anatomy'}]
    if b == 'incus':
        out.append({'title': 'Chien et al. (2009), Anatomy of the Distal Incus in Humans',
                    'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2774412/',
                    'locator': 'Results, Qualitative histological descriptions; Figs. 2–5: терминальная пластинка и соединительная ножка чечевицеобразного отростка, его связь с головкой стремени.',
                    'scope': 'anatomy'})
    else:
        out.append({'title': 'Sobotta, Atlas and Text-book of Human Anatomy (1909)',
                    'url': f'https://commons.wikimedia.org/wiki/File:Sobo_1909_{sobotta}.png',
                    'locator': f'Рис. {sobotta}: {FEATURES[key]["ru"]}; подпись соответствующего отростка или ножки.',
                    'scope': 'anatomy'})
    return out


def jobs():
    OUT.mkdir(parents=True, exist_ok=True)
    defs = [dict(id=k, **{p: v[p] for p in ('b', 'c', 'v', 'uv')}) for k, v in FEATURES.items()]
    js = '(()=>{const defs=' + json.dumps(defs) + ';window.__candidates=defs.map(row=>{const r=rayAt(row.b,row.v,...row.uv);const ray=new THREE.Raycaster(new THREE.Vector3(...r.o),new THREE.Vector3(...r.dir));const hit=ray.intersectObject(__meshes[row.b],false)[0];if(!hit)throw Error(row.id);return{...row,p:hit.point.toArray(),n:hit.face.normal.clone().transformDirection(__meshes[row.b].matrixWorld).toArray(),faceIndex:hit.faceIndex}});return __candidates})()'
    raycast_job = js
    (OUT / '40-final-picks.job').write_text(js, encoding='utf-8')
    for i, bone in enumerate(('malleus', 'incus', 'stapes'), 41):
        v = {'d': [1, 0, 0], 'up': [0, 0, -1]} if bone != 'stapes' else {'d': [0, 0, 1], 'up': [0, 1, 0]}
        js = f'show({json.dumps(bone)},{json.dumps(v)},"Проверенные новые ориентиры TA98");pins(__candidates.filter(p=>p.b==={json.dumps(bone)}).map(p=>({{p:p.p,t:p.c}})));true'
        (OUT / f'{i}-{bone}-final.job').write_text(js, encoding='utf-8')
    (OUT / 'review-inputs.json').write_text(json.dumps({
        'source_geometry': 'site/skull-openear.glb',
        'source_geometry_sha256': hashlib.sha256((ROOT / 'site/skull-openear.glb').read_bytes()).hexdigest(),
        'coordinate_frame': 'author RAS -> [-RASx,RASz,RASy], metres; native specimen, no inter-specimen registration',
        'features': FEATURES, 'raycast_job': raycast_job,
        'nomenclature_review': {'TA98': 'A15.3.02.034–048 excluding whole-ossicle entries .038 and .043; 13 subterms', 'Kolesnikov': '2003, printed page 196, visually checked the five additional Russian terms'},
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def collect():
    rows = json.loads((OUT / '40-final-picks.out').read_text(encoding='utf-8'))
    assert {r['id'] for r in rows} == set(FEATURES)
    for r in rows:
        assert len(r['p']) == len(r['n']) == 3 and not r.get('missing')
        spec = FEATURES[r['id']]
        assert (r['b'], r['c']) == (spec['b'], spec['c'])
        r['review'] = spec['observed']
        r['screenshots'] = ['build_head/openear_landmarks_completion/' + s for s in spec['images']]
    (OUT / 'picks.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Collected {len(rows)} exact native picks; no mesh modifications')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', action='store_true')
    parser.add_argument('--collect', action='store_true')
    args = parser.parse_args()
    if args.jobs: jobs()
    if args.collect: collect()

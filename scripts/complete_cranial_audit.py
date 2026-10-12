"""Publish the cranial completion review without changing any marker status."""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil
from head_localization import positions,descriptions
from head_cranial_evidence import GRAY,AS,TMA_F
from ta98 import T

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/complete_cranial'
QUEUE=ROOT/'qhead_complete_cranial'
fit=json.loads((OUT/'registration-fit.json').read_text())
anchors=json.loads((OUT/'manual-anchors.json').read_text())
facts=descriptions()
for row in anchors:
    code=row['code']
    row['ru']=T[code][1]
    row['lat']=T[code][0]
    row['method']='Ручной выбор лучом участка одноимённого крупного ориентира на двух отдельно осмотренных сетках; экранные координаты и нормали сохранены. Это проверка общей топографии, не определение точной морфометрической вершины.'
    row['refs']=facts[code]['refs'] if code in facts else [GRAY[row['bone']],AS[row['bone']]]

cavity_codes={'A02.1.03.029','A02.1.05.016','A02.1.07.008','A02.1.07.009','A02.1.07.010'}
pending=[]
for (bone,code),point in positions().items():
    if bone not in fit['fit_bones'] or point['localization']=='surface':continue
    row={'bone':bone,'code':code,'ru':T[code][1],'lat':T[code][0],
         'current_status':point['localization'],'modelNote':point['modelNote'],
         'refs':facts[code]['refs'],
         'status_after_review':point['localization']}
    row['result']= ('Доступна отдельная авторская поверхность полости Z-Anatomy. Приблизительное совмещение позволяет учебное сравнение, но не доказывает эту полость в основном образце.' if code in cavity_codes else
        'Вариант не обязан присутствовать в каждом черепе; наличие в данном образце не подтверждено.' if point['localization']=='variant' else
        'На осмотренных сетках нет надёжно различимого самостоятельного рельефа или просвета, позволяющего снять ограничение. Именованная линия Z-Anatomy не считается геометрией образования.')
    pending.append(row)

screen_names=[f'anchor_review_{source}_{bone}' for source in ['bp','z'] for bone in ['frontal','occipital','sphenoid']]
screen_names += [f'cavity_{bone}_{view}' for bone in ['frontal','sphenoid','ethmoid'] for view in ['ant','sup','lat','post']]
screen_names += ['bp43_ethmoid_sup','bp43_ethmoid_ant','bp43_ethmoid_lat','bp43_ethmoid_perpendicular_lat','bp_ethmoid_sup','bp_ethmoid_right_half_double','bp_ethmoid_left_half_double']
screens=ROOT/'shots/cranial-completion';screens.mkdir(parents=True,exist_ok=True)
for name in screen_names:
    shutil.copyfile(QUEUE/(name+'.png'),screens/(name+'.png'))

report={'review_date':'2026-10-12','scope':fit['fit_bones'],
    'summary':'Проверены источники мелкой геометрии, единое совмещение Z-Anatomy, восемь полостей и альтернативная решётчатая кость BodyParts3D 4.3. Ни один projection/variant автоматически не переименован в подтверждённый рельеф.',
    'pending_counts':dict(Counter(p['current_status'] for p in pending)),
    'source_inventory':{'file':'build_head/complete_cranial/z-object-inventory.json',
        'finding':'Имена зрительного, крыловидного, мыщелкового и подъязычного каналов, мелких отверстий и борозд представлены аннотационными объектами из двух вершин без граней. Дополнительные поверхности — только уже экспортированные восемь пазух/групп ячеек; скрытых сеток каналов не найдено.'},
    'registration':{'method':fit['method'],'transform_z_to_bp':fit['transform_z_to_bp'],
        'distances':fit['distances'],'anchors':anchors,
        'claim':'Приблизительное совмещение по крупной топографии. Оно не устанавливает тождество образцов и не подтверждает анатомию каждой мелкой структуры.'},
    'cavity_containment':json.loads((OUT/'cavity-containment.json').read_text()),
    'cavity_asset':{'file':'build_head/complete_cranial/head-cavities.glb','metadata':'build_head/complete_cranial/head-cavities.json',
        'status':'rejected_for_main_integration',
        'decision':'Не добавлять в основной BodyParts3D: пользователь выбрал только подтверждённую исходными моделями/сканами геометрию. Исходные полости сохраняются в независимом просмотрщике Z-Anatomy с их собственной геометрией и координатами.',
        'use':'Исследовательский результат оценки совмещения; не применять как основу для измерений, автоматического вычитания из основной кости или изменения статуса маркеров.'},
    'bp43':{'source':'https://github.com/olivercase/body_parts_3d_api',
        'files':[{'file':name,'sha256':hashlib.sha256((ROOT/'research/cache/bp43'/name).read_bytes()).hexdigest()} for name in ['FJ6309.obj','FJ6412.obj']],
        'observation':'FJ6309 содержит 22348 граней, отдельная перпендикулярная пластинка FJ6412 — 4856. Видны четыре гладких углубления верхних отделов лабиринта, но многочисленные решётчатые отверстия не разрешены. Медиальные образования не удаётся однозначно подтвердить ни в 3.0, ни в 4.3 после осмотра половин кости.',
        'registration':json.loads((OUT/'bp43-registration.json').read_text()),
        'decision':'Не заменять основную кость автоматически: иные пропорции и положение, остаточные расхождения до нескольких миллиметров; увеличение количества граней не равно полноте анатомии.'},
    'pending':pending,'screenshots':[f'shots/cranial-completion/{name}.png' for name in screen_names],
    'additional_source_review':[
        {'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6170943/','title':'Nowinski & Thaung (2018), A 3D stereotactic atlas of the adult human skull base',
         'result':'Статья описывает детально обработанные каналы и отверстия; её лицензия CC BY 4.0 относится к публикации. Отдельная совместимая лицензия на файлы атласа не подтверждена, геометрия не извлекалась.'},
        {'url':'https://3d.nih.gov/entries/3dpx-012260','title':'NIH 3D — Visible Human Male Skull',
         'result':'Найдена дополнительная модель целого черепа; покостная сегментация, совместимая лицензия конкретного файла и полнота мелких каналов не подтверждены. Не использована вместо основного набора.'}
    ]}
(ROOT/'research/cranial-completion-registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pending_counts':report['pending_counts'],'anchors':len(anchors),'screenshots':len(screen_names)},ensure_ascii=False))

"""Reproducible negative/limited variant review, not an anatomical completion."""
from temporal_variant_inspect import ROOT,OUT
import json,hashlib

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
variants=json.loads((ROOT/'site/skull-study-variants.json').read_text(encoding='utf-8'))
refs={p['c']:p['refs'] for p in variants}
ct=[]
for p in sorted(OUT.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    if 'frames' in d:
        image=p.with_suffix('.png');assert image.exists()
        ct.append({**ref(p),'image':ref(image),'frame_count':len(d['frames']),'bounds_mm':d['bounds_mm']})
views=[]
inputs=json.loads((OUT/'other-review-inputs.json').read_text(encoding='utf-8'))
for r in inputs['views']:
    p=ROOT/r['screenshot'];assert p.exists()
    views.append({**r,'sha256':sha(p)})
halleviews=[]
for folder,entries in {
 'jobs':{'01-internal':([0,1,0],[0,0,-1]),'02-lateral':([-1,0,0],[0,1,0])},
 'native-jobs':{'01-inside':([1,0,0],[0,1,0]),'02-outside':([-1,0,0],[0,1,0])},
 'high-jobs':{'01-inside':([-1,0,0],[0,1,0]),'02-outside':([1,0,0],[0,1,0])},
 'context-marked':{'01-marked':([0,1,0],[0,0,-1]),'02-oblique':([.2,1,.4],[0,0,-1])},
}.items():
    for name,(d,up) in entries.items():
        halleviews.append({**ref(OUT/folder/(name+'.png')),'d':d,'up':up})
xpct=json.loads((ROOT/'research/cache/temporal-variants/xpct-metadata.json').read_text(encoding='utf-8'))['data']['latestVersion']
assert xpct['license']['name']=='CC BY-NC 4.0'
report={
 'date':'2026-10-13',
 'scope':'Адресная проверка foramen mastoideum на полном Halle CT и уже полученных совместимых исходниках; дополнительные конкретные источники для .024/.035.',
 'new_confirmed_variant_meshes':0,'exported_anatomical_objects':0,'completeFeatureGeometry':False,
 'result':'Связь наружное устье → костный проход → устье в борозде сигмовидного синуса не подтверждена. Отрицательный результат этой проверки не доказывает отсутствия варианта у препарата и не означает невозможности дальнейшей сегментации.',
 'source':{'title':'Thomas Kirchner — A micro-CT of a human skull','url':'https://zenodo.org/records/6108435','license':'CC BY 4.0',
   'ct_file':'halle_skull.nrrd','ct_md5':'2b46ca394084ab84af20bc267114e75f','mask_file':'halle_skull_segmented.nrrd','mask_md5':'7ae22945a353069bdb695b63fa2f20bd',
   'both_complete_md5_rechecked':True,'native_spacing_mm':.125,'array_axes':'k,j,i','viewer_axes':'x=i, y=k, z=j; millimetres ×0.001',
   'anterior':'+viewer z, established by anatomy; header LPS not treated as independent evidence',
   'laterality':'Не присвоена: low-X/high-X — координатные стороны, не правая/левая анатомические стороны.',
   'lossless_roi_bounds_mm':[[0,35,30],[143.75,110,130]],
   'processing':'Исходные int16 CT и binary mask обрезаны без интерполяции. Контекстная сетка имеет шаг 0,25 мм; две локальные сетки — исходный шаг маски 0,125 мм. Marching cubes level 0.5, обращение winding, без сглаживания/достройки/закрытия отверстий.',
   'caches_not_for_publication':['mastoid-ct.npy','mastoid-mask.npy','context.glb','xlow-native.glb','xhigh-native.glb']},
 'candidates':[
  {'id':'halle_low_x_lumen','ta98_candidate':'A02.1.06.008','assigned_anatomical_name':None,'roi_bounds_mm':[[8,38,48],[36,65,85]],
   'context_marker_m':[.020,.050,.062],
   'observed':'На x17–20 мм различим округлый внутрикостный просвет с костной стенкой. В направлении x21–24 мм он сближается с извилистой щелью шва; на y49–54 мм округлый просвет виден отдельно от длинной щели.',
   'unconfirmed':'Не найден однозначный внутренний конец именно в sigmoid sulcus. Попадание ROI в топографически подходящую область недостаточно; часть CT-просвета не воспроизводится исходной бинарной маской.',
   'independent_review':'Cranial agent осмотрел dense-x/dense-y, mastoid-xlow-y и широкие виды с меткой: подтверждён реальный просвет, анатомическое имя не подтверждено.',
   'decision':'Не экспортировать под именем foramen mastoideum; не превращать сегмент просвета в полный канал.'},
  {'id':'halle_high_x_sutural_opening','ta98_candidate':'A02.1.06.008','assigned_anatomical_name':None,'roi_bounds_mm':[[112,37,57],[135,55,83]],
   'context_marker_m':[.122,.044,.071],
   'observed':'На y42–44 мм есть сообщение через толщу кости; в ортогональных z65–75 мм оно продолжается в разветвлённую щель шва.',
   'unconfirmed':'Именно эмиссарное отверстие не отделено от раскрытого шва; его собственный внутренний конец в sigmoid sulcus не установлен. Замкнутый трубчатый контур не требовался как обязательный признак, проверялась топография сообщения.',
   'independent_review':'Cranial agent независимо подтвердил сквозное сообщение и неоднозначность шов/эмиссарный ход; широкая привязка её не сняла.',
   'decision':'Не экспортировать под именем сосцевидного отверстия.'}
 ],
 'anatomical_identification_refs':[
  {'title':'Pekçevik et al. — Mastoid Emissary Vein Canal Incidence and Its Relationship with Jugular Bulb and Sigmoid Sulcus Anatomical Variations','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC8864204/',
   'locator':'Methods / Image Analysis, Figure 1: tracing the bony canal from the sigmoid sulcus extracranially; Fig.4 relationship to sigmoid sulcus.'},
  {'title':'Chaiyamoon et al. — Anatomical study of the mastoid foramina and mastoid emissary veins (2023)','url':'https://pubmed.ncbi.nlm.nih.gov/38110768/',
   'locator':'Abstract: 22 dry skulls / 44 sides, drilled courses, distinction of connecting/non-connecting foramina and exact entrance in the sigmoid groove.'}
 ],
 'ct_montages':ct,'ct_displayed_frames':sum(x['frame_count'] for x in ct),'halle_geometry_views':halleviews,
 'existing_additional_mesh_review':{
  'mesh':inputs['mesh'],'sha256':inputs['sha256'],'license_and_acquisition_record':'research/new-skull-source-audit.json',
  'views':views,'specimens':[
   {'node':'01_male-cranial_maxilla','source':'BoneHub Visible Human male','result_008':'В просмотренных наружных, нижнем и внутреннем видах не выделена пара устьев с прослеживаемым ходом; мелкая геометрия сглажена.',
    'result_035':'Самостоятельный околососцевидный выступ нижней стороны яремного отростка в этих видах не выделен.'},
   {'node':'02_female-cranial_maxilla','source':'BoneHub Visible Human female','result_008':'В просмотренных видах не подтверждён отдельный полный ход .008; сглаженная поверхность не даёт основания дорисовывать его.',
    'result_035':'Нижний и боковые виды не подтверждают отдельный удлинённый выступ в заявленном месте.'},
   {'node':'nih-002448','source':'NIH 3DPX-002448','result_008':'Внутри есть мелкие дефекты поверхности; их анатомические имена и связь с отдельным наружным отверстием не установлены.',
    'result_035':'Шейные позвонки и нижняя челюсть входят в состав общей сетки; отдельный paramastoid process из неё не идентифицирован.'}
  ],'limit':'Это адресная визуальная проверка указанных ракурсов, не доказательство анатомического отсутствия и не независимая проверка оригинальной CT-сегментации этих дополнительных сеток.'},
 'targeted_new_sources':[
  {'id':'gro_xpct_2025','title':'Schaeper et al. — 3D imaging of the human temporal bone by X-ray phase-contrast tomography',
   'article':'https://www.nature.com/articles/s44303-025-00086-y','dataset':'https://doi.org/10.25625/V3YSYD',
   'api':'https://data.goettingen-research-online.de/api/datasets/:persistentId/?persistentId=doi:10.25625/V3YSYD',
   'official_metadata_evidence':ref(ROOT/'research/cache/temporal-variants/xpct-metadata.json'),
   'article_license':'CC BY 4.0','actual_dataset_license':xpct['license'],'files':[{'id':f['dataFile']['id'],'name':f['dataFile']['filename'],'bytes':f['dataFile']['filesize']} for f in xpct['files']],
   'decision':'Отклонён для коммерчески совместимого набора: лицензия исходных объёмов CC BY-NC 4.0 отличается от лицензии статьи. Объёмы не скачивались и геометрия не извлекалась.'},
  {'id':'ini32_orbit','target':'A02.1.03.024','title':'INI-32 Orbit CT Atlas','url':'https://www.nitrc.org/projects/ini32_orbit_ct/',
   'paper':'https://pmc.ncbi.nlm.nih.gov/articles/PMC12720090/','declared_license':'CC Attribution',
   'decision':'Лицензия допускает коммерческое использование, но atlas — усреднение 32 пространственно нормализованных орбит, включая отражённые левые. Такой шаблон не подтверждает отдельную блоковую ость конкретного исходного человека; не использован для закрытия .024.'},
 ],
 'outcomes':[
  {'code':'A02.1.06.008','ru':'Сосцевидное отверстие','status':'not_demonstrated_as_named_complete_passage','new_geometry':False,'refs':refs['A02.1.06.008'],
   'remaining':'На исходных плотностях или другом разрешённом препарате однозначно связать внешнее устье с собственным костным ходом и устьем в борозде; проверить стенки на каждом участке, отдельно от шва и ячеек.'},
  {'code':'A02.1.03.024','ru':'Блоковая ость','status':'not_demonstrated_in_targeted_orbital_views','new_geometry':False,'refs':refs['A02.1.03.024'],
   'additional_independent_review':ref(ROOT/'research/cranial-orbital-variant-review.json'),
   'observed':'Cranial agent отдельно осмотрел 12 целевых глазничных ракурсов BoneHub male/female и NIH002448: обе глазницы, передний/нижнепередний и косые виды. Полные основание и верхушка отдельной spina trochlearis не подтверждены; сглаживание и разрывы сетки не приняты за ость.',
   'remaining':'Нужен индивидуальный CT/исходная сетка с реально различимой spina trochlearis, отдельно от trochlear fovea/других бугорков. Средний шаблон INI-32 не заменяет такой препарат; отрицательный осмотр сеток не доказывает отсутствия варианта у исходных людей.'},
  {'code':'A02.1.04.035','ru':'Околососцевидный отросток','status':'not_demonstrated_in_reviewed_native_views','new_geometry':False,'refs':refs['A02.1.04.035'],
   'remaining':'Нужен разрешённый исходный экземпляр с идентифицируемым processus paramastoideus; ни библиографический пример, ни обычный сосцевидный/яремный отросток не заменяет его геометрию.'}
 ],
 'publication_decision':'Публиковать можно отчёт и доказательные изображения с атрибуцией; отдельный анатомический объект .008 не создан. Большие ROI и диагностические GLB сохраняются локально. Главные 521 маркера и variant-флаги не менялись.',
 'script_files':['scripts/temporal_variant_inspect.py','scripts/temporal_variant_volume.py','scripts/temporal_variant_mesh.py','scripts/temporal_variant_other_jobs.py','scripts/temporal_variant_report.py'],
}
target=ROOT/'research/temporal-variant-geometry-review.json'
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'ct_frames':report['ct_displayed_frames'],'montages':len(ct),'halle_views':len(halleviews),'other_views':len(views),'new_geometry':0,'report_sha256':sha(target)})

"""Checkpoint 29 scoped decisions, preserving old IDs and untested methods.

No app/catalog/registry mutation. Source availability is separate from admission.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
rel=RUN.relative_to(ROOT).as_posix()
previous=json.loads((ROOT/'research/stage7-muscle-batch2-decisions-2026-10-21.json').read_text(encoding='utf8'))['rows']
plan={x['issue']:x for x in json.loads((ROOT/'research/stage7-reconstruction-method-plan-2026-10-22.json').read_text(encoding='utf8'))['rows']}
inventory=json.loads((RUN/'z-remaining-name-types.json').read_text(encoding='utf8'))['objects']

def method(status,description,evidence=None):
    return {'status':status,'description':description,'evidence':evidence or []}

def family(issue):
    for token in ['auricularis','depressor_supercilii','transversus_menti','sternalis',
                  'subcostales','intertransversarii','orbicularis_oculi','nasalis',
                  'orbicularis_oris','diaphragm','multifidus','rotatores']:
        if token in issue:return token
    raise ValueError(issue)

scope={
 'auricularis':{
  'observed':'В Z-Anatomy Extrinsic/Intrinsic auricular muscles — FONT либо двухвершинные подписи без граней; Auricular region — кожа, а не ушные мышцы.',
  'blocker':'Нет полученной индивидуальной мышцы; не зарегистрированы ушной хрящ, апоневротические/фасциальные и мышечные площадки нужного экземпляра.',
  'next':'Получить отдельную человеческую сегментацию либо разметить начало/прикрепление и оболочку тонкой мышечной пластинки на согласованной модели ушной области. Не заменять кожу ушной раковины мышцей.',
  'resource':['research/new-muscle-source-audit.json','research/muscle-completion-review.json']},
 'depressor_supercilii':{
  'observed':'В закреплённом Z-Anatomy есть текст определения, но отдельный целевой объект не найден. Corrugator/круговая мышца глаза не являются автоматическими заменами.',
  'blocker':'Кандидат Visible Ape Project именован автором, но разрешённый исходный файл ранее не получен; выделение структуры из общих лицевых сеток не подтверждено.',
  'next':'Получить авторский исходник VAP через разрешённую загрузку; проверить самостоятельный меш, сторону и топографию. Альтернатива — индивидуальная размеченная сегментация медиальной надглазничной области.',
  'resource':['https://www.visibleapeproject.com/3d-human-head-and-neck','https://api.sketchfab.com/v3/models/22dbb37977304b5aab9db083b51026d2','research/new-muscle-source-audit.json']},
 'transversus_menti':{
  'observed':'Самостоятельного transversus menti в закреплённом архиве не найдено; mentalis не принят за синоним.',
  'blocker':'Вариант требует документированного человеческого образца; диссертационный 3D-рисунок не даёт файл или лицензию геометрии.',
  'next':'Получить данные документированного варианта и права на конкретную геометрию/сегментацию. Не включать обязательную симметричную ленту по одному названию.',
  'resource':['research/new-muscle-source-audit.json']},
 'sternalis':{
  'observed':'Отдельного sternalis в закреплённом архиве не найдено.',
  'blocker':'Вариабельные форма, сторона и прикрепления; текущая модель не документирует этот вариант.',
  'next':'Получить аннотированный случай sternalis с формой, стороной и границами. Параметризация допустима только как явно индивидуальный пример с достаточными пространственными данными.',
  'resource':['research/stage7-muscle-batch2-decisions-2026-10-21.json']},
 'subcostales':{
  'observed':'Subcostal artery/vein в Z-Anatomy — сосудистые CURVE; целевых мышечных пучков нет.',
  'blocker':'Не определены реальные пучки, уровни рёбер, сторона и внутренние площадки прикрепления на текущем образце.',
  'next':'Получить лицензированные пучки/сегментацию или согласованную разметку внутренних рёберных прикреплений и подтверждённые поперечные формы. Не переносить границы из картинки без регистрации.',
  'resource':['research/stage7-muscle-batch2-decisions-2026-10-21.json']},
 'intertransversarii':{
  'observed':'Есть поясничные ventral/dorsal intertransversarii и общая подпись Intertransversarii; грудной отдельный меш отсутствует. Связка/поясничная мышца не заменяет грудную.',
  'blocker':'Нет индивидуально определённых грудных мышечных пучков с уровнями и формой.',
  'next':'Получить грудные пучки либо подтверждённую разметку их площадок и оболочек. Шейные и поясничные модели нельзя переименовать в грудные.',
  'resource':['research/stage7-muscle-batch2-decisions-2026-10-21.json']},
 'orbicularis_oculi':{
  'observed':'Есть Orbital/Palpebral part, но нет самостоятельных pars profunda/fasciculus ciliaris и их vertex groups. Поверхностная сетка не доказывает глубокий пучок.',
  'blocker':'Нет размеченной глубины и границ конкретного тонкого пучка; соседние части не являются его заменой.',
  'next':'Получить микроанатомическую сегментацию/геометрию века с обозначением глубокого и ресничного пучков, затем строить маску там, где общая сетка действительно содержит структуру.',
  'resource':['research/muscle-completion-review.json','research/stage7-muscle-batch2-decisions-2026-10-21.json']},
 'nasalis':{
  'observed':'Реальные Nasalis muscle.l/.r: 352 вершины/704 треугольника. Материалы Superficial 466/Tendon 238; это не альярная/поперечная сегментация. Vertex groups отсутствуют.',
  'blocker':'Не подтверждена линия раздела pars alaris и pars transversa в авторской или действующей геометрии.',
  'next':'Разметить анатомическую границу на зарегистрированной общей nasalis по доступным морфологическим/УЗ источникам; использовать маску, сохраняя непрерывную мышцу. Сухожилие не равно автоматически поперечной части.',
  'resource':['research/stage7-muscle-batch2-decisions-2026-10-21.json']},
 'orbicularis_oris':{
  'observed':'Реальные Orbicularis oris muscle.l/.r: 940 вершин/1880 треугольников. Все грани одного материала, vertex groups отсутствуют; двух целевых частей нет.',
  'blocker':'Нет подтверждённой глубины/границ pars marginalis и pars labialis на имеющейся поверхности.',
  'next':'Получить анатомическую поверхностно-глубинную разметку и убедиться, что общая сетка содержит обе части; маски предпочтительнее искусственного рассечения.',
  'resource':['research/muscle-completion-review.json']},
 'diaphragm':{
  'observed':'Есть Diaphragm: 4796 вершин/9592 треугольника; 8403 muscle/1189 Tendon. Есть авторские insertion patches, но нет готовых sternal/costal/lumbar masks или vertex groups.',
  'blocker':'Материал центрального сухожилия не определяет три мышечные территории прикреплений; не проверено соответствие авторских patches и текущей модели.',
  'next':'Проверить смысл и регистрацию авторских insertion patches Z-Anatomy на собственных костях и сухожильной границе; затем проследить подтверждённые территории по непрерывной сетке. Не делить по координатным плоскостям.',
  'resource':['research/thorax-muscle-evidence.json']},
 'multifidus':{
  'observed':'Есть отдельные авторские Multifidus thoracis muscle.r/.l: по 1987 вершин, 3902 треугольника, 21 связный пучок. Левая сторона уже зеркальная в исходнике (determinant < 0). Созданы два trial GLB с исправленным winding слева.',
  'blocker':'Ригидная регистрация по 12 позвонкам получена, но принятие места контакта каждого затронутого пучка не завершено. 12 внутрипучковых пар и межпучковые перекрытия не классифицированы как грубая анатомическая ошибка только по числу. Прямое соответствие границ текущему BP3D multifidus не установлено.',
  'next':'В сохранённой сцене сопоставить отмеченные контакты с анатомическими площадками задней дуги/отростков и уточнить, допустим ли отдельный учебный выбор авторской части. Для маски исходного BP3D нужен отдельный проверенный перенос/соответствие пучков; nearest-distance или осевой cut для маски недостаточны. Не заменять родителя. Если дефекты фасеток требуют ремонта, исправлять только производную с сохранением основной оболочки и повторной проверкой.',
  'resource':[rel+'/z-multifidus-registration.json',rel+'/z-multifidus-contact-classification-summary.json',rel+'/z-multifidus-fold-measurements.json','build_stage7/z_multifidus_trials_v1/provenance.json']},
 'rotatores':{
  'observed':'Есть Rotatores.l/.r по 3254 вершины/6518 треугольников, но нет longi/breves label или vertex groups. В каждой стороне один большой связный компонент 6456 граней и небольшой 62-гранный; это не готовое деление по длине пучков.',
  'blocker':'Не размечены непрерывные пучки и их конечные позвонки. Одно общее имя либо длина bounding box не задаёт longi/breves.',
  'next':'Получить/разметить окончания каждого пучка и уровни в согласованном костном контексте. Сначала проверить, действительно ли поверхностная сетка сохраняет отдельные пучки, затем применить маски.',
  'resource':['research/stage7-muscle-batch2-decisions-2026-10-21.json',rel+'/z-bundle-components.json']},
}

rows=[]
for old in previous:
    issue=old['issue']
    if issue=='MG-palmaris_brevis' or issue.startswith('MP-omohyoid_'):continue
    f=family(issue);s=scope[f];ispart=issue.startswith('MP-');newcandidate=f=='multifidus'
    historical=old.get('evidence',[])+['research/stage7-reconstruction-method-plan-2026-10-22.json']
    methods={
      'A':method('reused_prior_evidence','Ранее инвентаризированная текущая геометрия и общий родитель сохранены; полный аудит не повторён. '+old['sourceAssessment'],historical),
      'B':method('candidate_obtained_and_tested' if newcandidate else 'targeted_source_inspected_no_exact_target',s['observed'],[rel+'/source-receipt.json',rel+'/z-remaining-name-types.json',rel+'/z-target-arrays-v2.json']),
      'C':method('authored_mirror_identified_not_admitted' if newcandidate else 'conditional_no_accepted_counterpart',
                 'Зеркальность исходной левой авторской части установлена; положительная ориентация исправлена только в производной, это не отдельный донор.' if newcandidate else 'Не выполнено в этой партии: проверенного противоположного отсутствующего экземпляра/целевой маски нет; отражение не создаёт недостающую сегментацию. Для вариантов зеркальность не предполагается.',[rel+'/z-target-inventory.json'] if newcandidate else []),
      'D':method('authored_separate_part_found_current_parent_mapping_pending' if newcandidate else ('inspected_source_no_target_labels' if ispart else 'not_attempted_no_identified_region'),
                 s['blocker'],[rel+'/z-target-arrays-v2.json'] if ispart else historical),
      'E':method('not_attempted_specific_inputs_missing',plan[issue]['requiredData']+' Новый произвольный объём не создавался; метод не объявляется исчерпанным.',[]),
      'F':method('prior_scoped_evidence_only_not_exhausted' if f in ['auricularis','depressor_supercilii','transversus_menti','orbicularis_oculi','nasalis','orbicularis_oris'] else 'not_attempted_specific_dataset_not_identified',
                 'Сохранённый 3DFACE/MIDA аудит не даёт отдельную целевую метку; полный новый КТ/МРТ поиск и сегментация в этой партии не проводились.' if f in ['auricularis','depressor_supercilii','transversus_menti','orbicularis_oculi','nasalis','orbicularis_oris'] else 'Лицензированные изображения с конкретной целевой разметкой в этой партии не получены; отсутствие результата не доказывает отсутствие набора в мире.', ['research/new-muscle-source-audit.json'] if f in ['auricularis','depressor_supercilii','transversus_menti','orbicularis_oculi','nasalis','orbicularis_oris'] else [])}
    rows.append({'id':issue,'structure':old['structure'],'part':old.get('part'),
      'initialStatus':old['status'],'status':'candidate_review_pending' if newcandidate else 'blocked_current_inputs',
      'productionChanged':False,'admitted':False,'allMethodsExhausted':False,
      'existingAcceptanceCriterion':old['existingAcceptanceCriterion'],'observed':s['observed'],
      'blocker':s['blocker'],'nextStep':s['next'],'methods':methods,'resources':s['resource'],
      'trialModel':f"build_stage7/z_multifidus_trials_v1/thorax_multifidus_{'right' if '_right-' in issue else 'left'}-thoracic-test.glb" if newcandidate else None})
assert len(rows)==29 and len({r['id']for r in rows})==29
assert sum(r['id'].startswith('MG-')for r in rows)==12
assert sum(r['id'].startswith('MP-')for r in rows)==17
result={'schemaVersion':1,'generatedUTC':datetime.now(timezone.utc).isoformat(),'scope':{'muscles':12,'parts':17,'excluded':['MG-palmaris_brevis','MP-omohyoid_right-superior','MP-omohyoid_right-inferior','MP-omohyoid_left-superior','MP-omohyoid_left-inferior','additional left interspinales handled by another agent']},
 'methods':{'A':'Existing resources','B':'External scientific 3D source','C':'Controlled mirroring','D':'Segmentation or authored part','E':'Own reconstruction','F':'Medical imaging'},
 'productionIntegrations':0,'newTrialParts':2,'noModelResolved':0,'allMethodsExhausted':False,
 'source':{'repository':'https://github.com/Z-Anatomy/Models-of-human-anatomy','commit':'04d15340bad66394659c0e3b3ff9d9bb0924f6ca',
   'archiveCache':'research/cache/stage7-z-muscles-04d15340/Z-Anatomy.zip','blendCache':'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend',
   'license':'CC BY-SA 4.0','commercialUse':'Permitted subject to attribution, ShareAlike and other license terms; publication not performed.',
   'requiredAttribution':['Z-Anatomy — Gauthier Kervyn, Marcin Zielinski and contributors','BodyParts3D — The Database Center for Life Science — CC BY-SA 2.1 Japan'],
   'scopeCaution':'Archive also lists NC-attributed ear/kidney content. Those unrelated resources are not exported into these derivatives. Source geometry license does not imply anatomic approval.'},
 'newScientificSources':[{'url':'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/EN/TAH1810%20A4%20EN.htm','scope':'TA98 A04.3.02.204 nomenclature only'},
    {'url':'https://pubmed.ncbi.nlm.nih.gov/10818335/','doi':'10.1016/s1050-6411(00)00004-3','scope':'Bojadsen et al., 2000, comparative dissection 12 fresh + 2 embalmed cadavers; abstract/search text read, EFetch metadata verified. Supports regional architecture differences, not these mesh coordinates.'},
    {'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11051048/','scope':'Indexed section 5.1.1–5.1.2 / Fig.19 text supports craniomedial thoracic course and posterior location; direct page returned CAPTCHA. No image copied and no source-coordinate claim.'}],
 'checks':{'blenderCLI':'5.2.2 LTS, scripts disabled, specific objects read and derivative exports/render views completed',
    'trimesh':'Read-only labelled-bone rigid and similarity registration; watertight/positive volumes after left winding correction',
    'nodeGLB':json.loads((RUN/'node-z-multifidus-glb.json').read_text())['passed'],
    'bvh':'24 actual native/BVH matching rays; indices unchanged; face-pair diagnostics classified by connected component',
    'mcpSceneEvidence':rel+'/mcp-z-multifidus-scene-review.json' if(RUN/'mcp-z-multifidus-scene-review.json').exists() else None,
    'playwright':'Not run by this subtask; no app/card/selection code changed. Trial technical checks do not substitute for future integration UI checks.'},
 'multifidusInterpretation':{'perSide':{'connectedComponents':21,'triangles':3902,'withinComponentCrossingPairs':12,'betweenComponentCrossingPairs':521,'betweenComponentDuplicatePairs':1},
   'withinExampleSegmentMaxMM':0.5659284219402424,'withinExamplesMeasured':11,'withinFlaggedPairs':12,
   'numericalCaution':'Triangle intersection line length is not penetration. Counts/maxima alone are not medical rejection thresholds. Material Tendon is unused in these two source meshes; no attachment conclusion can be drawn from that slot.',
   'boneContactScope':'Some saved surface samples occur at component cranio-caudal mid-range, others at extrema. Neither category proves named attachment/body location. Anatomical contact classification remains pending.',
   'reasonNotIntegrated':'No completed educational admission of the mapped pouches/contacts and no validated mapping to the current parent selection. No claim that source parts are globally or irreparably anatomically wrong.',
   'registrationChoice':'Rigid preserves scale; similarity lowers bone nearest-vertex RMS but changes scale and worsens the maximum distance to the existing parent. Neither metric alone selects an anatomical winner.',
   'maskFeasibility':'Existing BP3D parent is an independently tessellated full muscle. A source-to-parent face/fascicle map has not been proven. Closest-point masks or coordinate cuts would be unvalidated. A separate authored part remains a candidate for isolated educational selection with parent retained.'},
 'rows':rows}
with(RUN/'decision.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'path':str(RUN/'decision.json'),'rows':len(rows),'newTrialParts':2,'admitted':0,'allMethodsExhausted':False},ensure_ascii=False))

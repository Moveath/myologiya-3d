"""Record only this session's new evidence; immutable inputs and issue statuses stay intact."""
import hashlib,json,re,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
rel=lambda p:Path(p).relative_to(ROOT).as_posix()
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
state=read(ROOT/'research/geometry-recovery-state.json')
Z=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
B=ROOT/'research/evidence-runs/bonehub-metacarpal-registration-2026-10-22T07-22-32-957Z-wWtQcl'
P=ROOT/'research/evidence-runs/stage7-interspinales-local-plane-2026-10-22T07-25-20-358Z-RCXRLB'
updates=[]
for current in state['items']:
    r=copy.deepcopy(current);r.pop('history')
    cid=r['catalogueId']
    if r['kind']=='bone':
        if cid in ['metacarpal_1_left','metacarpal_3_left']:
            d=next(x for x in read(B/'decision.json')['structures'] if x['id']==cid)
            file=B/d['testGLB']
            r['resources'].append(dict(file=rel(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),license='CC BY 4.0',source='BoneHub / Visible Human Male, pinned source in decision.json',status='test_only'))
            r['methods'][1].update(status='new_candidate_registered_not_admitted',summary=d['blocker'],evidence=[rel(B/'decision.json'),rel(B/'trial-glb-node-checks.json'),rel(B/f'{cid}-blender-review.json')])
            r['blocker']=d['blocker'];r['nextStep']='Сохранённые ракурсы просмотрены: основание/головка ориентированы согласованно, но текущие соседние поверхности пересекаются. Нужны отмеченные анатомические опоры основания/головки и независимая оценка единой позы; не подбирать transform только для исчезновения пересечений.'
            r['evidence'].extend([rel(B/'decision.json'),rel(B/'trial-glb-node-checks.json')])
        if cid.endswith('_left') and ('foot' in r['issueIds'][0].lower()):
            m=next(m for m in r['methods'] if m['code']=='F')
            m.update(status='image_header_checked_full_volume_not_processed',summary='Pinned FOOT_LEFT.seg.nrrd:17 labels, LPS, spacing0.9375×0.9375×1mm; five digit groups still combine phalanges. Header only64KiB. Matching male CT418636727bytes identified, not downloaded.',evidence=[rel(B/'foot-header-retrieval.json'),rel(B/'decision.json')])
            r['evidence'].append(rel(B/'foot-header-retrieval.json'))
        if any(x in r['issueIds'] for x in ['GEO-HAND-MCP1-R','GEO-HAND-MCP1-U']):
            r['evidence'].append(rel(RUN/'sesamoid-license-followup.json'))
            r['blocker']+=' Supplementary STL 2019: нынешняя политика CC BY/CC BY-NC действует для подач с сентября2024 и не устанавливает права на этот старый файл.'
    elif cid=='interspinales_cervicis_left':
        d=read(P/'mirror-preparation.json')
        r['resources'].append(dict(file=d['file'],sha256=d['sha256'],license='CC BY-SA 2.1 Japan',source='DBCLS, BodyParts3D3.0 FMA71309; bone-fitted rigid reflection',status='test_only'))
        m=next(m for m in r['methods'] if m['code']=='C')
        m.update(status='two_reflections_tested_not_admitted',summary='X=0: endpoint gaps1.237–2.984mm. Bone-fitted rigid plane: C2 endpoint1.779mm, C7 endpoint1.197mm; sampled bone overlap up to1.452mm. No per-bundle repositioning.',evidence=m['evidence']+[rel(P/'admission-decision.json'),rel(P/'bone-plane-fit.json')])
        r['evidence'].extend([rel(P/'admission-decision.json'),rel(P/'blender-review.json'),rel(RUN/'playwright-1280.json'),rel(RUN/'playwright-390.json')])
        r['blocker']='Два отражения не дают принятой сборки целой группы: X=0 оставляет зазоры, локальная костная плоскость возвращает перекрытия C3–C7. Костная симметрия не подтверждает площадки прикрепления. C7–T1 отсутствует.'
        r['nextStep']=read(P/'admission-decision.json')['nextStep']
    elif cid!='palmaris_brevis' and not cid.startswith('omohyoid_'):
        m=next(m for m in r['methods'] if m['code']=='B')
        ev=[rel(Z/'z-target-inventory.json'),rel(Z/'source-receipt.json'),rel(Z/'License.txt')]
        m.update(status='new_pinned_archive_checked',summary='Actual Z-Anatomy blend inspected at pinned commit04d15340. No admitted target mesh obtained; material names/whole muscles are not accepted TA-part segmentation.',evidence=ev)
        r['evidence'].extend(ev)
        if cid in ['thorax_multifidus_right','thorax_multifidus_left']:
            side=cid.rsplit('_',1)[1];f=ROOT/f'build_stage7/z_multifidus_trials_v1/{cid}-thoracic-test.glb'
            r['resources'].append(dict(file=rel(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),license='Z-Anatomy CC BY-SA4.0; required BP3D CC BY-SA2.1Japan attribution retained',sourceObject='Multifidus thoracis muscle.'+side[0],status='test_only'))
            m.update(status='named_part_retrieved_trial_exported',summary='Two real separately named thoracic meshes,3902 triangles each; left source is already mirrored. Rigid bone registration, not accepted parent segmentation.')
            d=next(m for m in r['methods'] if m['code']=='D')
            d.update(status='authored_component_geometry_retrieved',summary='21 connected bundles per side. 521 crossing pairs between bundles,12 within bundles; count alone is not a medical rejection criterion. No matching face mask on current parent muscle established.',evidence=[rel(Z/'z-multifidus-contact-classification-summary.json')])
            r['blocker']='Отдельная грудная геометрия найдена, но соответствие пучков текущим позвонкам/площадкам прикрепления и совмещение с родительской мышцей не принято. Регистрация по костям и пересечения сами по себе не дают анатомического решения. Неиспользуемый слот Tendon не является разметкой сухожилий.'
            r['nextStep']='В сохранённой сцене принять уровни и концы каждого пучка, локализовать контакты с костью; отделить допустимые контакты от ошибок. Проверить совместимость части с текущим родителем до подключения, без произвольного разреза/смещения.'
            r['evidence'].extend([rel(Z/'mcp-z-multifidus-scene-review.json'),rel(Z/'node-z-multifidus-glb.json'),rel(Z/'z-multifidus-contact-classification-summary.json')])
    if cid in ['transversus_menti','thorax_sternalis','thorax_diaphragm','orbicularis_oris','thorax_rotatores_thoracis','thorax_subcostales','thorax_intertransversarii_thoracis']:
        next(m for m in r['methods'] if m['code']=='C').update(status='not_applicable_as_automatic_replacement',summary='Непарная, вариабельная либо объединённая региональная карточка. Автоматическое отражение всей записи не восстанавливает подтверждённый экземпляр/границы части.')
    if r!= {k:v for k,v in current.items() if k!='history'}:updates.append(r)
batch=dict(id='new-sources-and-reflection-batches',at='2026-10-22',integrated=0,
           evidence=[rel(B/'decision.json'),rel(P/'admission-decision.json'),rel(Z/'mcp-z-multifidus-scene-review.json')],
           updates=updates,resume=dict(activeBatch='registered_anatomical_relations_pending',stage8Started=False,
           completed=['55 current owners/parts consolidated; unchanged GLB evidence reused','PB and4omohyoid parts not repeated','New BoneHub candidates and two registered metacarpals','Two independent reflection planes for left interspinales','Actual Z-Anatomy parts and targeted source review','1280/390 research browser check'],
           next='Start from named source evidence and saved Blender scenes. Do not regenerate or repeat prior metrics. For multifidus confirm labelled bundle endpoints/levels and parent compatibility. For foot use the pinned same-donor CT/header route; image segmentation and registration are unfinished, not declared exhausted.',
           doNotRepeat=['PB/omohyoid without new boundaries or method','Known BP3D original/mirrored bone conflicts without new source or landmark registration'],
           remainingWork='No new model passed the combined educational admission gate. A licensed imaging route is still available for investigation; full recovery is not declared complete.'))
with(RUN/'batch-updates.json').open('x',encoding='utf8')as h:json.dump(batch,h,ensure_ascii=False,indent=2)
print(json.dumps(dict(updatedRows=len(updates),batch=rel(RUN/'batch-updates.json'))))

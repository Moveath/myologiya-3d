"""Immutable derivative export and explicit educational admissions, never auto-admit."""
import argparse,hashlib,json,pathlib,shutil,sys
import numpy as np
import trimesh
from cardiovascular_catalog import CARDS,GROUPS,NOTICE,SOURCES
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=ROOT/'build_cardiovascular/bp3d-3.0-v1'
DEST=ROOT/'site/models/bodyparts3d-3.0/cardiovascular'
REPORT='research/cardiovascular-expansion-2026-10-26.md'
FIRST_REPORT='research/cardiovascular-first-integration-2026-10-24.md'
Z_NOTICE='Учебная схематическая модель Z-Anatomy. Ход и диаметр — по авторской кривой источника; это не сегментация реального образца.'
MASK_NOTICE='Часть общей модели BodyParts3D, выделенная списком её граней. Граница части приблизительна.'
EVIDENCE='research/evidence-runs/cardiovascular-first-integration-2026-10-22T11-41-39-801Z-wDXHnD'
UI_EVIDENCE='research/evidence-runs/cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9'
BATCH2_EVIDENCE=['research/evidence-runs/cardiovascular-batch2-2026-10-26T15-47-23-638Z-t6EBhW/batch2-topography.json',
 'research/evidence-runs/z-cardiovascular-2026-10-26T16-04-43-756Z-JXagmr/z-registration.json',
 'research/evidence-runs/z-cardiovascular-2026-10-26T16-04-43-756Z-JXagmr/z-vessel-review.json',
 'research/evidence-runs/z-cardiovascular-2026-10-26T16-04-43-756Z-JXagmr/z-mask-review.json',
 'research/evidence-runs/z-cardiovascular-2026-10-26T16-04-43-756Z-JXagmr/z-publish.json',
 'research/evidence-runs/cardiovascular-node-2026-10-26T16-19-04-440Z-xN5ser/node-production.json',
 'research/evidence-runs/cardiovascular-ui-2026-10-26T16-20-37-157Z-8mRBgG/ui-report.json',
 'research/evidence-runs/regression-part2-cardiovascular-2026-10-26T16-27-43-726Z-giAP4y/summary.json']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def immutable(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data,f'Refuse to overwrite derivative {p}'
    else:
        with p.open('xb')as f:f.write(data)
def exact_mesh(vertices,faces):
    # Area-weighted normals without an absolute metre-scale area tolerance.
    # Retain zero-area/duplicate source triangles; they are reported, not erased.
    unique,inverse=np.unique(vertices,axis=0,return_inverse=True);faces=inverse[faces]
    t=(unique[faces]-unique.mean(0))*1000
    cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n=np.zeros_like(unique)
    for i in range(3):np.add.at(n,faces[:,i],cross)
    lengths=np.linalg.norm(n,axis=1);bad=np.where(lengths==0)[0]
    for v in bad:
        adjacent=np.where(np.any(faces==v,axis=1))[0]
        if len(adjacent):n[v]=cross[adjacent[np.argmax(np.linalg.norm(cross[adjacent],axis=1))]]
    lengths=np.linalg.norm(n,axis=1);n[lengths==0]=[0,0,1];lengths=np.linalg.norm(n,axis=1)
    mesh=trimesh.Trimesh(vertices=unique,faces=faces,process=False);mesh.vertex_normals=n/lengths[:,None]
    return mesh,len(bad)
def prepare(run):
    for id,c in CARDS.items():
        if not c['fma']:continue
        source=ROOT/'research/cache/cardiovascular-bp3d-3.0'/f"{c['fma']}.obj"
        record=BUILD/(id+'.json')
        if not source.exists() or record.exists():continue
        original=trimesh.load(source,force='mesh',process=False)
        vertices=original.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
        mesh,normal_fallbacks=exact_mesh(vertices,original.faces)
        scene=trimesh.Scene();scene.add_geometry(mesh,node_name='s|'+id,geom_name='s|'+id)
        data=scene.export(file_type='glb');target=BUILD/(id+'.glb');immutable(target,data)
        actual=trimesh.load(target,force='mesh',process=False)
        assert np.array_equal(actual.triangles,vertices[original.faces].astype(np.float32).astype(float))
        provenance=json.loads((run/(c['fma']+'-source.json')).read_text(encoding='utf8'))
        assert digest(source)==provenance['sha256']
        result=dict(id=id,source=provenance,trial=target.relative_to(ROOT).as_posix(),sha256=digest(target),triangles=len(mesh.faces),vertices=len(mesh.vertices),boundsM=mesh.bounds.tolist(),watertight=bool(mesh.is_watertight),winding=bool(mesh.is_winding_consistent),volumeM3=float(mesh.volume),degenerate=int((original.area_faces<1e-12).sum()),duplicateFaces=len(mesh.faces)-len(np.unique(np.sort(mesh.faces,axis=1),axis=0)),normalFallbackVertices=normal_fallbacks,roundtrip='Exact float32 triangle corners/order',admission='candidate',transform='(x,z,-y)/1000; exact welding; area-weighted normals, largest adjacent face for cancellation; no fitting, mirroring, smoothing or decimation')
        immutable(record,(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
        print(id,result['triangles'],result['winding'],result['watertight'],flush=True)
def catalogue(run):
    admission_path=ROOT/'scripts/cardiovascular_admissions.json'
    admissions=json.loads(admission_path.read_text(encoding='utf8')) if admission_path.exists()else {}
    records=[];cards={}
    for id,c0 in CARDS.items():
        c=dict(c0);c['noModel']=True
        c['modelNote']='Отдельная принятая геометрия отсутствует. Карточка не обозначает подтверждённую 3D-границу.'
        trial=BUILD/(id+'.json');r=json.loads(trial.read_text(encoding='utf8'))if trial.exists()else None
        if id in admissions and admissions[id].get('kind','bodyparts3d')=='bodyparts3d':
            a=admissions[id];assert a['status']=='educational_limited' and a['evidence'] and r
            assert r['sha256']==a['sha256'] and r['winding']
            if r['degenerate'] or r['duplicateFaces']:assert a.get('technicalExceptions'),'Explicit technical exception review required'
            target=DEST/(id+'.glb');immutable(target,(ROOT/r['trial']).read_bytes())
            c.update(noModel=False,modelFile=target.relative_to(ROOT/'site').as_posix(),modelStatus='educational_limited',modelKind='bodyparts3d',modelRegionLabel='Сердечно-сосудистая система',modelNotice=NOTICE,modelNote=NOTICE+' '+a.get('limitation',''))
        elif id in admissions:
            # Z-Anatomy models and face masks are published by scripts/z_cardiovascular_pipeline.py; only their hash is checked here.
            a=admissions[id];assert a['status']=='educational_limited' and a['evidence']
            file=a['modelFile'] if a['kind']=='z-anatomy' else a['maskFile']
            assert digest(ROOT/'site'/file)==a['sha256'],id
            notice=Z_NOTICE if a['kind']=='z-anatomy' else MASK_NOTICE
            c.update(noModel=False,modelFile=file,modelStatus='educational_limited',modelKind=a['kind'],modelRegionLabel='Сердечно-сосудистая система',modelNotice=notice,modelNote=notice+' '+a.get('limitation',''))
            if a['kind']=='face-mask':
                assert admissions.get(a['segmentOf'],{}).get('kind','bodyparts3d')=='bodyparts3d',id
                c['segmentOf']=a['segmentOf']
        records.append(dict(id=id,ru=c['ru'],lat=c['lat'],system=c['system'],section=next(g['sec']for g in GROUPS if g['id']==c['g']),side=c['side'],noModel=c['noModel'],modelFile=c.get('modelFile'),modelKind=c.get('modelKind'),segmentOf=c.get('segmentOf'),candidate=r,admission=admissions.get(id),relations={k:c[k]for k in ['partOf','origin','drainsTo']if c.get(k)},refs=c['refs']))
        cards[id]=c
    for record in records:
        record['issueIds']=['FUT-005','CV-CATALOG-SOURCES','CV-GEO-MISSING' if record['noModel'] else 'CV-GEO-ACCEPTANCE']
        record['nextAction']=('Найти лицензированный отдельный меш или зарегистрированную сегментацию; для объединяющей карточки определить необходимость самостоятельного меша. Не создавать границы по названию.' if record['noModel'] else 'Проверить заявленную протяжённость, внутренние границы и соединения по зарегистрированным данным и независимой анатомической приёмке; учебный допуск не закрывает полную приёмку.')
    text='/* Generated by scripts/build_cardiovascular.py catalogue; edit cardiovascular_catalog.py. */\n(function(A){\nA.structures='+json.dumps(cards,ensure_ascii=False,indent=2)+';\nA.structureGroups='+json.dumps(GROUPS,ensure_ascii=False)+';\n})(window.ATLAS);\n'
    (ROOT/'site/data-cardiovascular.js').write_text(text,encoding='utf8')
    inventory=dict(schemaVersion=1,scope='Cardiovascular expansion; independent of unresolved stages 6/7',structures=records,counts=dict(cards=len(cards),educational=sum(not c['noModel']for c in cards.values()),noModel=sum(c['noModel']for c in cards.values()),fullAnatomicalAcceptance=0,proceduralReconstructions=0),sources=SOURCES)
    inventory['bySystem']={system:dict(cards=sum(r['system']==system for r in records),educational=sum(r['system']==system and not r['noModel'] for r in records),noModel=sum(r['system']==system and r['noModel'] for r in records)) for system in ('heart','arteries','veins')}
    inventory['counts']['byModelKind']={kind:sum(c.get('modelKind')==kind for c in cards.values()) for kind in ('bodyparts3d','z-anatomy','face-mask')}
    inventory['checkpoint']=dict(report=REPORT,firstReport=FIRST_REPORT,implementationStatus='second_local_educational_batch',testsDate='2026-10-26',registryDate='2026-10-26',evidence=[EVIDENCE+'/node-production.json',EVIDENCE+'/geometry-measurements.json',EVIDENCE+'/cv-heart-1280-result.json',*[UI_EVIDENCE+'/'+name for name in ('cv-vessels-1280-result.json','cv-regression-1280-result.json','cv-heart-390-result.json','cv-heart-390-completion.json','cv-vessels-390-result.json','cv-regression-390-result.json','canvas-raycast.json')]],evidenceBatch2=BATCH2_EVIDENCE,testLimit='Batch 2: Chromium/SwiftShader 1280/390 and Node r170 checks passed; no physical phone, no anatomist acceptance. First batch: Mobile heart scenario reached its time budget after 12 successful checks; remaining checks passed in a separately saved continuation. No full anatomical acceptance or physical-phone test.',preservedLegacy=dict(boneNoModel=0,muscleNoModel=14,musclePartsNoModel=21),next='CV-GEO-MISSING: septa, portal vein and aggregate aorta card; CV-GEO-ACCEPTANCE: expert review of masks, Z-Anatomy courses and junctions. No nervous system or automatic release.')
    (ROOT/'research/cardiovascular-state.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'provenance.json').write_text(json.dumps([r for r in records if not r['noModel'] and r['modelKind'] in ('bodyparts3d','face-mask')],ensure_ascii=False,indent=2),encoding='utf8')
    (DEST/'ATTRIBUTION.md').write_text('# BodyParts3D 3.0 — cardiovascular derivatives\n\nBodyParts3D, © 2008 Database Center for Life Science (DBCLS).\n\nSource: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip\n\nOriginal licensing: https://lifesciencedb.jp/bp3d/info_en/license/index.html\n\nOriginal and derived geometry: **CC BY-SA 2.1 Japan** — https://creativecommons.org/licenses/by-sa/2.1/jp/\n\nCommercial reuse is permitted subject to attribution, ShareAlike and no additional restrictions on this geometry. Derivatives retain every original triangle and use (x,z,-y)/1000, exact vertex welding and stable normals. No invented interiors, mirroring or specimen-specific fitting. See provenance.json for original and derived hashes.\n',encoding='utf8')
    print(json.dumps(inventory['counts']))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','catalogue']);p.add_argument('run');a=p.parse_args();globals()[a.mode](pathlib.Path(a.run))

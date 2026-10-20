import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const dir=path.resolve(process.argv[2]);assert.ok(dir.startsWith(path.resolve('research/evidence-runs')+path.sep));
const write=(n,v)=>fs.writeFile(path.join(dir,n),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const candidates=[
 {id:'K-PELVIS-PREAURICULAR',issue:'CAT-PELVIS-REVIEW',structures:['hip_bone','hip_bone_left'],candidate:'Предушковидная борозда',status:'требует проверки',
  available:'Gray PDF p.231 describes a variable preauricular sulcus. Not a required feature of every adult hip.',needed:'Second independent targeted source, catalogue applicability and a decision on a variant card; individual presence needs an accepted surface. Do not infer sex or coordinates from the reference figure.',refs:['https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf#page=231'],nextStage:5},
 {id:'K-PELVIS-COCCYGEAL-DETAIL',issue:'CAT-PELVIS-REVIEW',structures:['coc_os_coccygis','coc_cornu_coccygeum','sac_foramina_intervertebralia'],candidate:'Детализация Co1 и терминальных проходов S5',status:'требует проверки',
  available:'Gray PDF p.45 describes transverse elements and passages completed at the sacrococcygeal junction. Existing coccyx/cornu are retained, not duplicated.',needed:'Independent anatomical source and distinct-entity/synonym check before additional cards. Segment count and boundaries need same-specimen imaging/segmentation, GEO-007; do not apply a fixed segment count.',refs:['https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf#page=45','https://pmc.ncbi.nlm.nih.gov/articles/PMC5662850/'],nextStage:5},
 {id:'K-PELVIS-POSTERIOR-OBTURATOR',issue:'CAT-PELVIS-REVIEW',structures:['cox_tuberculum_obturatorium_posterius','context_hip_bone_left_A02_5_01_312'],candidate:'Принадлежность заднего запирательного бугорка',status:'требует проверки',
  available:'TA98 catalogue places .312 in pubic group; Gray describes posterior tubercle on ischial border. Both records remain variants; no part mask assigned.',needed:'Resolve nomenclature hierarchy versus anatomical location using a further independent atlas; identify the variant on each actual mesh before a point/part mask is accepted.',refs:['https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1027%20A2F%20EN.htm','https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf#page=234'],nextStage:5},
 {id:'K-PELVIS-GREATER-SCIATIC-CONTRIBUTORS',issue:'CAT-PELVIS-REVIEW',structures:['extra_hip_bone_greater_sciatic_foramen','extra_hip_bone_left_greater_sciatic_foramen'],candidate:'Полный набор участников большого седалищного отверстия',status:'требует проверки',
  available:'Passage exists and differs from notch (Gray/Semmelweis). OpenStax includes sacrum in its boundary description; ligament attachment alone is not direct bony boundary.',needed:'Second targeted source for each proposed sacral/capsular boundary role; then extend existing two IDs, not create duplicate shared IDs. Soft tissue boundaries cannot be recovered from bare hip meshes.',refs:['https://openstax.org/books/anatomy-and-physiology-2e/pages/8-3-the-pelvic-girdle-and-pelvis','https://semmelweis.hu/anatomia/files/2016/08/hj-dorsreg-eng.pdf'],nextStage:5}
];
await write('pelvic-candidates.json',candidates);
const rows=JSON.parse(await fs.readFile(dir+'/reviewed-records-ui-final.json','utf8'));
const original=JSON.parse(await fs.readFile(dir+'/inventory-before.json','utf8'));
const groups=Object.fromEntries(['hip_bone','hip_bone_left','sacrum'].map(b=>[b,{originalIds:original.filter(p=>p.b===b&&p.t==='ta').map(p=>p.id),attachments:original.filter(p=>p.b===b&&p.t==='att').map(p=>p.id),reviewedIds:rows.filter(p=>p.bone===b).map(p=>p.id)}]));
await write('coverage.json',{groups,originalBoneRecords:114,reviewedBoneRecords:140,attachmentRecords:6,candidates:candidates.map(x=>x.id),referencesReused:['B08','B09','B10'],anatomicalCoordinatesAccepted:0,fullAnatomicalCompletenessAccepted:false});
await write('geometry-observations.json',{imagesViewed:7,
 sacrum:'Anterior/posterior openings and caudal segment-like region visible. No accepted S5–Co1 boundary or segment count; generic markers do not cover all paired foramina/cornua.',
 hipBones:'Acetabular and auricular regions visible at overview scale; no accepted lunate/symphysial/auricular mask. No mirrored left points.',
 models:['site/leg-q-glb.txt','build_context_bones/leg_extra_hi.glb'],distanceCrossCheckMaximumMm:0.0000750894062199331,
 separateCoccyxMesh:false,newCoordinates:0,newContours:0,newMasks:0,geometryIssue:'GEO-PELVIS-LANDMARKS',priorBoundaryIssue:'GEO-007'});
await write('test-incidents.json',{incidents:[
 {file:'trimesh-pelvis.json',status:'failed_partial_json',reason:'numpy.bool_ was not JSON serializable after measurements. Partial file retained.',fix:'Convert side result to bool and serialize complete payload before opening output.',successfulReplacement:'trimesh-pelvis-v2.json'},
 {file:'../stage5-pelvis-mcp-2026-10-18T16-30-44-453Z-FQI3H7/result.json',status:'failed_test_assertion',reason:'Compared rays array to numeric 10. All preceding phases completed; production app unchanged.',fix:'Check rays.length, actual BVH count and nonempty hits.',successfulRecheck:'desktop-recheck.json'},
 {file:'update-registry.py',status:'prewrite_assertion_corrected',reason:'Initial ID parser omitted historical IDs with underscores.',fix:'Read all issue heading IDs; assert 221 prior cards before any write. Final result validates 224 and retained history.'}
 ]});
const oldHashes=JSON.parse(await fs.readFile(dir+'/hashes-before.json','utf8'));const changed=[];
for(const [f,h]of Object.entries(oldHashes))if(createHash('sha256').update(await fs.readFile(f)).digest('hex')!==h)changed.push(f);
const newFiles=['scripts/pelvis_stage5_review.py','verify/review_pelvis_stage5.py','verify/review_pelvis_stage5_blender.py','tools/prepare-stage5-pelvis-evidence.mjs','tools/verify-stage5-pelvis.mjs','tools/prepare-stage5-pelvis-mcp.mjs','tools/finalize-stage5-pelvis-evidence.mjs','research/stage5-pelvis-report-2026-10-18.md'];
const files=[...new Set([...changed,...newFiles])],hashes={};for(const f of files)hashes[f]=createHash('sha256').update(await fs.readFile(f)).digest('hex');
await write('changed-files.json',{changed,newFiles,sha256:hashes});
await write('evidence.json',{scope:'Stage5 pelvic batch; 114 original bone records and 26 additions. No original model or coordinate modifications.',
 status:'checks_completed_with_documented_test_incidents',data:'data-regression-ui-final.json',records:'reviewed-records-ui-final.json',coverage:'coverage.json',
 blender:'blender-pelvis.json',trimesh:'trimesh-pelvis-v2.json',observations:'geometry-observations.json',pubmed:'pubmed-coccyx.json',
 desktopInitial:'../stage5-pelvis-mcp-2026-10-18T16-30-44-453Z-FQI3H7/result.json',desktopContinuation:'desktop-recheck.json',
 mobile:'../stage5-pelvis-mcp-2026-10-18T16-33-21-851Z-l5Tclu/result.json',finalLabels:'code-labels-result.json',ring:'ring-final-ui.json',
 registry:'registry-final.json',candidates:'pelvic-candidates.json',incidents:'test-incidents.json',files:'changed-files.json',
 tests:['Three Python generators','verify_ta98.py:762 terms,3 historical differences','Node stable IDs/coordinates/out-of-scope preservation','Trimesh/Blender 74 anchors,7 viewed renders','Playwright1280dark composed check,390light full check','Final labels1280/390'],
 notRepeated:['Unchanged full mesh self-intersection scans','Unchanged skull clipping suite'],newAcceptedGeometry:0});
const issues=await fs.readFile('ANATOMY_ISSUES.md','utf8'),progress=await fs.readFile('ANATOMY_PROGRESS.md','utf8');
assert.ok(progress.includes(await fs.readFile(dir+'/ANATOMY_PROGRESS.md','utf8').then(s=>s.slice(s.indexOf('### LOG-')))));
const ids=[...issues.matchAll(/^### ([^\n]+)\n/gm)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length);
for(const id of ['PIN-PELVIS-KIND','GEO-PELVIS-LANDMARKS','SYS-ADDITIONAL-TA98'])assert.ok(issues.includes('['+id+'](#'+id.toLowerCase()+')'));
let localLinks=0;const missing=[];
for(const file of ['research/stage5-pelvis-report-2026-10-18.md'])for(const m of(await fs.readFile(file,'utf8')).matchAll(/\]\(([^)]+)\)/g)){
 if(/^(https?:|#)/.test(m[1]))continue;localLinks++;try{await fs.access(path.resolve(path.dirname(file),m[1]));}catch{missing.push(m[1]);}}
assert.deepEqual(missing,[]);
await write('final-validation.json',{status:'passed',uniqueIssueHeadings:ids.length,previousProgressHistoryPreserved:true,localLinksChecked:localLinks,changedFiles:changed,newFiles,newModelWrites:0});
console.log(JSON.stringify({status:'passed',changedFiles:changed,newFiles:newFiles.length,localLinksChecked:localLinks}));

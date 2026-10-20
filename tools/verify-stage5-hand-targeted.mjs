import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,contributingBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8'));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), idx=indexLandmarks(A.pins),oldIds=new Set(before.pins.map(p=>p.id));
assert.equal(Object.keys(idx.byId).length,A.pins.length,'unique IDs');
const allowedIds=new Set([...[1,2,3,4,5].flatMap(i=>['pd'+i+'_caput','pd'+i+'_tuberositas']),...[2,3,4,5].map(i=>'pm'+i+'_basis')]);
for(const p of before.pins){const q=idx.byId[p.id];assert.ok(q,p.id);for(const k of ['b','c','p','n','m','geometryKind'])assert.deepEqual(q[k],p[k],p.id+'/'+k);
 if(!allowedIds.has(p.id))assert.deepEqual(q,p,p.id);}
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.contextBoneSources,before.contextBoneSources);
for(const [b,d] of Object.entries(before.bones))assert.deepEqual(A.bones[b],d,b);
const bones=Object.keys(A.bones).filter(b=>!before.bones[b]);assert.equal(bones.length,29);
for(const b of bones){const d=A.bones[b];assert.equal(d.side,'left');assert.equal(d.noModel,true);assert.ok(!d.sourceId);assert.ok(d.note.includes('не отражалась'));}
assert.equal(A.bones.radius_left.noModel,true);assert.equal(A.bones.ulna_left.noModel,true);
const added=A.pins.filter(p=>!oldIds.has(p.id)),left=added.filter(p=>p.side==='left'),right=added.filter(p=>p.side==='right');
assert.equal(right.length,43);assert.equal(left.length,152);assert.equal(left.filter(p=>p.t==='ta').length,77);
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.deepEqual(p.m,[]);assert.equal(hasLandmarkPosition(p),false);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);assert.ok(p.refs.length>=2);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.id);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b],p.id+'/'+b);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);if(p.side==='left')assert.equal(A.bones[b].side,'left',p.id+'/'+b);}
 for(const b of p.articulatesWith||[]){assert.ok(A.bones[b]);if(p.side==='left')assert.equal(A.bones[b].side,'left');}
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],p.id+'/'+id);
 if(p.side==='left'){assert.ok(A.bones[p.b].noModel);assert.ok(!p.softTissueComponents);assert.ok(idx.byId[p.templateRecord]);}
}
for(const prefix of ['', 'left_hand_']){
 const q=idx.byId[prefix+'extra_hand_cmc4_joint'];assert.equal(q.relations.find(r=>r.bone==='capitate'+(prefix?'_left':'')).role,'adjacentContext');
 assert.equal(contributingBoneIds(q).length,2);assert.equal(contributingBoneIds(idx.byId[prefix+'extra_hand_midcarpal_joint']).length,7);
 assert.ok(!relatedBoneIds(idx.byId[prefix+'extra_hand_radiocarpal_joint']).includes(prefix?'ulna_left':'ulna'));
 for(const id of ['lunate_facet_hamate','hamate_facet_lunate','capitate_facet_metacarpal_4'])assert.equal(idx.byId[prefix+'extra_hand_'+id].anatomicalVariant,true);
}
assert.equal(right.filter(p=>p.anatomicalEntity==='joint').length,8);
const previous='research/evidence-runs/stage5-hand-2026-10-18T19-41-08-979Z-py70dn';
const candidates=JSON.parse(await fs.readFile(previous+'/remaining-candidates.json','utf8')).rows;
const decisions=candidates.map(c=>{
 const id=c.candidateId;let decision,ids=[],sources=[],remaining;
 if(id.startsWith('HAND-DISTAL')){decision='already_represented_distinct_parts';ids=c.existingIds;sources=['hand_ttu','hand_distal_head','hand_gray1918'];}
 else if(id.startsWith('HAND-FDS')){decision='insufficient_evidence';ids=c.existingIds;sources=['hand_fds_uams','hand_fds_29020826'];remaining='Законный полный текст PMC6535955/издательская копия и адресная сверка поля прикрепления со вторым источником; затем разметка данного образца. Абстракт не закрывает критерий.';}
 else if(id==='HAND-LEFT-SCOPE'){decision='missing_catalogue_added_models_blocked';ids=bones;sources=['hand_gray1918','hand_sobotta1914','sesamoid_chen2015','sesamoid_civan2020'];remaining='29 моделей и индивидуальная сегментация отсутствуют: GEO-HAND-LEFT-MODELS.';}
 else if(id.startsWith('HAND-FACET-')){const key=id.slice(11).toLowerCase();ids=right.filter(p=>p.id.includes('_facet_')&&p.id.replace('extra_hand_','').replace('_facet_','-').replaceAll('_','-')===key).map(p=>p.id);
   // Candidate keys retain underscores inside bone IDs.
   if(!ids.length)ids=right.filter(p=>p.id==='extra_hand_'+key.replace('-', '_facet_')).map(p=>p.id);
   assert.equal(ids.length,1,id);const p=idx.byId[ids[0]];decision=p.anatomicalVariant?'variant_card_added':'separate_surface_added';sources=p.refs.map(r=>r.id);}
 else {const mapping={
   'HAND-SCAPHOID-WAIST':'scaphoid_waist','HAND-CAPITATE-HEAD':'capitate_head','HAND-CAPITATE-NECK':'capitate_neck',
   'HAND-JOINT-MIDCARPAL':'midcarpal_joint',...Object.fromEntries([2,3,4,5].map(i=>['HAND-JOINT-CMC'+i,'cmc'+i+'_joint'])),
   ...Object.fromEntries([2,3,4].map(i=>['HAND-JOINT-INTERMETA'+i+'-'+(i+1),'intermetacarpal_joint_'+i+'_'+(i+1)]))};
   ids=['extra_hand_'+mapping[id]];assert.ok(idx.byId[ids[0]],id);decision='separate_card_added';sources=idx.byId[ids[0]].refs.map(r=>r.id);}
 return {...c,decision,implemented:decision!=='insufficient_evidence',resultIds:ids,sourceIds:sources.map(id=>id.startsWith('arm_forearm_')?id:'arm_forearm_'+id),status:decision==='insufficient_evidence'?'требует проверки':'проверена',
  confidence:decision==='insufficient_evidence'?'Недостаточно для точного поля прикрепления':'Высокая для каталожного решения; геометрия не принята',
  remaining:remaining||'Координаты/маски/наличие варианта на образце отдельно не приняты: GEO-HAND-LANDMARKS / GEO-HAND-LEFT-MODELS.'};
});
assert.equal(decisions.length,53);assert.equal(decisions.filter(c=>c.status==='проверена').length,49);
const refs=new Set([...A.pins.flatMap(p=>(p.refs||[]).map(r=>r.id)),...Object.values(A.bones).flatMap(b=>(b.refs||[]).map(r=>r.id))]);
for(const c of decisions)for(const id of c.sourceIds)assert.ok(refs.has(id),'Unknown reference '+id);
const allow=new Set(['scripts/make_pins.py','scripts/make_context_bone_data.py','site/data-context-bones.js','site/pins.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
let protectedFiles=0;for(const [f,h] of Object.entries(JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'))))if(!allow.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const resources=JSON.parse(await fs.readFile('research/evidence-runs/stage5-left-forearm-2026-10-18T19-20-46-330Z-35NAkG/left-forearm-resources.json','utf8'));
for(const r of resources.resources)assert.equal(createHash('sha256').update(await fs.readFile(r.file)).digest('hex'),r.sha256,r.file);
const result={status:'passed',candidatesReviewed:53,catalogueDecisionsConfirmed:49,attachmentDecisionsPending:4,newBoneCards:29,
 newRightRecords:right.length,newLeftRecords:left.length,existingRecordsClarified:14,unchangedRecords:before.pins.length-14,
 totalPins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,handRecords:A.pins.filter(p=>p.handReview).length,
 handBoneCards:Object.values(A.bones).filter(b=>b.sub==='hand'&&b.g!=='b_soft').length,
 newRightJoints:8,newLeftJoints:left.filter(p=>p.anatomicalEntity==='joint').length,protectedFiles,protectedModelResources:resources.resources.length,
 newCoordinates:0,acceptedCoordinates:0};
const suffix=process.argv[3]||'';assert.ok(/^[-a-z0-9]*$/.test(suffix));
for(const [file,data] of [['data-regression',result],['candidate-decisions',decisions],['added-records',added],['left-bone-inventory',bones.map(id=>({id,...A.bones[id]}))]])
 await fs.writeFile(path.join(out,file+suffix+'.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));

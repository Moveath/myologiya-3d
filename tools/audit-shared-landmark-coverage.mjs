// Reproducible coverage ledger. Classification is curated in the pending registry;
// automated coverage is not independent anatomical acceptance of every bone term.
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {checkData} from './verify-shared-landmarks.mjs';
import {indexLandmarks,isOwnBoneTerm,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const root=path.resolve(import.meta.dirname,'..');
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
const a=JSON.parse(JSON.stringify(box.window.ATLAS)),index=indexLandmarks(a.pins);
const pending=JSON.parse(await fs.readFile(path.join(root,'research/shared-landmarks-pending.json'),'utf8'));
const skull=JSON.parse(await fs.readFile(path.join(root,'site/skull-whole.json'),'utf8')).rows;
const reviewed=a.pins.filter(p=>p.relations?.length);
const confirmed=Object.values(Object.groupBy(reviewed,p=>p.concept)).map(pins=>({concept:pins[0].concept,codes:[...new Set(pins.flatMap(p=>[p.c,p.educationCode].filter(Boolean)))],instances:pins.map(p=>p.id),bones:[...new Set(pins.flatMap(p=>p.relations.map(r=>r.bone)))]}));
const skullQueue=new Map(pending.skull.flatMap(g=>g.codes.map(n=>[n,g.reason])));
const excludedNumbers=new Set([13,14,18,21,33,34,35,36,37,39,40,41,43,59,63,71]);
const skullRows=skull.map(r=>{const n=Number(r.c.split('.').at(-1));const c=confirmed.find(c=>c.codes.includes(r.c));return {code:r.c,ru:r.ru,disposition:c?'implemented':skullQueue.has(n)?'pending_relation_review':excludedNumbers.has(n)?'local_repeated_or_variant_not_one_shared_instance':'group_view_or_future_not_a_point',reason:skullQueue.get(n)||null,instances:c?.instances||[]};});
const cards=Object.entries(a.bones).filter(([,b])=>!b.g.startsWith('b_soft')).map(([id,b])=>{
 const pins=index.byBone[id]||[], own=pins.filter(p=>isOwnBoneTerm(p,id));
 const regions=[];
 if(b.g.startsWith('head_'))regions.push('head');
 if(b.g==='b_carpus')regions.push('carpus');
 if(['neck_vertebrae','thorax_spine','b_lumbar'].includes(b.g)||id==='sacrum')regions.push('spine');
 if(b.g.startsWith('thorax_'))regions.push('thorax');
 if(['hip_bone','hip_bone_left','sacrum'].includes(id))regions.push('pelvis');
 if(['b_meta','b_metatarsus','b_phal','b_toes'].includes(b.g))regions.push('distal-limbs');
 const queue=pending.other.filter(r=>r.bones?.includes(id)||regions.includes(r.region)).map(r=>r.id);
 if(regions.includes('head'))queue.push(...[...skullQueue.keys()].map(n=>'A02.1.00.'+String(n).padStart(3,'0')));
 return {id,ru:b.ru,group:b.g,ownTermCount:own.length,ownIDs:own.map(p=>p.id),
  sharedInstances:pins.filter(p=>p.relations?.length).map(p=>p.id),legacyShared:pins.filter(p=>p.sh).map(p=>p.id),
  candidateReview:queue,reviewResult:queue.length?'Existing terms inspected; related candidate families listed, membership not inferred from region.':'Existing local terms inspected; no further shared instance established from current records.',
  rule:'Articular contact, a matching name, an attachment or a part of one adult bone is not a shared landmark.'};
});
const data=await checkData();
const textCandidates=a.pins.filter(p=>!p.id.startsWith('shared_skull_')&&p.t==='ta'&&/вместе|между.*кост|совмест|смежн|соседних|образуют|шов/i.test(p.x||''))
 .map(p=>({id:p.id,bone:p.b,latin:p.lat,disposition:p.relations?.length?'implemented':p.id==='carp_os_centrale'?'variant_context':
 ['carp_sulcus_carpi','cox_ramus_ischiopubicus','cox_linea_arcuata','tal_sulcus_tali','cal_sulcus_calcanei','head_sphenoid_A02_1_05_041'].includes(p.id)?'pending_named_candidate_or_local_contribution':'local_structure_or_adjacency_not_a_shared_instance'}));
const report={date:'2026-10-15',scope:'All 141 existing bone cards, all existing pins and the 97-row skull catalogue. Structural checks plus shared-candidate classification, not a claim of exhaustive anatomical validation of all terms.',
 counts:{...data,affectedBones:new Set(reviewed.flatMap(p=>p.relations.map(r=>r.bone))).size,
  pendingSkullTerms:skullQueue.size,pendingOtherFamilies:pending.other.length,newUnlocated:reviewed.filter(p=>!p.p).length},
 confirmed,cards,skullRows,textCandidates,
 coordinateLimits:reviewed.filter(p=>!hasLandmarkPosition(p)).map(p=>({id:p.id,status:p.p?'existing_coordinate_unverified':'no_coordinate'})),
 pendingRegistry:'research/shared-landmarks-pending.json'};
await fs.writeFile(path.join(root,'research/shared-landmarks-coverage.json'),JSON.stringify(report,null,2)+'\n');
const table=['# Проверка 141 костной карточки','',report.scope,'','Числа собственных терминов и все прежние ID проверены против исходных региональных данных. Список кандидатов региона не означает доказанную связь с каждой его костью.','',
 '| Кость / ID | Собственные термины | Подтверждённые общие экземпляры | Очередь проверки |','|---|---:|---|---|',
 ...cards.map(c=>`| ${c.ru} / \`${c.id}\` | ${c.ownTermCount} | ${c.sharedInstances.join(', ')||'—'} | ${c.candidateReview.length?c.candidateReview.length+' записей; см. JSON':'Новых общих записей не установлено'} |`)];
await fs.writeFile(path.join(root,'research/shared-landmarks-bone-cards.md'),table.join('\n')+'\n');
console.log(JSON.stringify(report.counts));

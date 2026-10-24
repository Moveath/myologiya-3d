// Extensible system registry. A structure has one owner and explicit typed links.
export const ANATOMICAL_SYSTEMS = Object.freeze({
  bones:{label:'Кости',color:0xe4dbbd,defaultVisible:true},
  muscles:{label:'Мышцы',color:0xb56158,defaultVisible:true},
  heart:{label:'Сердце',color:0xc77679,defaultVisible:false},
  arteries:{label:'Артерии',color:0xd95b42,defaultVisible:false},
  veins:{label:'Вены',color:0x637fcd,defaultVisible:false},
});
export function systemOf(structure) {
  return structure.data?.system || (['m','o'].includes(structure.kind)?'muscles':'bones');
}
export function systemDefaults(saved={}) {
  return Object.fromEntries(Object.entries(ANATOMICAL_SYSTEMS).map(([key,s])=>[key,typeof saved[key]==='boolean'?saved[key]:s.defaultVisible]));
}
export function structureRelations(id,catalogue) {
  const card=catalogue[id];if(!card)return [];
  const links=[];
  for(const [field,label]of [['partOf','Часть структуры'],['origin','Начинается / продолжается от'],['drainsTo','Отток в']])
    if(card[field]&&catalogue[card[field]])links.push({id:card[field],label});
  for(const [key,c]of Object.entries(catalogue)) {
    if(c.partOf===id)links.push({id:key,label:'Анатомическая часть'});
    if(c.origin===id)links.push({id:key,label:'Ветвь / продолжение'});
    if(c.drainsTo===id)links.push({id:key,label:'Приток'});
  }
  return links;
}
export function admittedModel(card) {
  return !!card&&!card.noModel&&card.modelStatus==='educational_limited'&&typeof card.modelFile==='string';
}

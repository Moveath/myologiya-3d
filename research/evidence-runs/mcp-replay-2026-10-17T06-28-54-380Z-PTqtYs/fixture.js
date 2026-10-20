async(page)=>{
 const screenshots=[],dir="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/mcp-replay-2026-10-17T06-28-54-380Z-PTqtYs";
 const safePage=new Proxy(page,{get(target,key){
  if(key==='screenshot')return async(options={})=>{
   const nonce=await target.evaluate(()=>crypto.randomUUID());
   const base=String(options.path||'capture.png').split(/[\\/]/).pop().replace(/[^a-zA-Z0-9_.-]/g,'_');
   const actual=dir+'/'+nonce+'-'+base;screenshots.push(actual);
   return target.screenshot({...options,path:actual});
  };
  const value=Reflect.get(target,key);return typeof value==='function'?value.bind(target):value;
 }});
 const result=await (async(page)=>{await page.screenshot({path:"C:\\Users\\\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\\Desktop\\\u0443\u0447\u0435\u0431\u0430\\\u041c\u0438\u043e\u043b\u043e\u0433\u0438\u044f 3D\\shots\\stage5-skull-batch8\\1280-dark-batch-0.png"});return {status:"passed",purpose:"historical-path collision test"};})(safePage);
 return {result,screenshots,evidenceRun:dir};
}
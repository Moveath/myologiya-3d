// Read a saved fixture without editing it; redirect page screenshots to a new run.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const input=path.resolve(process.argv[2] || '');
if(!process.argv[2] || !input.startsWith(root+path.sep))throw Error('Pass a project MCP fixture filename');
const source=await fs.readFile(input,'utf8');
const run=await createEvidenceRun(root,'mcp-replay');
const code=`async(page)=>{
 const screenshots=[],dir=${JSON.stringify(run.dir.replaceAll('\\','/'))};
 const safePage=new Proxy(page,{get(target,key){
  if(key==='screenshot')return async(options={})=>{
   const nonce=await target.evaluate(()=>crypto.randomUUID());
   const base=String(options.path||'capture.png').split(/[\\\\/]/).pop().replace(/[^a-zA-Z0-9_.-]/g,'_');
   const actual=dir+'/'+nonce+'-'+base;screenshots.push(actual);
   return target.screenshot({...options,path:actual});
  };
  const value=Reflect.get(target,key);return typeof value==='function'?value.bind(target):value;
 }});
 const result=await (${source.trim().replace(/;$/, '')})(safePage);
 return {result,screenshots,evidenceRun:dir};
}`;
const fixture=await run.write('fixture.js',code);
await run.write('provenance.json',{input,generated:fixture,scope:'page.screenshot only; original fixture read-only; rerun uses a new screenshot UUID'});
console.log(JSON.stringify({fixture,run:run.dir}));

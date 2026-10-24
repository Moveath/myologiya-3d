// Explicit local-process fallback when the MCP session cannot grant actions.
// Only the loopback atlas and this newly launched browser are touched.
import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from 'playwright';
const run=path.resolve(process.argv[2]),revision=process.argv[3]||'v7';
if(!/^v\d+$/.test(revision))throw Error('Invalid revision');
const browser=await chromium.launch({headless:true,executablePath:process.argv[4]||process.env.ATLAS_CHROMIUM||undefined,
 args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],timeout:15000});
const results=[];let watchdog;
try{
 watchdog=setTimeout(()=>{browser.close().finally(()=>process.exit(124));},150000);
 for(const width of [1280,390]){
  const context=await browser.newContext({viewport:{width,height:width===390?844:900},deviceScaleFactor:1,
   isMobile:width===390,hasTouch:width===390,colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
  const page=await context.newPage();
  for(const phase of ['setup','cards','sides']){
   const text=await fs.readFile(path.join(run,`mcp-neck-${revision}-${width}-${phase}.txt`),'utf8');
   const test=new Function('return ('+text+');')();
   const result=await test(page);results.push({...result,runner:'local Playwright process, not MCP'});
   await fs.writeFile(path.join(run,`cli-neck-${revision}-${width}-${phase}.json`),JSON.stringify(results.at(-1),null,2),{flag:'wx'});
   console.log(JSON.stringify({width,phase,status:result.status,checks:result.checks.length,error:result.error}));
   if(result.status!=='passed')throw Error(result.error);
  }
  await context.close();
 }
}finally{
 clearTimeout(watchdog);await browser.close();
 await fs.writeFile(path.join(run,`cli-neck-${revision}-summary.json`),JSON.stringify(results,null,2),{flag:'wx'});
}

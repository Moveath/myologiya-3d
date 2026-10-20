// Produces a NEW derivative only. Never replaces an existing GLB or its report.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {inspectGeometry, validateExport} from './geometry-export-check.mjs';

const [input, output] = process.argv.slice(2);
if (!input || !output || path.extname(output).toLowerCase() !== '.glb')
  throw Error('Usage: node tools/package-geometry-safe.mjs SOURCE.glb NEW-OUTPUT.glb');
if (path.resolve(input) === path.resolve(output)) throw Error('Source and output must differ');
const reportPath = output + '.validation.json';
for (const name of [output,reportPath]) {
  try { await fs.access(name); throw Error(`Refusing existing output: ${name}`); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
}
const temp = await fs.mkdtemp(path.join(os.tmpdir(),'atlas-export-'));
try {
  const candidate = path.join(temp,'candidate.glb');
  const cli = fileURLToPath(new URL('./node_modules/gltfpack/cli.js',import.meta.url));
  const flags = ['-c','-noq','-kn','-km'];
  const run = spawnSync(process.execPath,[cli,'-i',input,'-o',candidate,...flags],{encoding:'utf8'});
  if (run.error || run.status !== 0) throw Error(run.error?.message ?? run.stderr.slice(-1200));
  const before = await inspectGeometry(input), after = await inspectGeometry(candidate);
  const errors = validateExport(before,after);
  if (errors.length) throw Error(`Export rejected: ${errors.slice(0,12).join('; ')}`);
  const report = {flags,reference:before,output:{...after,file:output},errors,
    limits:'No anatomical approval or self-intersection proof. No texture conversion. Non-quantized positions/normals; compare source geometry separately.'};
  // COPYFILE_EXCL prevents a race from overwriting an existing output.
  await fs.copyFile(candidate,output,fs.constants.COPYFILE_EXCL);
  await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify({output,meshes:after.meshes.length,errors:0,report:reportPath}));
} finally {
  await fs.unlink(path.join(temp,'candidate.glb')).catch(error => { if (error.code !== 'ENOENT') throw error; });
  await fs.rmdir(temp);
}

// New test evidence belongs to an allocated run, never to a historical snapshot.
import fs from 'node:fs/promises';
import path from 'node:path';

export async function createEvidenceRun(root, label) {
  if (!/^[a-z0-9-]+$/.test(label)) throw new Error('Invalid evidence run label');
  const parent = path.resolve(root, 'research/evidence-runs');
  await fs.mkdir(parent, {recursive:true});
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const dir = await fs.mkdtemp(path.join(parent, `${label}-${stamp}-`));
  return {
    dir,
    async write(name, value) {
      if (path.basename(name) !== name || /[\\/]/.test(name) || name === '..') throw new Error('Invalid evidence filename');
      const target = path.join(dir, name);
      await fs.writeFile(target, typeof value === 'string' ? value : JSON.stringify(value,null,2)+'\n', {flag:'wx'});
      return target;
    },
  };
}

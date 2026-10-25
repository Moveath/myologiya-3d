// Print ATLAS muscles/groups defined by the given hand-written data files as JSON (read-only).
import fs from 'node:fs';
import vm from 'node:vm';
const ctx = {window: {}};
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const file of process.argv.slice(2)) vm.runInContext(fs.readFileSync(file, 'utf8'), ctx);
process.stdout.write(JSON.stringify({muscles: ctx.window.ATLAS.muscles, groups: ctx.window.ATLAS.groups}));

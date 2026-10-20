"""Write Python check evidence into a unique run allocated by the Node helper."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def write_report(value, label, filename, target=None):
    if target is None:
        result = subprocess.run(['node', '--input-type=module', '-e',
            'import {createEvidenceRun} from "./tools/evidence-run.mjs";'
            'console.log((await createEvidenceRun(process.cwd(),process.argv[1])).dir);', label],
            cwd=ROOT, check=True, capture_output=True, text=True, encoding='utf-8')
        target = Path(result.stdout.strip()) / filename
    else:
        target = Path(target).resolve()
        if not target.is_relative_to(ROOT / 'research/evidence-runs') or not target.parent.is_dir():
            raise ValueError('Use an existing evidence-run directory, not a historical report path')
    with target.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return target

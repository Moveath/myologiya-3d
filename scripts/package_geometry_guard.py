"""Check every candidate before a publisher is allowed to write any asset."""
from pathlib import Path
import subprocess
import json


def validate_candidates(root, reference, candidates, expected_bones):
    root=Path(root)
    checker=Path(__file__).resolve().parents[1]/'tools/check-geometry-export.mjs'
    for candidate in candidates:
        run=subprocess.run(['node',str(checker),str(root/reference),str(root/candidate)],
                           capture_output=True,text=True,encoding='utf-8')
        if run.returncode:
            raise ValueError('Geometry export rejected before publication: '+(run.stdout+run.stderr)[-1500:])
        actual=json.loads(run.stdout)['referenceBones']
        if actual != expected_bones:
            raise ValueError('Actual hi GLB bone counts disagree with STL/metadata')

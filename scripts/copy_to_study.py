"""Create a new portable project folder in the user's existing study directory.

No existing folder is replaced. Dependencies and cached third-party publications
are excluded; tracked sources, distributable assets and downloaded head models
are included. No credentials or .git directory are copied.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
study=root.parent/'учеба'
destination=study/'Миология 3D'
study.mkdir(exist_ok=True)
destination.mkdir(exist_ok=False)
relative_paths=[p for p in subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode('utf-8').split('\0') if p]
relative_paths+=['build_head/head_hi.glb','build_head/head.glb','build_head/head_q.glb','build_head/meta.json']
relative_paths += [str(p.relative_to(root)) for directory in ['stl_head','shots/head'] for p in (root/directory).rglob('*') if p.is_file()]
for relative in relative_paths:
    source=(root/relative).resolve()
    source.relative_to(root)
    target=destination/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest(),relative
subprocess.run([__import__('sys').executable,str(destination/'scripts/package_site.py'),str(destination/'dist')],check=True)
print('Project folder:',destination)
print('Files copied and verified:',len(relative_paths))

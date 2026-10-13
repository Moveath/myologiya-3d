"""Create or explicitly update the portable atlas in the study directory.

--update copies project-owned files into an existing atlas; unrelated files stay.
Dependencies and cached third-party publications
are excluded; tracked sources, distributable assets and downloaded head models
are included. No credentials or .git directory are copied.
"""
from pathlib import Path
import argparse
import hashlib
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--update',action='store_true',help='Update the previously created atlas folder without deleting files')
args=parser.parse_args()
study=root.parent/'учеба'
destination=study/'Миология 3D'
study.mkdir(exist_ok=True)
if args.update and destination.exists():
    assert (destination/'scripts/package_site.py').is_file(), 'Destination is not the existing atlas copy'
    assert (destination/'README.md').read_text(encoding='utf-8').startswith('# Миология 3D'), 'Unexpected destination'
else:
    destination.mkdir(exist_ok=False)
relative_paths=[p for p in subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode('utf-8').split('\0') if p]
relative_paths+=['build_head/head_hi.glb','build_head/head.glb','build_head/head_q.glb','build_head/meta.json']
relative_paths += [str(p.relative_to(root)) for directory in ['stl_head','shots/head','shots/head-detail','shots/head-study','shots/head-features','shots/head-channels','shots/head-catalogues','shots/head-geometry','shots/atlas-touch','shots/skull-education'] for p in (root/directory).rglob('*') if p.is_file()]
relative_paths += [str(p.relative_to(root)) for directory in ['build_head/complete_face','build_head/complete_temporal/jobs','shots/cranial-completion','build_head/face_features','build_head/cranial_extent','build_head/temporal_channels/extent-bp','build_head/temporal_variants'] for p in (root/directory).rglob('*.png')]
relative_paths += [str(p.relative_to(root)) for directory in ['shots/skull-educational-bones','qhead_muscle_reconstructions'] for p in (root/directory).rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.jpg')]
relative_paths=list(dict.fromkeys(relative_paths))
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

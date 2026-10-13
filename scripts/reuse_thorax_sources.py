"""Reuse already obtained BodyParts3D originals before fetching missing files."""
from pathlib import Path
import shutil
from manifest_thorax import all_ids
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'stl_thorax'
out.mkdir(exist_ok=True)
count=0
for fid in set(all_ids()):
    destination=out/f'{fid}.stl'
    if destination.exists():continue
    for folder in ['stl_neck','stl_head','stl_dl','stl_leg','stl_body']:
        source=ROOT/folder/f'{fid}.stl'
        if source.exists():
            shutil.copy2(source,destination)
            count+=1
            break
print('Reused source files:',count)

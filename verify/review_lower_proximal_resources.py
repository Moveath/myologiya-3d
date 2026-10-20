"""Recheck immutable resource evidence; inspect lower-limb names, not infer mirrored bones."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]; out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
prior=ROOT/'research/evidence-runs/stage5-left-forearm-2026-10-18T19-20-46-330Z-35NAkG/left-forearm-resources.json'
old=json.loads(prior.read_text('utf8')); rows=[]
pattern=re.compile(r'24475|24478|24481|24487|(?:femur|patella|tibia|fibula)[_ -]?left|left.*(?:femur|patella|tibia|fibula)',re.I)
for r in old['resources']:
 p=ROOT/r['file']; assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],p
 rows.append(dict(file=r['file'],sha256=r['sha256'],matches=[n for n in r['names'] if pattern.search(n)]))
all_files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.venv','node_modules','.git','evidence-runs'))]
current={str(p.relative_to(ROOT)).replace('\\','/') for p in all_files if p.suffix.lower()=='.glb' or p.name.endswith('-glb.txt')}
assert current=={r['file'].replace('\\','/') for r in rows},'New resource: inspect it before accepting cached inventory'
source_files=[str(p.relative_to(ROOT)) for p in all_files if re.search(r'24475|24478|24481|24487',p.name)]
result=dict(resources=rows,matchingSourceFiles=source_files,prior=str(prior.relative_to(ROOT)),
 limits='All named resources rehashed. No matching left bone identified. Anonymous nodes and dictionary IDs do not establish anatomical identity; reconstruction is not an original.')
with (out/'resources-lower-proximal.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(resources=len(rows),matches=sum(len(r['matches']) for r in rows),matchingSourceFiles=source_files)))

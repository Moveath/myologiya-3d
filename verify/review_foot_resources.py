"""Reuse hash-matched geometry evidence; check left dictionary/source availability."""
import hashlib,json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
prior=ROOT/'research/evidence-runs/stage5-left-forearm-2026-10-18T19-20-46-330Z-35NAkG/left-forearm-resources.json'
cached=json.loads(prior.read_text(encoding='utf8'))
dictionary=[]
for line in (ROOT/'bp/all_named.tsv').read_text(encoding='utf8').splitlines():
    if '\t' not in line:continue
    code,name=line.split('\t',1)
    if (('left' in name and any(w in name for w in ('talus','calcaneus','navicular','cuboid','cuneiform','metatarsal','toe'))) or name=='sesamoid bone of left foot'):
        dictionary.append(dict(id=code,name=name))
assert len(dictionary)==27
pattern=re.compile(r'(?<!\d)(?:FMA)?(?:'+'|'.join(re.escape(d['id'].removeprefix('FMA')) for d in dictionary)+r')(?!\d)',re.I)
resources=[];source_matches=[]
for base,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in ('.git','.venv','node_modules','evidence-runs','__pycache__')]
    for f in files:
        p=Path(base)/f
        if p.suffix.lower()=='.glb' or p.name.endswith('-glb.txt'):resources.append(p)
        if pattern.search(f):source_matches.append(str(p.relative_to(ROOT)))
known={r['file'].replace('\\','/') for r in cached['resources']}
current={str(p.relative_to(ROOT)).replace('\\','/') for p in resources}
assert known <= current, 'Missing historical resource'
copies=[]
for p in resources:
    name=str(p.relative_to(ROOT)).replace('\\','/')
    if name in known:continue
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    original=next((r['file'] for r in cached['resources'] if r['sha256']==digest),None)
    assert original,('New geometry requires fresh inventory',name)
    copies.append(dict(file=name,identicalTo=original,sha256=digest))
matches=[]
for r in cached['resources']:
    assert hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
    for name in r['names']:
        if pattern.search(name) or (re.search(r'(talus|calcaneus|navicular|cuboid|cuneiform|metatarsal|toe|sesamoid)',name,re.I) and re.search(r'left',name,re.I)):
            matches.append(dict(file=r['file'],name=name))
assert not matches and not source_matches,(matches,source_matches)
result=dict(status='passed',dictionaryOnly=dictionary,namedLeftMatches=matches,matchingSourceFiles=source_matches,resourcesChecked=len(resources),additionalIdenticalCopies=copies,
    limits='Dictionary IDs are not meshes. Unidentified anonymous fragments cannot establish a complete left foot. No reflected reconstruction.')
with (out/'resource-review.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',dictionaryEntries=len(dictionary),resources=len(resources),namedMatches=matches,sourceMatches=source_matches)))

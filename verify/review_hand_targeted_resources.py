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
    if re.fullmatch(r'left (scaphoid|lunate|triquetral|pisiform|trapezium|trapezoid|capitate|hamate)',name) or re.fullmatch(r'left (first|second|third|fourth|fifth) metacarpal bone',name) or re.fullmatch(r'(proximal|middle|distal) phalanx of left (thumb|index finger|middle finger|ring finger|little finger)',name):
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
assert {str(p.relative_to(ROOT)).replace('\\','/') for p in resources}=={r['file'].replace('\\','/') for r in cached['resources']},'New resource: inspect it before reuse'
matches=[]
for r in cached['resources']:
    assert hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
    for name in r['names']:
        if pattern.search(name) or (re.search(r'(scaphoid|lunate|triquetr|pisiform|trapezium|trapezoid|capitate|hamate|metacarpal|phalanx|sesamoid)',name,re.I) and re.search(r'left',name,re.I)):
            matches.append(dict(file=r['file'],name=name))
assert not matches and not source_matches,(matches,source_matches)
geometry_file=ROOT/'research/evidence-runs/stage5-hand-2026-10-18T19-41-08-979Z-py70dn/trimesh-hand.json'
geometry=json.loads(geometry_file.read_text(encoding='utf8'))
for row in geometry['rows']:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256']
result=dict(status='passed',dictionaryOnly=dictionary,namedLeftMatches=matches,matchingSourceFiles=source_matches,
    resourcesChecked=len(resources),cachedTrimesh=str(geometry_file.relative_to(ROOT)),cachedTrimeshRows=len(geometry['rows']),
    maximumPriorDistanceMm=max(r['distanceMm'] for r in geometry['anchors']),acceptedCoordinates=0,
    limits='27 dictionary entries are identities, not meshes. Hash-matched prior 28-object/81-anchor measurement reused. Anonymous fragments remain unidentified; no claim of exhaustive biological absence.')
name=sys.argv[2] if len(sys.argv)>2 else 'resource-review.json'
assert Path(name).name==name and name.endswith('.json')
with (out/name).open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k not in ('dictionaryOnly','limits')},ensure_ascii=False))

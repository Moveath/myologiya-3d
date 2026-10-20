"""Record stage-4 inputs and coordinate provenance without modifying anatomy."""
from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage4-2026-10-16'
OUT.mkdir(exist_ok=True)
for name in ('ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'):
    target=OUT/(name+'.before')
    if not target.exists():target.write_bytes((ROOT/name).read_bytes())
text=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
cards=dict(re.findall(r'(?ms)^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)',text))
pending=[]
for key,body in cards.items():
    if 'Этап: **4**' in body and 'Статус: **проверена**' not in body:
        fields={s.split(':',1)[0].lstrip('- '):s.split(':',1)[1].strip() for s in body.splitlines() if s.startswith('- ') and ':' in s}
        pending.append(dict(id=key,title=body.strip().splitlines()[0].strip('*'),status=re.search(r'Статус: \*\*([^*]+)',body)[1],fields=fields))
(OUT/'remaining-before.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
baseline=json.loads((ROOT/'research/stage4-2026-10-15/protected-files-before.json').read_text(encoding='utf8'))
extra=list(ROOT.glob('site/*.glb'))+list(ROOT.glob('build*/**/*.glb'))+[ROOT/'tools/package.json',ROOT/'tools/package-lock.json']
for path in extra:baseline[str(path.relative_to(ROOT)).replace('\\','/')]=None
for name in baseline:
    path=ROOT/name
    baseline[name]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
target=OUT/'protected-before.json'
if not target.exists():target.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ids=['hum_collum_chirurgicum','hum_corpus','hum_facies_anterolateralis','hum_sulcus_n_radialis','rad_corpus','rad_facies_anterior','cal_sinus_tarsi']
points=[]
for filename in ('pins/ta.json','pins_leg/ta.json'):
    if not (ROOT/filename).exists():continue
    for row in json.loads((ROOT/filename).read_text(encoding='utf8')):
        if row['id'] in ids: points.append(dict(source=filename,**row))
snippets=[]
for name in ('build/landmarks.js','build/landmarks_ta.js','build/pintool.html','build_leg/landmarks_ta.js','build_leg/pintool.html'):
    lines=(ROOT/name).read_text(encoding='utf8').splitlines()
    for n,line in enumerate(lines,1):
        if any(x in line for x in ids+['surg_neck','radial_groove','rad_anterior','arm_raw.glb','toFixed(5)','hit.point.toArray()','const surgical','const ant =']):
            snippets.append(dict(file=name,line=n,text=line))
record=dict(git_present=(ROOT/'.git').exists(),raw_arm_present=(ROOT/'build/arm_raw.glb').exists(),raw_leg_default_present=(ROOT/'build_leg/arm_raw.glb').exists(),rounding_max_mm=3**.5*.005,points=points,source_lines=snippets,
note='No normal offset in surf/pick; historical GLB URL for leg can be overridden by ?f=. Saved hash/query for that historical run is unavailable.')
(OUT/'coordinate-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'remaining':[(p['id'],p['status']) for p in pending],'protected':len(baseline),'source_points':len(points)},ensure_ascii=False))


from pathlib import Path
from collections import Counter
import re,json,hashlib
from urllib.parse import unquote
root=Path.cwd()
base=root/'research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh'
bundle=root/'research/stage5-thorax-batch2-2026-10-18'
def parse(s):
 out={}
 for m in re.finditer(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)',s,re.M|re.S):
  status=re.search(r'Статус:\s*\*\*([^*]+)',m[2]);stage=re.search(r'Этап:\s*\*\*([^*]+)',m[2])
  if status:
   assert m[1].strip() not in out
   out[m[1].strip()]={'status':status[1],'stage':stage[1] if stage else None,'science':'Научная проверка: да' in m[2]}
 return out
issues=(root/'ANATOMY_ISSUES.md').read_text(encoding='utf-8')
progress=(root/'ANATOMY_PROGRESS.md').read_text(encoding='utf-8')
old_progress=(base/'before-ANATOMY_PROGRESS.md').read_text(encoding='utf-8')
old=parse((base/'before-ANATOMY_ISSUES.md').read_text(encoding='utf-8'));current=parse(issues)
assert len(old)==215 and len(current)==216
assert set(old)<=set(current) and set(current)-set(old)=={'SYS-ADDITIONAL-SEARCH'}
changed=[i for i in old if current[i]['status']!=old[i]['status']]
assert changed==['PIN-THORAX-KIND']
assert current['PIN-THORAX-KIND']['status']==current['SYS-ADDITIONAL-SEARCH']['status']=='проверена'
assert old_progress[old_progress.index('### LOG-'):].strip() in progress
counts=Counter(x['status'] for x in current.values())
assert counts=={'проверена':47,'требует проверки':81,'заблокирована':54,'открыта':34}
stage5=[sum(x['stage']=='5' and x['status']=='проверена' for x in current.values()),sum(x['stage']=='5' for x in current.values())]
assert stage5==[25,94]
science=sum(x['science'] and x['status']!='проверена' for x in current.values()); assert science==133
for issue in ['PIN-THORAX-KIND','SYS-ADDITIONAL-SEARCH']:
 line=next(x for x in issues.splitlines() if x.startswith('| ['+issue+']')); assert line.endswith('| проверена |')
e=json.loads((bundle/'evidence.json').read_text(encoding='utf-8'))
for k,v in e.items():
 if isinstance(v,str) and v.startswith('research/') and k!='registry_final': assert (root/v).is_file(),(k,v)
for k in ['data','full_ui_1280','full_ui_390','final_search_ui']:
 assert json.loads((root/e[k]).read_text(encoding='utf-8'))['status']=='passed',k
rows=json.loads((bundle/'reviewed-records.json').read_text(encoding='utf-8'))
assert len(rows)==len({p['id'] for p in rows})==294
data=json.loads((root/e['data']).read_text(encoding='utf-8'));assert data['records']==rows
report=root/'research/stage5-thorax-batch2-report-2026-10-18.md'
for text,parent in [(report.read_text(encoding='utf-8'),report.parent),(progress[progress.index('### LOG-20261018-02'):],root)]:
 for href in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in href or href.startswith('#'):continue
  path=unquote(href.split('#')[0]).strip('<>')
  assert (parent/path).exists(),path
hashes=json.loads((base/'hashes-before.json').read_text(encoding='utf-8'))
allowed={'scripts/make_pins_thorax.py','scripts/make_shared_landmarks.py','site/pins-thorax.js','site/pins-shared.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'}
protected=[]
for p,h in hashes.items():
 if p not in allowed:
  assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
  protected.append(p)
assert len(protected)==53
old_html=(base/'index-before.html').read_text(encoding='utf-8')
assert (root/'site/index.html').read_text(encoding='utf-8')==old_html.replace("q.t === 'ta' ? 'TA98' : 'мышца'","q.t === 'ta' ? 'TA98' : q.t === 'additional' ? 'ориентир' : 'мышца'")
result={'status':'passed','date':'2026-10-18','total':216,'counts':dict(counts),'verified':47,'unclosed':169,'blocked':54,'sciencePending':science,'stage5VerifiedAndTotal':stage5,'oldIdsPreserved':len(old),'oldStatusChanges':changed,'newVerified':['SYS-ADDITIONAL-SEARCH'],'historicalJournalPreserved':True,'indexedRecords':294,'protectedFilesUnchanged':protected,'localLinksExist':True,'acceptedNewCoordinates':0,'acceptedExtents':0}
with (base/'registry-final.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='protectedFilesUnchanged'},ensure_ascii=True))


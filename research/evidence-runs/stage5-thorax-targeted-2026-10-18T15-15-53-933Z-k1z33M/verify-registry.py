from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import json,re,hashlib
root=Path.cwd();out=root/'research/evidence-runs/stage5-thorax-targeted-2026-10-18T15-15-53-933Z-k1z33M'
def parse(s):
 result={}
 for m in re.finditer(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)',s,re.M|re.S):
  st=re.search(r'Статус:\s*\*\*([^*]+)',m[2]);stage=re.search(r'Этап:\s*\*\*([^*]+)',m[2])
  if st:
   assert m[1] not in result
   result[m[1]]={'status':st[1],'stage':stage[1] if stage else '', 'science':'Научная проверка: да' in m[2]}
 return result
current=(root/'ANATOMY_ISSUES.md').read_text(encoding='utf8');old=(out/'before-ANATOMY_ISSUES.md').read_text(encoding='utf8')
before,after=parse(old),parse(current);assert len(before)==216 and len(after)==217
assert set(after)-set(before)=={'GEO-THORAX-CARTILAGE-COVERAGE'}
assert all(after[i]==v for i,v in before.items())
counts=Counter(v['status'] for v in after.values());assert counts=={'проверена':47,'открыта':34,'требует проверки':81,'заблокирована':55}
science=sum(v['status']!='проверена' and v['science'] for v in after.values());assert science==134
stage=[sum(v['stage']=='5' and v['status']=='проверена' for v in after.values()),sum(v['stage']=='5' for v in after.values())];assert stage==[25,95]
p=(root/'ANATOMY_PROGRESS.md').read_text(encoding='utf8');previous=(out/'before-ANATOMY_PROGRESS.md').read_text(encoding='utf8')
assert previous[previous.index('### LOG-'):].strip() in p
evidence={'date':'2026-10-18','status':'completed_with_open_geometry_limits','scope':'targeted thorax review; no new coordinates or mesh edits',
 'current':{k:str((out/v).relative_to(root)).replace('\\','/') for k,v in {
 'node':'data-regression.json','blender':'blender-cartilage.json','python_sources':'cartilage-source-components.json','ui_1280':'ui-1280-v2.json','ui_390':'ui-390-v2.json','pubmed_search':'pubmed-search.json','pubmed_efetch':'pubmed-verified.json','crista_ids':'crista-22-decisions.json','markup_inventory':'geometry-markup-inventory.json','markup_groups':'markup-groups-corrected.json','registry':'registry-final.json'}.items()},
 'reused':{'previous_batch':'research/stage5-thorax-batch2-report-2026-10-18.md','index':'research/stage5-thorax-batch2-2026-10-18/evidence.json','trimesh_490':'research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh/trimesh-positions.json','previous_blender_27_views':'research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh/blender-ribs.json'},
 'limits':['New Blender comparison only for cartilage coverage; previous rib/point/BVH/clipping checks reused with unchanged protected code/models.',
 'UI first attempt used wrong overview location; ui-1280.json retained, final v2 passed.',
 'Persistent browser cache disabled during final checks; final current data validated in DOM.',
 'Draft markup-groups.json superseded by markup-groups-corrected.json; no data types changed.',
 'Python TA98 console: 762 terms, three previously documented differences; no new difference.',
 'PubMed abstract access only; Bookshelf reCAPTCHA and Masaryk photo index timeout not bypassed.',
 'No new or historical issue closed in this task.']
}
for k in ['node','blender','ui_1280','ui_390']:
 d=json.loads((root/evidence['current'][k]).read_text(encoding='utf8'));assert d['status']=='passed',k
for section in ['current','reused']:
 for k,v in evidence[section].items():
  if k!='registry':assert (root/v).is_file(),v
hashes=json.loads((out/'hashes-before.json').read_text(encoding='utf8'))
allowed={'scripts/thorax_terms.py','scripts/thorax_ribs_stage5.py','scripts/manifest_thorax.py','site/pins-thorax.js','site/pins-shared.js','site/data-thorax.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'}
protected=[]
for f,h in hashes.items():
 if f not in allowed:
  assert hashlib.sha256((root/f).read_bytes()).hexdigest()==h,f
  protected.append(f)
assert len(protected)==57
reg={'status':'passed','total':217,'verified':47,'unclosed':170,'counts':dict(counts),'sciencePending':science,'stage5':stage,'closedThisTask':0,'oldStatusChanges':[],'oldIdsPreserved':216,'newBlocked':['GEO-THORAX-CARTILAGE-COVERAGE'],'historicalProgressPreserved':True,'protectedFilesUnchanged':protected}
for name,obj in [('registry-final.json',reg),('evidence.json',evidence)]:
 with (out/name).open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
report=root/'research/stage5-thorax-targeted-report-2026-10-18.md'
for text,parent in [(report.read_text(encoding='utf8'),report.parent),(p[p.index('### LOG-20261018-03'):],root)]:
 for href in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in href or href.startswith('#'):continue
  assert (parent/unquote(href.split('#')[0]).strip('<>')).exists(),href
print(json.dumps({k:v for k,v in reg.items() if k not in ['counts','protectedFilesUnchanged']},ensure_ascii=True))


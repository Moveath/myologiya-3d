"""Export the addressed decisions and frozen review scope; no new anatomy inference."""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'research/stage5-skull-batch6-2026-10-16'
sys.path.insert(0, str(ROOT/'scripts'))
from head_skull_batch6 import reviewed_decisions, decision_sources
from ta98 import BONE, T

def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

script=(ROOT/'site/pins-head.js').read_text(encoding='utf-8')
head=json.loads(script.split('push(...',1)[1].rsplit(');',1)[0])
before={p['id']:p for p in read('head-baseline.json')}
decisions=reviewed_decisions(); records=[]
for p in head:
    d=decisions.get((p['b'],p['c']))
    if not d: continue
    records.append(dict(id=p['id'],bone=p['b'],code=p['c'],nameRu=p['ru'],latin=p['lat'],
        beforeDefinition=before[p['id']]['x'],definition=p['x'],kind=d['kind'],rationale=d['reason'],
        sourceGroup=d['group'],refs=p['refs'],side=p['b'].rsplit('_',1)[1],
        coordinateAcceptance=False,extentAcceptance=False))
remaining=[dict(id=p['id'],bone=p['b'],code=p['c'],nameRu=p['ru']) for p in head if p['geometryKind']=='unknown']
write('geometry-kind-review.json',dict(date='2026-10-16',records=records,
    byBone=dict(Counter(r['bone'] for r in records)),byKind=dict(Counter(r['kind'] for r in records)),
    explicit=len(head)-len(remaining),remaining=remaining,remainingTarget=[]))
targets={b for b,c in decisions}; catalogue=[]
for p in head:
    if p['b'] not in targets: continue
    assert p['c'] in BONE[p['b']]
    assert p['ru']==T[p['c']][1] and p['lat']==T[p['c']][0].split(';')[0].strip()
    catalogue.append(dict(id=p['id'],bone=p['b'],code=p['c'],ru=p['ru'],latin=p['lat'],
        definition=p['x'],kind=p['geometryKind'],
        review='current representation and catalogue' if (p['b'],p['c']) in decisions else 'previous type retained; definition/context checked',
        geometryAccepted=False))
write('catalogue-review.json',dict(records=catalogue,recordCount=len(catalogue),
    uniqueCodes=len({p['code'] for p in catalogue}),missingApplicableTA98Codes=[],
    naming='Matched existing reconciled TA98/Russian table; no new access to the 2003 Russian atlas claimed.',
    completeness='TA98 bone sections covered; not proof of exhaustive educational anatomy, accessory canals, articular facets or specimen geometry.',
    gaps=[dict(key='facial_incisive_fossa',bones=['maxilla_right','maxilla_left'],parentCode='A02.1.12.007',
               ru='Резцовая ямка передней поверхности верхней челюсти',notEquivalentTo='A02.1.00.060',coordinate=None),
          dict(key='canine_eminence',bones=['maxilla_right','maxilla_left'],parentCode='A02.1.12.007',
               ru='Клыковое возвышение',notEquivalentTo='A02.1.12.009',coordinate=None)],
    gapEvidence=['Gray/Lewis PDF p.118: anterior surface',
                 'NBK538527 Table 1: indexed text; direct CAPTCHA'],
    nextStep='Resolve separate educational entries and nomenclature mapping without false TA98 codes or provisional coordinates.'))
refs={r['id']:r for d in decisions.values() for r in decision_sources(d)}
write('source-review.json',dict(date='2026-10-16',sources=list(refs.values()),
    reusedEvidence='Existing independent pairs from head_face_evidence.py / head_terms.py retained per record, including Buchanan/Gray, dental histology and palatine spine study. Not all were reopened.',
    liveTerminology=[dict(code='A02.1.13.016',
        url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/02.1.13.016%20Entity%20TA98%20EN.htm',
        finding='Latin, bilateral/composite property and hierarchy verified; no automatic FMA -> geometryKind conversion.')],
    accessLimits=['Buchanan UNSW: 403, previous addressed evidence retained.',
        'Bookshelf NBK538527, Table 1, NBK557817 and direct PMC: CAPTCHA; indexed passages identified.',
        'IMAIOS open definitions read; cited closed atlases not claimed read.',
        'BDJ Cooper/Cascarini 2008 metadata accessible, full text paywalled; indexed sentence not sufficient to close SH-060.'],
    pubmedRecords=read('pubmed-targeted.json')['records']+read('pubmed-hiatus.json')['records'],
    api='First sandbox TLS request failed; approved official EFetch succeeded: 4 records, 2 requests. Metadata alone is not anatomical evidence.',
    independence='Review and included primary study are not independent observations. No population measurements transferred to GLB.',
    newGeometryAccepted=False))
b=read('blender-review.json')
write('geometry-observations.json',dict(tool='Blender MCP',recordCount=84,
    viewedImages=[i['file'] for i in b['images']],
    maxNearestSurfaceMm=max(d for r in b['records'] for d in r['nearestSurfaceMm'].values()),
    transformation='Three (x,y,z) -> Blender (x,-z,y)',
    visible='Крупные пластинки, пазушная полость изолированных maxillae, зубные лунки и разделители, стык нёбных частей.',
    unconfirmed=['Весь подглазничный и резцовые каналы, ветвление и центры просветов',
        'Полные края большого/малых нёбных отверстий и непрерывность каналов',
        'Резцовый шов, мелкие нёбные ости/борозды, все участки гребней',
        'Точные линии нёбных швов и границы поверхностей отростков',
        'Две локальные записи не доказывают отдельные общие носовые ости'],
    note='Красные сферы показывают прежние координаты; радиус 0.8 мм только графический. Сглаженный рельеф не принят как полный extent.',
    coordinateAcceptance=False,extentAcceptance=False,
    sourceUnchanged=b['sourceUnchanged'],originalScenePreserved=b['originalScenePreserved']))
print(json.dumps(dict(records=len(records),catalogue=len(catalogue),kinds=dict(Counter(r['kind'] for r in records)))))

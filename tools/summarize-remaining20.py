"""Per-owner decisions without changing admission or collapsing issues into bones."""
import json
from pathlib import Path
import sys

run=Path(sys.argv[1]).resolve()
read=lambda f:json.loads((run/f).read_text(encoding='utf8'))
atlas=read('atlas-before.json');meta=read('comparison-metadata.json');depth=read('comparison-depth.json')['rows']
bykey={}
for r in depth:
    key=tuple(sorted((r['a'],r['b'])))
    bykey[key]=max(bykey.get(key,0),r['maxSamplePenetrationMM'])
decisions=[]
for id,b in atlas['bones'].items():
    if not b.get('noModel'):continue
    issue=('GEO-HAND-MCP1-R' if id=='sesamoid_mcp1_radial_right' else
           'GEO-HAND-MCP1-U' if id=='sesamoid_mcp1_ulnar_right' else
           'GEO-HAND-LEFT-MODELS' if id.startswith(('metacarpal','sesamoid_mcp1')) else 'GEO-LOWER-LEFT-FOOT')
    variants=[]
    for prefix in ['native','mirror']:
        key=prefix+'__'+id
        if key not in meta:continue
        pairs=[dict(other=pair[1] if pair[0]==key else pair[0],maxSampleDepthMM=d) for pair,d in bykey.items() if key in pair]
        pairs.sort(key=lambda p:-p['maxSampleDepthMM'])
        variants.append(dict(id=key,source=meta[key]['source'],crossingNeighbors=pairs))
    sesamoid=id.startswith('sesamoid_mcp1')
    required=('Идентифицированные лучевая/локтевая сетки MCP I с разрешением на коммерческое распространение производных, масштабом, стороной и данными регистрации к той же кисти; либо лицензированная CT/MRI-сегментация и независимая приёмка.' if sesamoid else
              'Согласованные маски/контуры сопряжённых поверхностей, поза и исходная сегментация одного образца; независимая оценка отмеченных пересечений и обоснованное исправление. Полная приёмка отдельно от учебного допуска.')
    decisions.append(dict(id=id,ru=b['ru'],issue=issue,status='заблокирована',noModel=True,
                          admitted=False,variants=variants,required=required,stage='6 / 8',
                          reason='Нет принятой отдельной формы и регистрации; морфометрия не задаёт готовую сетку.' if sesamoid else
                          'Варианты численно целы, но сопряжение не принято. Меньшая выборочная глубина не является самостоятельным допуском.'))
assert len(decisions)==20
with (run/'owner-decisions.json').open('x',encoding='utf8') as f:json.dump(decisions,f,ensure_ascii=False,indent=2)
lines=['# Поимённый остаток: 20 владельцев','',
 'Два варианта одной кости не присутствуют одновременно. Все глубины — выборочные диагностические значения, не физиологический порог. Полные пары, версии и критерии: `owner-decisions.json`.','',
 '| ID | Существующий ID задачи | Решение |', '|---|---|---|']
for d in decisions:
    reason=('Лицензированный и идентифицированный сесамоид не принят; см. источники OSF/Hegdé/Zenodo в итоговом отчёте.' if not d['variants'] else
            'Оставить оба варианта тестовыми; требуется приёмка сопряжённых поверхностей. Рабочие соседи сохранены.')
    lines.append(f"| `{d['id']}` | {d['issue']} | {reason} |")
with (run/'owner-decisions.md').open('x',encoding='utf8') as f:f.write('\n'.join(lines)+'\n')
ui=[]
for width,rev in [(1280,'v3'),(390,'v4')]:
    for region in ['arm','leg']:
        phases=['setup','working']+(['capture'] if width==390 else [])+(['blocked-0','blocked-4'] if region=='arm' else ['blocked-0','blocked-4','blocked-8','blocked-12'])
        for phase in phases:
            name=f'ui-{rev}-{width}-{region}-{phase}-result.json'
            if width==1280 and region=='arm' and phase=='setup':name='ui-1280-arm-setup-result-v2.json'
            r=read(name)
            if 'content' in r:r=json.loads(r['content'][0]['text'].split('### Result\n')[1].split('\n### Ran')[0])
            assert r['status']=='passed',name
            ui.append(dict(file=name,checks=len(r['checks']),width=width,region=region,phase=phase))
summary=dict(owners=20,meshOwners=16,sesamoidsWithoutAcceptedSource=4,newAdmissions=0,noModel=20,
             browserPhases=len(ui),browserChecks=sum(x['checks'] for x in ui),browser=ui,
             blenderViews=sum(len(read(f)['views']) for f in ['blender-hand.json','blender-foot-joints.json','blender-toe-joints.json']),
             closedIssues=0,fullAnatomicalAcceptance=False)
with (run/'review-summary.json').open('x',encoding='utf8') as f:json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in summary.items() if k!='browser'}))

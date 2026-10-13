"""Publish the finite educational inventory without upgrading anatomical evidence."""
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
def read(name):
    return json.loads((SITE/name).read_text(encoding='utf8'))
def array(value):
    return value if isinstance(value, list) else [value] if value else []
def unique_refs(refs):
    seen = set(); result = []
    for ref in refs:
        key = (ref['url'], ref.get('locator'))
        if key not in seen:
            result.append(ref); seen.add(key)
    return result
def license_text(value):
    if isinstance(value, dict):
        return ' · '.join(str(value[k]) for k in ('name','attribution','url') if value.get(k))
    return value
def model(source, file):
    return dict(id=source['id'], ru=source['ru'], file=file,
        nodes=source.get('nodeNames',source.get('nodes',[])), contextNodes=source.get('contextNodes',[]),
        labels=source.get('labels',[]), camera=source.get('camera',{}), known=array(source.get('known',source.get('demonstrates'))),
        limitations=array(source.get('modelLimit'))+array(source.get('unknown'))+array(source.get('limitations')),
        method=source.get('method'), refs=source.get('refs',[]), license=license_text(source.get('license')))

def export():
    bones=read('skull-educational-bones.json')
    muscles=read('skull-muscle-reconstructions.json')
    attachments=read('skull-attachment-education.json')
    ossicles=read('skull-openear-landmarks.json')
    indexed={m['id']:model(m,bones['modelFile']) for m in bones['models']}
    entries=[]
    for r in bones['records']:
        links=[]
        if r['kind']=='whole':
            if r.get('sourceLaunch'):
                links.append(dict(label='Исходный учебный вид ↗',href='skull-detail.html?'+urlencode(dict(mode=r['sourceLaunch'].get('mode','z'),code=r['c'],**{'from':'whole'}))))
        else:
            for i,a in enumerate(r.get('sourceViews',[])):
                if a.get('viewer',{}).get('mode') not in (None,'main'):
                    links.append(dict(label=a['source']+' · исходная модель ↗',href='skull-detail.html?'+urlencode(dict(mode=a['viewer']['mode'],bone=r['bone'],code=r['c'],assessment=i,**{'from':'geometry'}))))
            links.append(dict(label='Исходная кость и маркер ↗',href='./?'+urlencode(dict(study='landmark',value=r['pinId']))+'#head'))
        if r['kind']=='variant':
            links.append(dict(label='Опубликованный пример варианта ↗',href='skull-study.html?'+urlencode({'code':r['c']})))
        entries.append(dict(id=r['id'],category={'whole':'whole','variant':'variants'}.get(r['kind'],'bones'),ru=r['ru'],lat=r['lat'],code=r['c'],subtitle=r.get('boneRu','Череп как целое'),status=r['status'],
            known=array(r['known']),unknown=array(r['unknown']),limitations=array(r['modelLimit']),guidance=array(r['learningGuidance']),refs=r['refs'],models=[indexed[k] for k in r['modelIds']],links=links,
            originalLocalization=r.get('originalLocalization'),originalExtentStatus=r.get('originalExtentStatus')))
    side={'right':'правая сторона','left':'левая сторона','unpaired':'непарная'}
    for r in muscles['entries']:
        key=r['muscle']+(':'+r['part'] if r.get('part') else '')
        entries.append(dict(id='muscle:'+key,category='muscles',ru=r['ru'],lat=r['lat'],code=r['ta98'],subtitle='Часть мышцы' if r.get('part') else 'Мышца',status=r['status'],
            known=array(r.get('summary'))+array(r.get('demonstrates')),unknown=array(r.get('unknown')),limitations=array(r.get('limitations')),guidance=array(r.get('learningGuidance')) or ['Сопоставь схему с описанием начала и прикрепления. Условную форму нельзя использовать для измерений или определения границ на исходном черепе.'],refs=r['refs'],
            models=[model(r,muscles['asset'])] if r.get('nodes') else [],links=[dict(label='Начало и прикрепление ↗',href='skull-education.html?'+urlencode({'id':'attachment:'+key})),dict(label='Карточка мышцы в атласе ↗',href='./?'+urlencode(dict(study='muscle',value=key))+'#head')]))
    for r in attachments['items']:
        entries.append(dict(id='attachment:'+r['id'],category='attachments',ru=r['ru'],lat=r['lat'],code=r['ta98'],subtitle=side[r['side']],status='documented_attachment',
            known=[r['origin']['known'],r['insertion']['known']],unknown=[r['origin']['unknown'],r['insertion']['unknown']],limitations=r['limitations']+[v for v in [r.get('note'),r.get('partNote')] if v],
            guidance=[r['origin']['learningGuidance'],r['insertion']['learningGuidance']],refs=unique_refs(r['origin']['refs']+r['insertion']['refs']),models=[],attachment=dict(origin=r['origin'],insertion=r['insertion']),
            links=[dict(label='Карточка мышцы в атласе ↗',href='./?'+urlencode(dict(study='muscle',value=r['id']))+'#head')]))
    for r in ossicles['markers']:
        entries.append(dict(id='ossicle:'+r['c'],category='ossicles',ru=r['ru'],lat=r['lat'],code=r['c'],subtitle='OpenEar ZETA · правая сторона',status='source_model',known=[r['x']],
            unknown=[r['modelNote']],limitations=['Маркер выделяет указанный участок исходной косточки. Наличие точки не доказывает сохранность всей микрогеометрии. Левый экземпляр не получен и не имитируется отражением.'],
            guidance=['Открой собственный ракурс OpenEar и сопоставь образование с соседними частями косточки. Учитывай ограничения конкретного ориентира.'],refs=r['refs'],models=[],links=[dict(label='Косточка и ориентир OpenEar ↗',href='skull-detail.html?'+urlencode(dict(mode='openear',marker=r['id'])))]))
    assert len(entries)==728 and len({r['id'] for r in entries})==728
    expected={'bones':507,'variants':14,'whole':97,'muscles':19,'attachments':78,'ossicles':13}
    assert Counter(r['category'] for r in entries)==expected
    for r in entries:
        assert all(r[k] for k in ('ru','lat','code','known','unknown','limitations','guidance')),r['id']
        assert len({ref['url'] for ref in r['refs']})>=2,r['id']
        assert all(ref.get('locator') and ref.get('title') and ref['url'].startswith('https://') for ref in r['refs']),r['id']
        for m in r['models']:
            assert m['nodes'] and (SITE/m['file']).is_file(),r['id']
            assert len({ref['url'] for ref in m['refs']})>=2,m['id']
    files=['skull-educational-bones.json','skull-educational-bones.glb','skull-muscle-reconstructions.json','skull-muscle-reconstructions.glb','skull-attachment-education.json','skull-openear-landmarks.json']
    data=dict(version=1,policy='Исходная геометрия, отдельно обозначенная учебная схема или явное объяснение ограничений; решение для каждой записи согласовано пользователем 13 октября 2026.',
        title='Череп: модели и объяснения',entries=entries,counts=dict(total=len(entries),categories=expected,status=dict(Counter(r['status'] for r in entries)),unique3DDiagrams=len({m['id'] for r in entries for m in r['models']}),recordsWithDiagrams=sum(bool(r['models']) for r in entries),attachmentFields=156),
        educationalDispositionComplete=True,completeSkullGeometry=False,independentAnatomistReview=False,physicalDeviceTests=False,
        sourceFiles={f:hashlib.sha256((SITE/f).read_bytes()).hexdigest() for f in files})
    (SITE/'skull-education.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    report={k:v for k,v in data.items() if k!='entries'}
    report['meaning']='Каждая запись получила материал и объяснение в принятом учебном объёме. Это не процент точной анатомической геометрии и не заключение специалиста.'
    report['entryIds']=[r['id'] for r in entries]
    (ROOT/'research/skull-educational-release.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data['counts'],ensure_ascii=False))

if __name__=='__main__':export()

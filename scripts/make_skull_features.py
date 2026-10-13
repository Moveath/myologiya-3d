"""Merge independently reviewed native-model evidence without transferring coordinates."""
from pathlib import Path
import json
import re
from collections import defaultdict
from ta98 import T
ROOT=Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf8'))

def build():
    native={'z':read('research/face-completion-z-markers.json'),
            'openear':read('pins_head/openear-native.json')['markers'],'microct':[]}
    for region in ('face','cranial','temporal'):
        path=ROOT/f'pins_head/{region}-native-features.json'
        if not path.exists():
            raise ValueError(f'Missing reviewed native features: {path.name}')
        data=json.loads(path.read_text(encoding='utf8'))
        for m in data['markers']:
            mode=m.get('mode') or data.get('mode')
            assert mode in native, (m['id'],mode)
            native[mode].append(m)
    features={}
    for mode,markers in native.items():
        assert len({m['id'] for m in markers})==len(markers), mode
        for m in markers:
            assert all(k in m for k in ('id','b','c','p','n','ru','lat','view','refs','modelNote')),m
            assert len(m['refs'])>=2 and m.get('evidence'),m['id']
            assert len(m['p'])==len(m['n'])==3,m['id']
            m['mode']=mode
            m.setdefault('specimen',{'z':'Z-Anatomy','microct':'Halle · микро-КТ','openear':'OpenEar · ZETA'}[mode])
            if mode=='openear' and m['specimen']=='ZETA':
                m['specimen']='OpenEar ZETA'
            entry=features.setdefault(m['c'],{'c':m['c'],'ru':re.sub(r' · (справа|слева)$','',m['ru']),'lat':m['lat'],'views':[]})
            entry['views'].append({k:m[k] for k in ('mode','id','ru','specimen','modelNote')})
    variant_rows=read('site/skull-study-variants.json')
    for e in read('site/skull-variant-examples.json')['examples']:
        term=next(p for p in variant_rows if p['c']==e['c'])
        entry=features.setdefault(e['c'],{'c':e['c'],'ru':term['ru'],'lat':term['lat'],'views':[]})
        entry['example']=e
    for mode, filename in [('channels', 'skull-temporal-channels.json'), ('cranial_channels', 'skull-cranial-channels.json')]:
        if not (ROOT/'site'/filename).is_file():
            continue
        model=read('site/'+filename)
        for row in model['structures']:
            code=row['ta98']
            assert code in T, code
            assert len(row['refs'])>=2 and row['modelNote']
            entry=features.setdefault(code, {'c':code, 'ru':T[code][1], 'lat':T[code][0], 'views':[]})
            entry.setdefault('channel_views', []).append({'mode':mode, 'id':row['id'], 'ru':row['ru'],
                 'specimen':model['source'], 'modelNote':row['modelNote'], 'scope':row['scope'],
                 'completeFeatureGeometry':row['completeFeatureGeometry']})
    out={'complete_geometry_claim':False,'markers':native,
         'counts':{mode:len(markers) for mode,markers in native.items()}}
    (ROOT/'site/skull-native-features.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    catalogue={'complete_geometry_claim':False,'features':sorted(features.values(),key=lambda r:r['c'])}
    (ROOT/'site/skull-feature-catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'site/skull-evidence-index.js').write_text('window.ATLAS.headEvidence = '+json.dumps(list(features),ensure_ascii=False)+';\n',encoding='utf8')
    print('Native-model markers:',out['counts'],'; detailed terms:',len(features))

if __name__=='__main__':build()

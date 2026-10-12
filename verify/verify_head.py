"""Check actual GLB coverage, surface records, references and card integrity."""
from pathlib import Path
from collections import Counter
import sys,json,base64,struct,math

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import manifest_head as manifest
from ta98 import BONE,T
from head_muscles import MUSCLE_TEMPLATES,EVIDENCE

muscle_ref={r['code']:r['lat'] for r in json.loads((root/'verify/ifaa-head-muscles.json').read_text(encoding='utf-8'))}
# Printed TA98 corrections, documented in the relevant cards.
assert muscle_ref.pop('A04.1.02.012')=='musculus depressor septi nasi'
muscle_ref['A04.1.03.012']='musculus depressor septi nasi'
assert muscle_ref['A04.1.03.032']=='musculus levator nasolabialis'
muscle_ref['A04.1.03.032']='musculus levator labii superioris alaeque nasi'
for muscle in MUSCLE_TEMPLATES.values():
    assert muscle['lat'].replace('m. ','musculus ')==muscle_ref[muscle['code']]
    for part in muscle.get('parts',{}).values():
        assert part['lat']==muscle_ref[part['code']],part['code']

def glb_names(path):
    data=base64.b64decode(path.read_bytes())
    magic,version,length=struct.unpack_from('<III',data)
    assert magic==0x46546c67 and version==2 and length==len(data)
    size,kind=struct.unpack_from('<II',data,12)
    assert kind==0x4e4f534a
    gltf=json.loads(data[20:20+size])
    return {n.get('name','').rstrip('|') for n in gltf['nodes']}

expected={'b|'+b for b in manifest.BONES}|{'o|epicranial_aponeurosis'}
expected|={'m|'+key+('|'+part if part else '') for key,parts in manifest.MUSCLES.items() for _,part in parts}
for filename in ['head-glb.txt','head-q-glb.txt']:
    names=glb_names(root/'site'/filename)
    assert expected <= names, (filename,sorted(expected-names))
    assert len([n for n in names if n.startswith('c|')])==len(manifest.CONTEXT)

raw=(root/'site/pins-head.js').read_text(encoding='utf-8')
pins=json.loads(raw.split('push(...',1)[1].rsplit(');',1)[0])
assert len({p['id'] for p in pins})==len(pins)
for bone in manifest.BONES:
    subset=[p for p in pins if p['b']==bone]
    assert Counter(p['c'] for p in subset)==Counter(BONE[bone]),bone
    for p in subset:
        assert p['lat']==T[p['c']][0].split(';')[0].strip()
        assert len(p['refs'])>=2
        if 'p' in p:
            assert len(p['p'])==len(p['n'])==3
            assert all(math.isfinite(n) for n in p['p']+p['n'])
            assert -.1 < p['p'][0] < .1 and 1.4 < p['p'][1] < 1.7 and -.02 < p['p'][2] < .22
        else: assert 'не подтверждено' in p['modelNote']
        for mu,role,*part in p['m']:
            base=mu.removesuffix('_right').removesuffix('_left')
            assert base in MUSCLE_TEMPLATES and role in ['o','i']
            if part: assert part[0] in MUSCLE_TEMPLATES[base].get('parts',{})

for key,entry in EVIDENCE.items():
    for f,refs in entry['fields'].items():
        if f not in entry.get('unconfirmed',[]): assert len(set(refs))>=2,(key,f)
assert len(manifest.BONES)==22 and len(manifest.MUSCLES)==43
assert len(pins)==521
print(f'Head integrity passed: 22 bones, 43 modeled muscle instances, {len(pins)} TA98 records, {sum("p" in p for p in pins)} positions')

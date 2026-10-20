"""Build the small reviewed shared-landmark catalogue; never modifies geometry."""
import json
import hashlib
from pathlib import Path
from shared_landmarks import instances, existing_patches
from skull_targeted_review import new_shared, review_shared
from neck_stage5_review import shared_records as neck_shared_records
from thorax_stage5_review import shared_records as thorax_shared_records
from thorax_ribs_stage5 import shared_records as rib_shared_records
from lumbar_stage5_review import shared_records as lumbar_shared_records
from pelvis_stage5_review import shared_records as pelvis_shared_records

ROOT = Path(__file__).resolve().parents[1]


def reviewed_records():
    terms=json.loads((ROOT/'research/skull-whole-scope-audit.json').read_text(encoding='utf-8'))['rows']
    terminology = {r['code']:r['latin'] for r in terms}
    records = list(instances(terminology)) + list(new_shared(terminology)) + list(neck_shared_records()) + list(thorax_shared_records()) + list(rib_shared_records()) + list(lumbar_shared_records()) + list(pelvis_shared_records())
    review = json.loads((ROOT / 'research/shared-landmarks-geometry.json').read_text(encoding='utf-8'))
    source = ROOT / review['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == review['sourceSha256'], 'Repeat the Blender review after geometry changes'
    raw = (ROOT / 'site/pins-head.js').read_text(encoding='utf-8')
    old_pins = {p['id']: p for p in json.loads(raw.split('push(...', 1)[1].rsplit(');', 1)[0])}
    assert len({p['id'] for p in records}) == len(records)
    for pin in records:
        # Old skull-wide cards predate explicit representation kinds. Keep the
        # uncertainty visible; anatomy must be reviewed before assigning a type.
        if pin['id'].startswith('shared_skull_') and not pin.get('geometryKind'):
            pin['geometryKind'] = 'unknown'
        review_shared(pin)
        assert len({r['bone'] for r in pin['relations']}) == len(pin['relations']) >= 2
        assert pin['b'] in {r['bone'] for r in pin['relations']}
        assert len({r['authorGroup'] for r in pin['refs']}) >= 2
        candidate = next((c for c in review['candidates'] if c.get('instanceId') == pin['id']), None)
        if candidate and candidate.get('acceptedScope') == 'temporal_boundary_point':
            assert candidate['bone'] == pin['b']
            original = old_pins[candidate['sourcePin']]
            assert original['p'] == candidate['p'] and original['n'] == candidate['n'], 'Repeat review after the source pin changes'
            assert candidate['distanceMm'][pin['b']] < 0.01
            pin['anchors'] = [dict(sourcePin=original['id'], bone=pin['b'], scope='temporal_boundary_point',
                                   model=review['source'], modelSha256=review['sourceSha256'],
                                   p=original['p'], n=original['n'], review='research/shared-landmarks-geometry.json')]
            # Compatibility with the existing renderer; no averaging or mirroring.
            pin.update(p=original['p'], n=original['n'], loc='projection', view=[0, 1, -0.8])
            pin['modelNote'] = ('Маркер обозначает один участок височного края яремного отверстия: использована отдельно проверенная '
                                'точка яремной вырезки этой стороны. Это не центр просвета, не весь контур отверстия и не отдельная '
                                'модель канала. Полная форма и размеры отверстия здесь не подтверждены.')
    return records


def all_linked_records():
    """Metadata for both newly created instances and in-place legacy migrations."""
    old={}
    for name in ['pins-head.js','pins-leg.js']:
        raw=(ROOT/'site'/name).read_text(encoding='utf-8')
        body=raw.split('push(...',1)[1] if 'push(...' in raw else raw.split('.concat(',1)[1]
        old.update({p['id']:p for p in json.loads(body.rsplit(');',1)[0])})
    return reviewed_records()+[{**old[p['id']],**p} for p in existing_patches()]


def build():
    records = reviewed_records()
    patches = list(existing_patches())
    measurements=json.loads((ROOT/'verify/shared-expansion-geometry.json').read_text(encoding='utf-8'))
    decisions=json.loads((ROOT/'research/shared-expansion-geometry-review.json').read_text(encoding='utf-8'))
    old_by_id={p['id']:p for p in all_linked_records()}
    assert len({p['id'] for p in patches}) == len(patches)
    for patch in patches:
        assert len({r['bone'] for r in patch['relations']}) >= 2
        assert len({r['authorGroup'] for r in patch['refs']}) >= 2
        measured=next(p for p in measurements['points'] if p['id']==patch['id'])
        decision=next(p for p in decisions['points'] if p['id']==patch['id'])
        assert hashlib.sha256((ROOT/measured['model']).read_bytes()).hexdigest()==measured['sha256']
        assert old_by_id[patch['id']]['p']==measured['p'] and old_by_id[patch['id']]['n']==measured['n']
        assert (patch.get('anchorStatus')=='unverified') == (decision['status']=='unverified')
        patch['geometryReview']='research/shared-expansion-geometry-review.json'
        if decision['status']=='representative_component':
            patch['anchors']=[dict(sourcePin=patch['id'],bone=patch['catalogueBones'][0],scope=decision['scope'],
                                   model=measured['model'],modelSha256=measured['sha256'],p=measured['p'],n=measured['n'],
                                   review='research/shared-expansion-geometry-review.json')]
    target = ROOT / 'site/pins-shared.js'
    packed=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':'))
    target.write_text('/* Generated by scripts/make_shared_landmarks.py; load after all regional pins. */\n(() => {\n'
                      'const pins=window.ATLAS.pins;\n'
                      'for(const patch of '+packed(patches)+') {\n'
                      ' const matches=pins.filter(p=>p.id===patch.id);\n'
                      ' if(matches.length!==1) throw new Error("Shared landmark target: "+patch.id);\n'
                      ' const pin=matches[0], refs=[...(pin.refs||[])];\n'
                      ' for(const ref of patch.refs) if(!refs.some(r=>r.id===ref.id)) refs.push(ref);\n'
                      ' Object.assign(pin,patch,{refs});\n'
                      '}\npins.push(...'+packed(records)+');\n})();\n',encoding='utf-8')
    print(f'{len(records)} new instances; {len(patches)} existing instances linked; no geometry changed')


if __name__ == '__main__':
    build()

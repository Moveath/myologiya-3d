"""Check resumability invariants without running geometry or altering evidence."""
from pathlib import Path
import argparse, copy, importlib.util, json

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recovery_state',ROOT/'tools/geometry-recovery-state.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def check():
    state=json.loads((ROOT/'research/geometry-recovery-state.json').read_text(encoding='utf8'))
    baseline=module.validate(state)
    rejected=[]
    mutations={
        'duplicate_key':lambda s:s['items'][1].update(key=s['items'][0]['key']),
        'identity_drift':lambda s:s['items'][0].update(catalogueId='unrelated_bone'),
        'unknown_issue':lambda s:s['items'][0].update(issueIds=['NONEXISTENT-RECOVERY-ISSUE']),
        'missing_evidence':lambda s:s['items'][0]['evidence'].append('research/not-a-real-recovery-result.json'),
        'duplicate_method':lambda s:s['items'][0]['methods'].append(copy.deepcopy(s['items'][0]['methods'][0])),
        'false_admission':lambda s:s['items'][0].update(admitted=True),
        'false_coverage':lambda s:s['items'][0].update(currentNoModel=False),
        'stale_counts':lambda s:s['currentCounts'].update(bones=0),
    }
    for name,mutate in mutations.items():
        candidate=copy.deepcopy(state);mutate(candidate)
        try:module.validate(candidate)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(f'Invalid checkpoint was accepted: {name}')
    # Save rejects a bad candidate before touching the immutable revision or active file.
    before=(ROOT/'research/geometry-recovery-state.json').read_bytes()
    candidate=copy.deepcopy(state);mutations['false_admission'](candidate)
    try:module.save(candidate,ROOT/'research',dict(id='must-not-be-written'))
    except AssertionError:pass
    else:raise AssertionError('Invalid state was saved')
    assert (ROOT/'research/geometry-recovery-state.json').read_bytes()==before
    return dict(status='passed',baseline=baseline,rejectedInvalidStates=rejected,
                invalidSavePreservesCheckpoint=True,productionModified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
    result=check()
    if args.output:
        with Path(args.output).open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))

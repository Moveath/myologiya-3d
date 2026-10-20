"""Lightweight consistency check; does not infer whether an issue is resolved."""
from pathlib import Path
from collections import Counter, defaultdict
import json,re

ROOT=Path(__file__).resolve().parents[1]

def check():
    issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf-8-sig')
    progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf-8-sig')
    cards=list(re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',issues,re.M|re.S))
    ids=[m[1] for m in cards]
    assert len(ids)==len(set(ids)), 'Duplicate issue IDs'
    counts=Counter();stages=defaultdict(lambda:[0,0]);science=0
    for match in cards:
        ident,body=match[1],match[2]
        stage=int(re.search(r'Этап: \*\*(\d+)\*\*',body)[1])
        status=re.search(r'Статус: \*\*([^*]+)\*\*',body)[1]
        counts[status]+=1;stages[stage][1]+=1;stages[stage][0]+=status=='проверена'
        science+=status!='проверена' and 'Научная проверка: да.' in body
        line=next((line for line in issues.splitlines() if line.startswith(f'| [{ident}](')),None)
        assert line is not None, f'Missing index: {ident}'
        fields=[x.strip() for x in line.split('|')[1:-1]]
        assert fields[-1]==status and int(fields[-3])==stage, f'Index mismatch: {ident}'
        assert '- Решение и критерий закрытия:' in body and '- Доказательства исправления и тесты:' in body, ident
    summary=issues.split('## Сводка\n',1)[1].split('## Указатель задач',1)[0]
    for status in ('открыта','в работе','требует проверки','заблокирована','исправлена','проверена'):
        assert f'| {status} | {counts[status]} |' in summary, f'Summary mismatch: {status}'
    current=progress.split('## Сводка учёта',1)[1].split('## Записи журнала',1)[0]
    assert f'**{len(ids)} записей: {counts["проверена"]} проверено, {len(ids)-counts["проверена"]} не закрыто;' in current, 'Progress summary is stale'
    for stage,(done,total) in stages.items():
        line=next(x for x in progress.splitlines() if x.startswith(f'| {stage} |'))
        assert f'{done} проверено / {total} всего' in line, f'Stage {stage} count mismatch'
    return {'status':'passed','issues':len(ids),'status_counts':dict(counts),'scientific_pending':science,'stages':dict(stages)}

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))

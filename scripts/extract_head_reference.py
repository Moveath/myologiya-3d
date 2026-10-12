"""Extract the public IFAA reference independently of the atlas's term table."""
from pathlib import Path
import html
import re
import json

root = Path(__file__).resolve().parents[1]
def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()
for name in ['ifaa-head-bones', 'ifaa-head-muscles']:
    source = (root / 'research/cache' / (name + '.html')).read_text(encoding='utf-8-sig')
    rows = []
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', source, re.I | re.S):
        cells = [clean(cell) for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.I | re.S)]
        if len(cells) >= 4 and re.fullmatch(r'\d{2}\.\d\.\d{2}\.\d{3}', cells[1]):
            latin = re.sub(r'\s*\d+ children$', '', cells[2]).strip()
            rows.append({'code': 'A' + cells[1], 'lat': latin, 'en': cells[3]})
    (root / 'verify' / (name + '.json')).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print(name, len(rows))
    for row in rows:
        print(row['code'], row['lat'])

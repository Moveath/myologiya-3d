"""Nomenclature fixture of the abdominal muscles from an independent IFAA download (TA98 04.5.01).

The page is parsed as downloaded (UTF-16); raw Latin terms are preserved. The printed Russian edition
(Kolesnikov 2003) has no Cyrillic text layer for these pages, so its equivalents were read from page
images rendered at 150-170 dpi (pp. 48-49), kept with the evidence run, and are listed here as data.
Usage: python scripts/make_ifaa_abdomen_fixture.py IFAA_PAGE.htm
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/04.5.01%20TA98%20EN.htm'
PRINTED_RU = {
    'A04.5.01.001': 'Прямая мышца живота', 'A04.5.01.002': 'Сухожильные перемычки',
    'A04.5.01.003': 'Влагалище прямой мышцы живота', 'A04.5.01.006': 'Дугообразная линия',
    'A04.5.01.007': 'Пирамидальная мышца', 'A04.5.01.008': 'Наружная косая мышца живота',
    'A04.5.01.009': 'Паховая связка; паховая дуга', 'A04.5.01.017': 'Внутренняя косая мышца живота',
    'A04.5.01.018': 'Мышца, поднимающая яичко', 'A04.5.01.019': 'Поперечная мышца живота',
    'A04.5.01.020': 'Паховый серп; соединительное сухожилие', 'A04.5.01.022': 'Белая линия',
    'A04.5.01.027': 'Квадратная мышца поясницы',
}
raw = Path(sys.argv[1]).read_bytes()
text = raw.decode('utf-16')
cells = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).replace('\xa0', ' ').strip()
         for c in re.findall(r'<td[^>]*>(.*?)</td>', text, re.S | re.I)]
cells = [re.sub(r'\s+', ' ', c) for c in cells]
terms = {}
for i, c in enumerate(cells):
    if re.fullmatch(r'A04\.5\.01\.\d{3}', c):
        terms[c] = dict(lat=cells[i + 1], en=cells[i + 2], url=URL)
assert len(terms) == 27, len(terms)
for code, ru in PRINTED_RU.items():
    terms[code]['ruPrinted'] = ru
out = dict(checked='2026-10-26', source='Independent IFAA download; raw Latin terms preserved',
           license='IFAA website CC BY-SA 4.0; nomenclature factual identifiers',
           pages=[dict(url=URL, sha256=hashlib.sha256(raw).hexdigest(), entries=len(terms))],
           printedRussian=dict(title='Международная анатомическая терминология (рус. экв.), под ред. Л. Л. Колесникова, 2003',
                               pages='48–49', method='Read from rendered page images; the PDF text layer has no Cyrillic for these rows.'),
           terms=terms)
data = (json.dumps(out, ensure_ascii=False, indent=2) + '\n').encode('utf8')
target = ROOT / 'verify/ifaa-abdomen-muscles.json'
if target.exists():
    assert target.read_bytes() == data, 'Refusing to overwrite a different fixture'
else:
    target.write_bytes(data)
print(len(terms), 'terms')

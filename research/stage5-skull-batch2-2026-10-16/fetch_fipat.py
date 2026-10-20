"""Read-only retrieval of explicit TA98 entity properties, not geometry acceptance."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote
import json, re

OUT = Path(__file__).with_name('fipat-occipital.json')
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, data):
        if data.strip(): self.parts.append(data.strip())

def fetch(number):
    code=f'A02.1.04.{number:03}'
    url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/'+quote(code[1:]+' Entity TA98 EN.htm')
    result=dict(code=code,url=url,geometryAccepted=False)
    try:
        with urlopen(Request(url,headers={'User-Agent':'AnatomySourceReview/1.0'}),timeout=20) as r: data=r.read().decode('utf-8',errors='replace')
        parser=Text();parser.feed(data); text=' '.join(parser.parts)
        assert code in text and 'TA98 Entity Page' in text
        result.update(status='read',bilateral='This entity has left and right instances' in text,
                      entityType=('material' if 'Type of entity Material entity' in text else 'immaterial' if 'Type of entity Immaterial entity' in text else 'not_extracted'),
                      taxonomy=text.split('FMA Taxonomy',1)[-1].split('Date:',1)[0][:1200],
                      english=text.split('TA98 English equivalent',1)[-1].split('Properties',1)[0].split('TA98 Hierarchy',1)[0][:180])
    except Exception as e: result.update(status='unavailable',error=type(e).__name__+': '+str(e)[:180])
    return result

if __name__=='__main__':
    assert not OUT.exists(),'Do not overwrite previous evidence'
    with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(fetch,range(2,38)))
    OUT.write_text(json.dumps(dict(date='2026-10-16',scope='TA98 entity properties only; nomenclature is not an independent topographic source',rows=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(read=sum(r['status']=='read' for r in rows),unavailable=sum(r['status']!='read' for r in rows))))

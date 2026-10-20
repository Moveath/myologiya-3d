"""Fetch addressed public texts, never overwrite prior evidence."""
from pathlib import Path
from urllib.request import urlopen, Request
from html.parser import HTMLParser
import json, xml.etree.ElementTree as ET, time
OUT=Path(__file__).resolve().parents[1]/'research/stage5-skull-targeted-2026-10-17'
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        if tag in ('p','h1','h2','h3','h4','li','br'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:return r.read()
url="https://embryology.med.unsw.edu.au/embryology/index.php?title=Book_-_Buchanan%27s_Manual_of_Anatomy_including_Embryology_5"
try:
    data=get(url).decode('utf-8');p=Text();p.feed(data)
    with (OUT/'buchanan-text.txt').open('x',encoding='utf-8') as f:f.write('URL: '+url+'\n'+''.join(p.parts))
    print('Buchanan text saved',len(data))
except Exception as e:print('Buchanan fetch failed:',type(e).__name__,str(e)[:180])
time.sleep(.45)
url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=37106571,26339819,40603468&retmode=xml'
data=ET.fromstring(get(url));records=[]
for a in data.findall('PubmedArticle'):
    records.append(dict(pmid=a.findtext('.//PMID'),abstract=[''.join(e.itertext()) for e in a.findall('.//AbstractText')]))
with (OUT/'pubmed-notch-abstracts.json').open('x',encoding='utf-8') as f:json.dump(dict(api=url,records=records),f,ensure_ascii=False,indent=2)
print('Official EFetch abstracts:',len(records))

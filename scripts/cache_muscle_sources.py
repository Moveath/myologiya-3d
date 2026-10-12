"""Download reference text for editorial review; cache is never published."""
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'research/cache'
INDEX = 'https://www.meddean.luc.edu/lumen/meded/grossanatomy/dissector/mml/headneck.htm'
names = ['auricularis','buccinator','corrugator supercilii','depressor anguli oris',
         'depressor labii inferioris','frontalis','lateral pterygoid','levator anguli oris',
         'levator labii superioris','masseter','medial pterygoid','mentalis','nasalis',
         'orbicularis oculi','orbicularis oris','procerus','risorius','temporalis',
         'temporoparietalis','zygomaticus major','zygomaticus minor']

def get(url):
    r = requests.get(url, timeout=50)
    r.raise_for_status()
    return r

soup = BeautifulSoup(get(INDEX).content, 'html.parser')
sources = {}
for a in soup.find_all('a', href=True):
    label = a.get_text(' ',strip=True).lower()
    if any(n in label for n in names):
        url = urljoin(INDEX,a['href'])
        sources['lumen-'+url.split('/')[-1].replace('.htm','')] = url
slugs = ['occipitofrontalis','temporoparietalis','orbicularis-oculi','corrugator-supercilii',
         'depressor-supercilii','auricularis-anterior','auricularis-superior','auricularis-posterior',
         'orbicularis-oris','depressor-anguli-oris','transversus-menti','risorius','zygomaticus-major',
         'zygomaticus-minor','levator-labii-superioris','levator-labii-superioris-alaeque-nasi',
         'depressor-labii-inferioris','levator-anguli-oris','buccinator','mentalis','nasalis',
         'depressor-septi-nasi','procerus','masseter','temporalis','medial-pterygoid','lateral-pterygoid']
for slug in slugs:
    sources['tma-'+slug] = f'https://teachmeanatomy.info/encyclopaedia/{slug[0]}/{slug}/'
    if slug not in ('transversus-menti','depressor-supercilii','auricularis-anterior','auricularis-superior','auricularis-posterior','temporoparietalis'):
        sources['kenhub-'+slug] = f'https://www.kenhub.com/en/library/anatomy/{slug}-muscle'
sources['kenhub-face'] = 'https://www.kenhub.com/en/library/anatomy/the-facial-muscles'
sources['kenhub-temporoparietalis'] = 'https://www.kenhub.com/de/library/anatomie/musculus-temporoparietalis'

def fetch(item):
    key,url=item
    try:
        target=CACHE/(key+'.html')
        if not target.exists(): target.write_bytes(get(url).content)
        soup=BeautifulSoup(target.read_bytes(),'html.parser')
        for node in soup(['script','style','nav','footer','header']): node.decompose()
        main=soup.find('main') or soup
        (CACHE/(key+'.txt')).write_text(main.get_text(' ',strip=True),encoding='utf-8')
        return key,{'url':url,'status':'readable'}
    except Exception as exc: return key,{'url':url,'status':str(exc)}

with ThreadPoolExecutor(max_workers=8) as pool:
    results=dict(pool.map(fetch,sources.items()))
(CACHE/'muscle-source-index.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for key,value in results.items(): print(key,value['status'],flush=True)

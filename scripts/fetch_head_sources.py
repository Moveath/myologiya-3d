"""Cache public reference pages for reproducible editorial review (not site assets)."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import json

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache'
CACHE.mkdir(parents=True, exist_ok=True)
SOURCES = {
    'ifaa-head-bones': 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH402%20A2F%20EN.htm',
    'ifaa-head-muscles': 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH1673%20A2F%20EN.htm',
    'ifaa-skull': 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH305%20A2F%20EN.htm',
    'tma-mastication': 'https://teachmeanatomy.info/head/muscles/mastication/',
    'tma-face': 'https://teachmeanatomy.info/head/muscles/facial-expression/',
    'ttuhsc-head-muscles': 'https://anatomy.ttuhscep.edu/anatomytables/muscles_head.html',
    'ttuhsc-head-arteries': 'https://anatomy.ttuhscep.edu/anatomytables/arteries_head_neck.html',
    'gray-muscles': 'https://en.wikipedia.org/wiki/List_of_skeletal_muscles_of_the_human_body',
    'openstax-skull': 'https://openstax.org/books/anatomy-and-physiology-2e/pages/7-2-the-skull',
}
def fetch(item):
    key, url = item
    path = CACHE / (key + '.html')
    if path.exists(): return key + ': cached'
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Myologiya3D educational source review'})
        with urllib.request.urlopen(request, timeout=45) as response:
            path.write_bytes(response.read())
        return key + ': downloaded'
    except Exception as error:
        return key + ': ' + str(error)
if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(fetch, SOURCES.items()): print(result, flush=True)

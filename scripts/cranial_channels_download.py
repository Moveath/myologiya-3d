"""Get the openly licensed original Halle CT for source-mask cross-checking."""
from pathlib import Path
import requests,hashlib,json,time,concurrent.futures,math
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'research/cache/skull-microct'
record=json.loads((CACHE/'record.json').read_text(encoding='utf-8'))
row=next(f for f in record['files'] if f['key']=='halle_skull.nrrd')
dest=CACHE/row['key'];partial=dest.with_suffix('.partial')
expected=row['checksum'].split(':',1)[1]
def digest(p):
 h=hashlib.md5()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
if dest.exists():
 assert dest.stat().st_size==row['size'] and digest(dest)==expected
 print('Original CT verified');raise SystemExit
parts=CACHE/'halle-ct-parts';parts.mkdir(exist_ok=True)
chunk=32*1024*1024
def fetch(number):
 start=number*chunk;end=min(row['size'],start+chunk)-1;p=parts/f'{number:03d}.part'
 if p.exists() and p.stat().st_size==end-start+1:return p
 response=requests.get('https://zenodo.org/records/6108435/files/halle_skull.nrrd?download=1',headers={'Range':f'bytes={start}-{end}'},stream=True,timeout=(30,120));response.raise_for_status()
 assert response.status_code==206 and response.headers['Content-Range']==f'bytes {start}-{end}/{row["size"]}'
 with p.open('wb') as f:
  for block in response.iter_content(4*1024*1024):f.write(block)
 assert p.stat().st_size==end-start+1
 print('Verified byte range',number,start,end,flush=True);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 paths=list(pool.map(fetch,range(math.ceil(row['size']/chunk))))
h=hashlib.md5();count=0
with partial.open('wb') as f:
 for p in paths:
  with p.open('rb') as src:
   while b:=src.read(8*1024*1024):f.write(b);h.update(b);count+=len(b)
assert count==row['size'] and h.hexdigest()==expected,(count,h.hexdigest())
partial.replace(dest)
print('Original CT downloaded and MD5 verified',flush=True)

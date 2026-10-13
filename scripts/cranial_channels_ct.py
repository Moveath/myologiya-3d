"""Stream a native CT ROI. During download, previews remain unverified."""
from cranial_channels_inspect import ROOT,OUT,LO,HI,SP
from pathlib import Path
import gzip,io,time,json
import numpy as np
CACHE=ROOT/'research/cache/skull-microct';SIZE=2833296569;CHUNK=32*1024*1024
class Parts:
 def __init__(self,pos):self.pos=pos
 def read(self,n=-1):
  if n<0:n=SIZE-self.pos
  n=min(n,SIZE-self.pos);out=[]
  while n:
   number=self.pos//CHUNK;offset=self.pos%CHUNK;p=CACHE/'halle-ct-parts'/f'{number:03d}.part';expected=min(CHUNK,SIZE-number*CHUNK)
   warned=False
   while not p.exists() or p.stat().st_size!=expected:
    if not warned:print('Waiting for CT byte range',number,flush=True);warned=True
    time.sleep(2)
   size=min(n,expected-offset)
   with p.open('rb') as f:f.seek(offset);data=f.read(size)
   assert len(data)==size
   self.pos+=size;n-=size;out.append(data)
  return b''.join(out)
 def tell(self):return self.pos
def ct():
 target=OUT/'base-ct.npy'
 if target.exists():return np.load(target,mmap_mode='r')
 src=CACHE/'halle_skull.nrrd';headfile=src if src.exists() else CACHE/'halle-ct-parts/000.part'
 with headfile.open('rb') as f:
  header=[]
  while (line:=f.readline()).strip():header.append(line.decode('ascii').strip())
  offset=f.tell()
 assert 'type: int16' in header and 'sizes: 1150 1700 1400' in header
 start=np.rint(LO[[0,2,1]]/SP).astype(int);end=np.rint(HI[[0,2,1]]/SP).astype(int)
 shape=tuple(map(int,(end-start)[[2,1,0]]));partial=OUT/'base-ct.partial.npy'
 result=np.lib.format.open_memmap(partial,mode='w+',dtype=np.int16,shape=shape)
 f=src.open('rb') if src.exists() else Parts(offset)
 if src.exists():f.seek(offset)
 g=gzip.GzipFile(fileobj=f)
 for k in range(end[2]):
  raw=g.read(1150*1700*2);assert len(raw)==1150*1700*2
  if k>=start[2]:result[k-start[2]]=np.frombuffer(raw,dtype='<i2').reshape(1700,1150)[start[1]:end[1],start[0]:end[0]]
  if k%100==0:print('CT ROI slice',k,'/',end[2],flush=True)
 result.flush();del result;partial.replace(target)
 (OUT/'base-ct-provenance.json').write_text(json.dumps({'source':'https://zenodo.org/records/6108435','sourceFile':'halle_skull.nrrd','expectedMD5':'2b46ca394084ab84af20bc267114e75f','requiresWholeFileChecksumVerification':True,'spacing_mm':.125,'bounds_m':[LO.tolist(),HI.tolist()],'arrayAxes':'y,z,x = source k,j,i','processing':'Original int16 density data; crop only; no interpolation.'},indent=2))
 return np.load(target,mmap_mode='r')
if __name__=='__main__':ct();print('CT ROI available. Verify complete-source MD5 before publication.',flush=True)

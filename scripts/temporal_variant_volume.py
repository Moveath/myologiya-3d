"""Lossless native Halle crop including both mastoid regions, kept local only."""
from temporal_variant_inspect import ROOT,OUT
import gzip,json,hashlib
import numpy as np
LO=np.array([0,35,30.]);HI=np.array([143.75,110,130]);SP=.125

def extract(kind):
    name='halle_skull.nrrd' if kind=='ct' else 'halle_skull_segmented.nrrd'
    path=ROOT/'research/cache/skull-microct'/name
    digest='2b46ca394084ab84af20bc267114e75f' if kind=='ct' else '7ae22945a353069bdb695b63fa2f20bd'
    target=OUT/('mastoid-'+kind+'.npy')
    if target.exists():return
    actual=hashlib.md5()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(32*1024*1024),b''):actual.update(block)
    assert actual.hexdigest()==digest
    start=np.rint(LO[[0,2,1]]/SP).astype(int);end=np.rint(HI[[0,2,1]]/SP).astype(int)
    shape=tuple(map(int,(end-start)[[2,1,0]]));partial=target.with_suffix('.partial.npy')
    dst=np.lib.format.open_memmap(partial,mode='w+',dtype=np.int16 if kind=='ct' else np.uint8,shape=shape)
    with path.open('rb') as f:
        while f.readline().strip():pass
        g=gzip.GzipFile(fileobj=f)
        for k in range(end[2]):
            raw=g.read(1150*1700*2);assert len(raw)==1150*1700*2
            if k>=start[2]:dst[k-start[2]]=np.frombuffer(raw,dtype='<i2').reshape(1700,1150)[start[1]:end[1],start[0]:end[0]]
            if k%100==0:print(kind,k,flush=True)
    dst.flush();del dst;partial.replace(target)
    (OUT/('mastoid-'+kind+'-provenance.json')).write_text(json.dumps({'source':str(path.relative_to(ROOT)),'md5':digest,'md5_verified':True,
       'bounds_mm':[LO.tolist(),HI.tolist()],'source_step_mm':SP,'array_axes':'y,z,x = original k,j,i',
       'processing':'Native crop only. No interpolation. Binary source mask cast to uint8 without value change.'},indent=2),encoding='utf-8')

if __name__=='__main__':
    extract('ct');extract('mask')

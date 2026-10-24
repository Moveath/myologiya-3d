"""Bounded, resumable extraction of original BP3D 3.0 OBJ files (no publishing)."""
import argparse,hashlib,importlib.util,json,pathlib,zipfile,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
URL='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip'
def main():
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('ids',nargs='+');a=p.parse_args()
    run=ROOT/a.run; cache=ROOT/'research/cache/cardiovascular-bp3d-3.0';cache.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('rangezip',ROOT/'tools/inspect-stage6-sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    pending=[x for x in a.ids if not (run/(x+'-source.json')).exists()]
    if not pending:return
    class CurlZip(m.RemoteZip):
        def read(self,size=-1):
            size=min(self.size-self.pos,size if size>=0 else self.size)
            if not size:return b''
            if self.used+size>60000000:raise TimeoutError('60 MB range budget')
            start=self.pos
            result=subprocess.run(['curl.exe','--fail','--silent','--show-error','--max-time','50','--range',f'{start}-{start+size-1}',self.url],capture_output=True,timeout=55,check=True).stdout
            if len(result)!=size:raise ValueError('Server ignored byte range')
            self.used+=size;self.pos+=size;return result
    source=CurlZip(URL,budget=60000000)
    with zipfile.ZipFile(source) as z:
        for fma in pending:
            entry='BodyParts3D_3.0_obj_95/'+fma+'.obj'
            if entry not in z.namelist():
                print(fma,'absent',flush=True);continue
            data=z.read(entry);target=cache/(fma+'.obj')
            if target.exists():assert target.read_bytes()==data,'Source changed'
            else:
                with target.open('xb') as f:f.write(data)
            record=dict(fma=fma,url=URL,version='3.0',entry=entry,file=target.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),crc=z.getinfo(entry).CRC,author='Database Center for Life Science (DBCLS)',license='CC BY-SA 2.1 Japan')
            with (run/(fma+'-source.json')).open('x',encoding='utf8')as f:json.dump(record,f,indent=2)
            print(fma,len(data),flush=True)
if __name__=='__main__':main()

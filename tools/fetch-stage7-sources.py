"""Bounded official archive extraction; originals are immutable research inputs."""
import hashlib,json,pathlib,sys,zipfile
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('rangezip',pathlib.Path(__file__).with_name('inspect-stage6-sources.py'))
module=module_from_spec(spec);spec.loader.exec_module(module)
run=pathlib.Path(sys.argv[1]);cache=pathlib.Path('research/cache/stage7-sources');cache.mkdir(exist_ok=True,parents=True)
url='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip'
source=module.RemoteZip(url,budget=8_000_000)
with zipfile.ZipFile(source) as archive:
 for fma in ['FMA45856','FMA45857','FMA71309','FMA71442','FMA71443']:
  entry='BodyParts3D_3.0_obj_95/'+fma+'.obj';target=cache/(fma+'.obj')
  if target.exists():raise FileExistsError(target)
  data=archive.read(entry)
  with target.open('xb')as f:f.write(data)
  record=dict(fma=fma,url=url,entry=entry,file=target.as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),crc=archive.getinfo(entry).CRC)
  with (run/(fma+'-source.json')).open('x',encoding='utf8')as f:json.dump(record,f,indent=2)
  print(fma,len(data),flush=True)
print('Range bytes',source.used)

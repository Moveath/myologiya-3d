import runpy,zipfile,pathlib,json,hashlib,sys
RemoteZip=runpy.run_path('tools/inspect-stage6-sources.py')['RemoteZip']
run=pathlib.Path(__file__).parent
cache=pathlib.Path('research/cache/stage6-sources')
ids={'femur_left': 'FMA24475', 'patella_left': 'FMA24487', 'tibia_left': 'FMA24478', 'fibula_left': 'FMA24481', 'hip_bone_left': 'FMA16587', 'talus_left': 'FMA24483'}
url='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip'
remote=RemoteZip(url); rows=[]
with zipfile.ZipFile(remote) as archive:
 for bone,fma in ids.items():
  target=cache/(fma+'.obj')
  entry,=[i for i in archive.infolist() if pathlib.PurePosixPath(i.filename).name==fma+'.obj']
  existed=target.exists()
  if existed:
   data=target.read_bytes()
   import zlib
   assert zlib.crc32(data)==entry.CRC
  else:
   data=archive.read(entry)
   with target.open('xb') as f:f.write(data)
  rows.append(dict(id=bone,sourceId=fma,entry=entry.filename,crc=entry.CRC,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),reused=existed,purpose='target' if bone in list(ids) else 'neighbour reference only'))
with (run/'source-extraction.json').open('x',encoding='utf8') as f:json.dump(dict(url=url,rows=rows,rangeBytes=remote.used),f,indent=2)
print(json.dumps(dict(sources=len(rows),reused=sum(r['reused'] for r in rows),rangeBytes=remote.used)))

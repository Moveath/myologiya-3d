import runpy,zipfile,pathlib,json,hashlib,sys
RemoteZip=runpy.run_path('tools/inspect-stage6-sources.py')['RemoteZip']
run=pathlib.Path(__file__).parent
cache=pathlib.Path('research/cache/stage6-sources')
ids={'phalanx_prox_1_left': 'FMA65470', 'phalanx_prox_2_left': 'FMA71915', 'phalanx_prox_3_left': 'FMA71908', 'phalanx_prox_4_left': 'FMA71916', 'phalanx_prox_5_left': 'FMA66791', 'phalanx_mid_2_left': 'FMA23938', 'phalanx_mid_3_left': 'FMA23940', 'phalanx_mid_4_left': 'FMA23942', 'phalanx_mid_5_left': 'FMA23944', 'phalanx_dist_1_left': 'FMA23951', 'phalanx_dist_2_left': 'FMA23953', 'phalanx_dist_3_left': 'FMA23955', 'phalanx_dist_4_left': 'FMA23957', 'phalanx_dist_5_left': 'FMA23959'}
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

"""Read at most64KiB of a pinned public NRRD; do not download the image volume."""
import pathlib,urllib.request,json,hashlib,time
RUN=pathlib.Path(__file__).resolve().parent
SHA='7d520ffe410b3f79d82991b8368b2d51844feb80'
remote='visible_human_3d_models/CT/Segmentation/01_Male/FOOT_LEFT.seg.nrrd'
url=f'https://huggingface.co/datasets/BoneHub/visible-human-3d-models/resolve/{SHA}/{remote}'
record={'sourceUrl':url,'commit':SHA,'request':'Range bytes=0-65535','limitBytes':65536,'sourceLicense':'CC BY4.0 (pinned README in earlier run)','retrievedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'fullVolumeDownloaded':False}
try:
    req=urllib.request.Request(url,headers={'Range':'bytes=0-65535'})
    with urllib.request.urlopen(req,timeout=20) as response:
        data=response.read(65536)
        record.update(httpStatus=response.status,contentRange=response.headers.get('Content-Range'),contentLength=response.headers.get('Content-Length'),bytesRead=len(data))
    limit=data.find(b'\n\n')
    if limit<0:raise RuntimeError('NRRD header terminator not found within64KiB')
    header=data[:limit+2].decode('ascii')
    if not header.startswith('NRRD'):raise RuntimeError('not NRRD header')
    (RUN/'bonehub-male-foot-header.nrrd.txt').open('x',encoding='ascii').write(header)
    record.update(status='header_retrieved',headerBytes=limit+2,headerSha256=hashlib.sha256(data[:limit+2]).hexdigest(),metadata={})
    for line in header.splitlines():
        if line.startswith('#') or ':' not in line:continue
        k,v=line.split(':',1);record['metadata'][k]=v.lstrip('= ').strip()
except Exception as exc:record.update(status='failed',error=str(exc))
(RUN/'foot-header-retrieval.json').open('x',encoding='utf8').write(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in record.items() if k!='metadata'},ensure_ascii=False))

# Public repository file metadata only, no CT payload.
api=f'https://huggingface.co/api/datasets/BoneHub/visible-human-3d-models/tree/{SHA}/visible_human_3d_models/CT/Image'
try:
    with urllib.request.urlopen(api,timeout=20) as response:
        data=response.read(200000)
    entries=json.loads(data)
    (RUN/'bonehub-ct-file-metadata.json').open('x',encoding='utf8').write(json.dumps({'url':api,'files':entries,'CTDownloaded':False},indent=2))
    print([(x.get('path'),x.get('size')) for x in entries])
except Exception as exc:
    (RUN/'bonehub-ct-file-metadata-error.json').open('x',encoding='utf8').write(json.dumps({'url':api,'error':str(exc)}))
    print('CT metadata fetch failed',str(exc))

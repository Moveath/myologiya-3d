"""Local recovery snapshot before writes; does not stage, commit, or publish.

Backs up the complete current site and editable source/catalogue documents.
Research caches and historical evidence stay in place and are never modified.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main(run):
    out=ROOT/'.codex/checkpoints'/run.name;out.mkdir(parents=True,exist_ok=False)
    files=set()
    for directory in ['site','scripts','verify','.agents/skills']:
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__'not in p.parts)
    files.update(p for p in (ROOT/'tools').glob('*')if p.is_file())
    files.update(ROOT.glob('*.md'));files.update((ROOT/'research').glob('*.md'));files.update((ROOT/'research').glob('*.json'))
    paths=sorted(files);manifest=[]
    zip_path=out/'site-and-sources.zip'
    with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1)as archive:
        for p in paths:
            raw=p.read_bytes();name=p.relative_to(ROOT).as_posix()
            manifest.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            archive.writestr(name,raw)
    with zipfile.ZipFile(zip_path)as archive:assert archive.testzip() is None
    git=subprocess.check_output(['git','status','--porcelain=v1','-z'],cwd=ROOT)
    (out/'git-status.z').write_bytes(git)
    record=dict(scope='Complete site plus editable code and root research documents; original source caches and historical evidence left untouched',
                files=len(manifest),uncompressedBytes=sum(r['bytes']for r in manifest),
                archive=zip_path.relative_to(ROOT).as_posix(),archiveBytes=zip_path.stat().st_size,
                archiveSHA256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),
                gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
                gitIndexModified=False,filesManifest=manifest,
                restore='Extract selected files into a separate review directory, compare hashes, then restore only explicitly required paths. No automatic rollback.')
    with (out/'manifest.json').open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2)
    with (run/'checkpoint.json').open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in record.items()if k!='filesManifest'}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');args=p.parse_args();main((ROOT/args.run).resolve())

"""Loopback-only test build. Does not expose research, recipes, or user files."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import unquote,urlsplit
import argparse
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trial-dir',required=True);p.add_argument('--port',type=int,default=8785);a=p.parse_args()
    trial=(ROOT/a.trial_dir).resolve()
    if not trial.is_relative_to(ROOT/'build_stage7') or not trial.is_dir():p.error('Need existing build_stage7 directory')
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self,path):
            url=unquote(urlsplit(path).path)
            if url=='/trial.html':base=trial;rel='trial.html'
            elif url.startswith('/trial/'):base=trial;rel=url[len('/trial/'):]
            else:base=ROOT/'site';rel=url.lstrip('/')
            target=(base/rel).resolve()
            return str(target) if target.is_relative_to(base) else str(base/'__invalid__')
    ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()

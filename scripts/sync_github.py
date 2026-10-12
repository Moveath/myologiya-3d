"""Publish a reviewed directory via GitHub's Git Data API when Git transport is unavailable.

Only staged/tracked index contents are published. Credentials remain in memory.
Existing branch content is inspected; concurrent remote changes abort the update.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Moveath/myologiya-3d'
branch, directory = sys.argv[1], Path(sys.argv[2]).resolve()
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
result = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                        text=True, capture_output=True, env=env, check=True)
credentials = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
headers = {'Authorization': 'Bearer ' + credentials['password'], 'Accept': 'application/vnd.github+json',
           'User-Agent': 'Myologiya3D', 'Content-Type': 'application/json'}
def api(path, method='GET', body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(4):
        try:
            request = urllib.request.Request('https://api.github.com/repos/' + REPO + path,
                                             headers=headers, method=method, data=data)
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == 3: raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3: raise RuntimeError('GitHub API connection failed') from None
        time.sleep(2)

def current():
    try:
        return api('/git/ref/heads/' + branch)['object']['sha']
    except urllib.error.HTTPError as error:
        if error.code in (404, 409): return None
        raise

previous = current()
if previous is None and branch == 'main':
    # Git Data API cannot create blobs in an entirely empty repository.
    api('/contents/README.md', 'PUT', {'message': 'Initialize anatomy atlas',
        'content': base64.b64encode((directory / 'README.md').read_bytes()).decode(), 'branch': 'main'})
    previous = current()
old = api('/git/trees/' + previous + '?recursive=1') if previous else {'tree': []}
known = {item['path']: item['sha'] for item in old['tree'] if item['type'] == 'blob'}
paths = subprocess.check_output(['git', '-C', str(directory), 'ls-files', '-z']).decode('utf-8').split('\0')
paths = [path for path in paths if path]
assert paths and all((directory / path).is_file() for path in paths)
assert subprocess.run(['git','-C',str(directory),'diff','--quiet']).returncode == 0, 'Stage reviewed changes before publishing'

def upload(path):
    data = subprocess.check_output(['git','-C',str(directory),'show',':'+path])
    sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if known.get(path) != sha:
        blob = api('/git/blobs', 'POST', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
        assert sha == blob['sha'], path
        print('Uploaded', path, flush=True)
    return {'path': path, 'mode': '100644', 'type': 'blob', 'sha': sha}

with ThreadPoolExecutor(max_workers=4) as pool:
    entries = list(pool.map(upload, paths))
tree = api('/git/trees', 'POST', {'tree': entries})
if previous and tree['sha'] == old['sha']:
    print('Already current', branch, previous)
    sys.exit(0)
commit = api('/git/commits', 'POST', {'message': 'Publish anatomy atlas' if branch == 'gh-pages' else 'Update anatomy atlas sources',
              'tree': tree['sha'], 'parents': [previous] if previous else []})
assert current() == previous, 'Remote branch changed during publication; retry after review'
if previous:
    api('/git/refs/heads/' + branch, 'PATCH', {'sha': commit['sha'], 'force': False})
else:
    api('/git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': commit['sha']})
assert current() == commit['sha']
print('Published', branch, commit['sha'], flush=True)

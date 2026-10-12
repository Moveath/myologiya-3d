"""Create/configure the atlas repository using Git's existing credential helper.

Credentials stay in process memory; they are never written or printed.
Usage: python scripts/github_repository.py create|pages|status
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
import time

repo = 'Moveath/myologiya-3d'
environment = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
credential = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                            text=True, capture_output=True, env=environment, check=True)
values = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
headers = {'Authorization': 'Bearer ' + values['password'], 'Accept': 'application/vnd.github+json',
           'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Myologiya3D'}
def api(path, method='GET', body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(3):
        try:
            request = urllib.request.Request('https://api.github.com' + path, headers=headers, data=data, method=method)
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError:
            raise
        except urllib.error.URLError:
            if attempt == 2: raise RuntimeError('GitHub API connection failed') from None
            time.sleep(2)

action = sys.argv[1]
if action == 'create':
    try:
        result = api('/repos/' + repo)
    except urllib.error.HTTPError as error:
        if error.code != 404: raise
        result = api('/user/repos', 'POST', {'name': repo.split('/')[1],
                     'description': 'Учебный 3D-атлас анатомии: кости, мышцы и ориентиры TA98', 'private': False})
    print(result['html_url'])
elif action == 'pages':
    try:
        result = api('/repos/' + repo + '/pages')
    except urllib.error.HTTPError as error:
        if error.code != 404: raise
        result = api('/repos/' + repo + '/pages', 'POST', {'build_type': 'legacy', 'source': {'branch': 'gh-pages', 'path': '/'}})
    print(json.dumps({k: result.get(k) for k in ('html_url', 'status', 'source')}))
elif action == 'status':
    result = api('/repos/' + repo + '/pages/builds/latest')
    print(json.dumps({k: result.get(k) for k in ('status', 'error', 'commit')}))

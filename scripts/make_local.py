"""site/index.html is written as a page fragment (the Claude artifact host adds <!doctype>, <html>, <body>).
For any other host (local server, GitHub Pages, Netlify) wrap it into a full document.

usage: python3 scripts/make_local.py site/index.html site/local.html
"""
import sys
import re
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def versioned_asset(url, root):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path.endswith('.js'):
        return url
    file = (root / parts.path).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        return url
    # Content, not wall-clock time: identical builds retain the same cache keys.
    digest = hashlib.sha256(file.read_bytes()).hexdigest()[:16]
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != 'v']
    return urlunsplit(('', '', parts.path, urlencode(query + [('v', digest)]), parts.fragment))

def make_document(src):
    root = src.resolve().parent
    body = src.read_text(encoding='utf-8')
    body = re.sub(r'<title>.*?</title>\s*', '', body, count=1, flags=re.S)
    body = re.sub(r'(<script\b[^>]*\bsrc=[\"\'])([^\"\']+)([\"\'])',
                  lambda m: m[1] + versioned_asset(m[2], root) + m[3], body)
    body = re.sub(r'(\bfrom\s+[\"\'])(\./[^\"\']+\.js(?:\?[^\"\']*)?)([\"\'])',
                  lambda m: m[1] + versioned_asset(m[2], root) + m[3], body)
    # Nested project imports (e.g. visibility -> model-sides) need fresh URLs too.
    # Three.js and BVH vendor imports stay pinned to their existing versions.
    def import_map(match):
        data = json.loads(match[2])
        imports = data.setdefault('imports', {})
        for file in sorted(root.glob('atlas-*.js')):
            key = './' + file.name
            imports[key] = versioned_asset(key, root)
        return match[1] + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + match[3]
    body = re.sub(r'(<script\s+type="importmap">)(.*?)(</script>)', import_map, body, flags=re.S)
    head = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<title>Миология 3D — учебный атлас анатомии</title>'
        '<meta name="description" content="Учебный 3D-атлас анатомии: кости, мышцы и образования по TA98. Русские и латинские названия.">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>')
    return head + body + '</body></html>\n'

if __name__ == '__main__':
    src, dst = map(Path, sys.argv[1:3])
    dst.write_text(make_document(src), encoding='utf-8', newline='\n')
    print('written', dst)

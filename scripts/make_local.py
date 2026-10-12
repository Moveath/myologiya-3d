"""site/index.html is written as a page fragment (the Claude artifact host adds <!doctype>, <html>, <body>).
For any other host (local server, GitHub Pages, Netlify) wrap it into a full document.

usage: python3 scripts/make_local.py site/index.html site/local.html
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
body = open(src, encoding="utf-8").read()
head = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<title>Миология 3D — учебный атлас анатомии</title>'
        '<meta name="description" content="Учебный 3D-атлас анатомии: кости, мышцы и образования по TA98. Русские и латинские названия.">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>')
open(dst, "w", encoding="utf-8").write(head + body + "</body></html>\n")
print("written", dst)

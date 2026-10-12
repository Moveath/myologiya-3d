"""Persistent Playwright driver: keeps one page open and runs JS jobs dropped into a queue folder.

usage: python3 driver.py <serve_dir> <page> <queue_dir> <port>
  job:    <queue_dir>/<name>.job   (JS expression; may be an async arrow function call)
  result: <queue_dir>/<name>.out   (JSON) and <queue_dir>/<name>.png (screenshot of #wrap if present)
"""
import sys, os, time, json, glob, threading, http.server, functools
from playwright.sync_api import sync_playwright

serve_dir, page_name, qdir, port = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
NM = os.environ.get("NM", "")
os.makedirs(qdir, exist_ok=True)
for f in glob.glob(os.path.join(qdir, "*")):
    os.remove(f)

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)
Handler.log_message = lambda *a: None
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()


def route_cdn(route):
    path = route.request.url.split("/npm/", 1)[1]
    pkg, rest = path.split("/", 1)
    fp = os.path.join(NM, pkg.rsplit("@", 1)[0], rest)
    if os.path.exists(fp):
        route.fulfill(path=fp, content_type="application/javascript")
    else:
        route.abort()


log = open(os.path.join(qdir, "_console.log"), "a")
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 820, "height": 820})
    pg.on("console", lambda m: (log.write(f"{m.type}: {m.text}\n"), log.flush()))
    pg.on("pageerror", lambda e: (log.write(f"pageerror: {e}\n"), log.flush()))
    pg.route("https://cdn.jsdelivr.net/npm/**", route_cdn)
    pg.goto(f"http://127.0.0.1:{port}/{page_name}")
    pg.wait_for_function("window.__ready === true", timeout=180000)
    open(os.path.join(qdir, "_READY"), "w").write("1")
    while True:
        jobs = sorted(glob.glob(os.path.join(qdir, "*.job")), key=os.path.getmtime)
        if os.path.exists(os.path.join(qdir, "_STOP")):
            break
        for j in jobs:
            name = os.path.basename(j)[:-4]
            code = open(j).read()
            os.remove(j)
            try:
                if code.strip() == "RELOAD":
                    pg.reload(); pg.wait_for_function("window.__ready === true", timeout=180000); r = "reloaded"
                else:
                    r = pg.evaluate(code)
                res = json.dumps(r, ensure_ascii=False)
            except Exception as e:
                res = "ERROR " + str(e)[:2000]
            try:
                el = pg.query_selector("#wrap")
                (el or pg).screenshot(path=os.path.join(qdir, name + ".png"))
            except Exception as e:
                pass
            open(os.path.join(qdir, name + ".out"), "w").write(res)
        time.sleep(0.05)
    b.close()
httpd.shutdown()

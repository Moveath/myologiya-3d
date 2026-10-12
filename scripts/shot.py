"""Screenshot a local page with Playwright; jsDelivr three.js requests are served from node_modules.

usage: python3 shot.py <serve_dir> <page> <out_prefix> [w h] [js_to_run_before_shot ...]
"""
import sys, threading, http.server, functools, os, time
from playwright.sync_api import sync_playwright

serve_dir, page_name, out = sys.argv[1], sys.argv[2], sys.argv[3]
w = int(sys.argv[4]) if len(sys.argv) > 4 else 1280
h = int(sys.argv[5]) if len(sys.argv) > 5 else 800
steps = sys.argv[6:]
NM = os.environ.get("NM", "")

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)
Handler.log_message = lambda *a: None
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()


def route_cdn(route):
    url = route.request.url
    # https://cdn.jsdelivr.net/npm/three@0.170.0/<path>
    path = url.split("/npm/", 1)[1]
    pkg, rest = path.split("/", 1)
    name = pkg.rsplit("@", 1)[0]
    fp = os.path.join(NM, name, rest)
    if os.path.exists(fp):
        route.fulfill(path=fp, content_type="application/javascript")
    else:
        print("MISSING", fp)
        route.abort()


with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                        color_scheme=os.environ.get("SCHEME", "light"),
                        has_touch=os.environ.get("TOUCH") == "1")
    pg = ctx.new_page()
    pg.on("console", lambda m: print("console:", m.type, m.text))
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.route("https://cdn.jsdelivr.net/npm/**", route_cdn)
    pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
    pg.route("https://fonts.gstatic.com/**", lambda r: r.abort())
    pg.goto(f"http://127.0.0.1:8765/{page_name}")
    pg.wait_for_function("window.__ready === true", timeout=120000)
    time.sleep(1.0)
    pg.screenshot(path=f"{out}_0.png")
    for i, js in enumerate(steps, 1):
        if js.startswith("CLICK "):
            x, y = map(float, js.split()[1:3]); pg.mouse.click(x, y); r = None
        elif js.startswith("TAP "):
            x, y = map(float, js.split()[1:3]); pg.touchscreen.tap(x, y); r = None
        else:
            r = pg.evaluate(js)
        if r is not None:
            print("eval:", r)
        time.sleep(1.2)
        pg.screenshot(path=f"{out}_{i}.png")
    b.close()
httpd.shutdown()

"""Render the start-screen figure layers with Playwright.
usage: render_body.py <serve_dir> <out_dir> <w> <h>
"""
import sys, os, base64, json, threading, http.server, functools
from playwright.sync_api import sync_playwright

serve_dir, out_dir, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
NM = os.environ["NM"]
os.makedirs(out_dir, exist_ok=True)
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)
Handler.log_message = lambda *a: None
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8766), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()


def route_cdn(route):
    path = route.request.url.split("/npm/", 1)[1]
    pkg, rest = path.split("/", 1)
    route.fulfill(path=os.path.join(NM, pkg.rsplit("@", 1)[0], rest), content_type="application/javascript")


def save(name, data_url):
    open(os.path.join(out_dir, name), "wb").write(base64.b64decode(data_url.split(",", 1)[1]))


with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": W, "height": H})
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.on("console", lambda m: print("console:", m.text) if m.type == "error" else None)
    pg.route("https://cdn.jsdelivr.net/npm/**", route_cdn)
    pg.goto(f"http://127.0.0.1:8766/render.html?w={W}&h={H}")
    pg.wait_for_function("window.__ready === true", timeout=300000)
    if os.environ.get("ONLY") == "mask":
        save("mask2x.png", pg.evaluate("shot('mask')"))
        b.close(); httpd.shutdown(); print("ok"); sys.exit(0)
    save("bones.png", pg.evaluate("shot('bones')"))
    save("skin-light.png", pg.evaluate("shot('skin', {color: '#3f6c66', alpha: 0.95, pow: 2.2})"))
    save("skin-dark.png", pg.evaluate("shot('skin', {color: '#a9d6cf', alpha: 0.85, pow: 2.2})"))
    for r in ["head", "neck", "trunk", "arm", "leg"]:
        save(f"hl-{r}.png", pg.evaluate(f"shot('hl', '{r}')"))
    save("id.png", pg.evaluate("shot('id')"))
    save("mask.png", pg.evaluate("shot('mask')"))
    open(os.path.join(out_dir, "anchors.json"), "w").write(pg.evaluate("anchors()"))
    b.close()
httpd.shutdown()
print("ok")

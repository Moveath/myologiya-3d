"""Start the portable atlas using only Python's standard library."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
import webbrowser

site=Path(__file__).resolve().parents[1]/'site'
for port in range(8000,8051):
    try:
        server=ThreadingHTTPServer(('127.0.0.1',port),partial(SimpleHTTPRequestHandler,directory=str(site)))
        break
    except OSError:
        if port==8050: raise
url=f'http://127.0.0.1:{port}/local.html'
print('Atlas:',url,flush=True)
print('Keep this window open. Press Ctrl+C to stop.',flush=True)
threading.Timer(.4,lambda:webbrowser.open(url)).start()
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()

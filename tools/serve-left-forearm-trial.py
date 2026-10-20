"""Loopback-only review server: site assets + a separate generated trial directory."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "build_stage6/left_forearm_v1/browser"

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        url = unquote(urlsplit(path).path)
        base = TRIAL if url.startswith("/stage6-trial/") else ROOT / "site"
        rel = url[len("/stage6-trial/"):] if base == TRIAL else url.lstrip("/")
        result = (base / rel).resolve()
        return str(result) if result.is_relative_to(base) else str(base / "__invalid_path__")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8784)
    args = parser.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()

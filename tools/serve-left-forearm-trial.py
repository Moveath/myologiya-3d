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
    parser.add_argument("--trial-dir", default="build_stage6/left_forearm_v1/browser")
    args = parser.parse_args()
    candidate = (ROOT / args.trial_dir).resolve()
    if not candidate.is_relative_to(ROOT / "build_stage6") or not candidate.is_dir():
        parser.error("Trial directory must exist inside build_stage6")
    TRIAL = candidate
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()

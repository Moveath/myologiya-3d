"""Compute landmark positions in a running pintool driver and save them as JSON.

usage (driver must be running, see AGENTS.md):
  python3 scripts/export_positions.py qarm pins/ta.json pins/old_hi.json
  python3 scripts/export_positions.py qleg pins_leg/ta.json pins_leg/old_hi.json

landmarks.js    -> window.__pins (older landmark set, reused as anchors)  -> old_hi.json
landmarks_ta.js -> window.__ta   (every TA98 term + attachment areas)      -> ta.json
"""
import json, os, subprocess, sys

qdir, ta_out, old_out = sys.argv[1:4]
q = os.path.join(os.path.dirname(os.path.abspath(__file__)), "q.py")


def run(name, js):
    r = subprocess.run([sys.executable, q, qdir, name, js], capture_output=True, text=True, check=True).stdout.strip()
    if r.startswith("ERROR"):
        sys.exit(r)
    return json.loads(r)


print(run("x_lm", "runLM()"))
res = json.loads(run("x_ta", "runTA()"))
if res["miss"]:
    sys.exit(f"positions not found: {res['miss']}")
ta = json.loads(run("x_ta_dump", "JSON.stringify(__ta)"))
old = json.loads(run("x_old_dump", "JSON.stringify(__pins.filter(p => !p.missing).map(p => ({b: p.bone, id: p.id, p: p.p.map(x => +x.toFixed(5)), n: p.n.map(x => +x.toFixed(3))})))"))
json.dump([{"b": p["bone"], "id": p["id"], "p": p["p"], "n": p["n"]} for p in ta if not p.get("missing")], open(ta_out, "w"))
json.dump(old, open(old_out, "w"))
print(len(ta), "TA positions ->", ta_out, ";", len(old), "older positions ->", old_out)

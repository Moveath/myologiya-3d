"""Send one JS job to a running driver and print its result.

usage: python3 q.py <queue_dir> <name> <js | @file.js>
"""
import sys, os, time

qdir, name, code = sys.argv[1], sys.argv[2], sys.argv[3]
if code.startswith("@"):
    code = open(code[1:]).read()
out = os.path.join(qdir, name + ".out")
for ext in (".out", ".png"):
    if os.path.exists(os.path.join(qdir, name + ext)):
        os.remove(os.path.join(qdir, name + ext))
tmp = os.path.join(qdir, name + ".tmp")
open(tmp, "w").write(code)
os.rename(tmp, os.path.join(qdir, name + ".job"))
t0 = time.time()
while not os.path.exists(out):
    if time.time() - t0 > 300:
        print("TIMEOUT"); sys.exit(1)
    time.sleep(0.05)
time.sleep(0.05)
print(open(out).read())

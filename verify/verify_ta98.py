"""Compare the atlas TA98 table (scripts/ta98.py) with the reference list copied from IFAA (verify/ifaa.txt).

usage: python3 verify/verify_ta98.py
Expected output: exactly 3 known differences —
  A02.5.10.015 is shown as "ERR1" in the IFAA list (its entity page says facies malleolaris medialis);
  A02.5.10.017 / A02.5.11.007: IFAA lists "musculi longi flexoris hallucis", the atlas keeps "musculi flexoris hallucis longi".
"""
import os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(root, "scripts"))
from ta98 import T

ref = {}
for line in open(os.path.join(root, "verify", "ifaa.txt")):
    code, lat = line.strip().split(" ", 1)
    ref["A" + code] = lat
print("only in IFAA list:", sorted(set(ref) - set(T)))
print("only in atlas:", sorted(set(T) - set(ref)))
diff = 0
for c in sorted(set(ref) & set(T)):
    r = ref[c].strip("()").split(";")[0].strip()
    m = T[c][0].split(";")[0].strip()
    if r != m or ref[c].startswith("(") != (T[c][2] == "inc"):
        diff += 1
        print("DIFF", c, "| IFAA:", ref[c], "| atlas:", T[c][0], T[c][2])
print(len(ref), "terms compared,", diff, "differences")

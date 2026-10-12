"""Compare the atlas TA98 table (scripts/ta98.py) with the reference list copied from IFAA (verify/ifaa.txt).

usage: python3 verify/verify_ta98.py
Expected output: exactly 3 known differences —
  A02.5.10.015 is shown as "ERR1" in the IFAA list (its entity page says facies malleolaris medialis);
  A02.5.10.017 / A02.5.11.007: IFAA lists "musculi longi flexoris hallucis", the atlas keeps "musculi flexoris hallucis longi".
"""
import os, sys, json
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(root, "scripts"))
from ta98 import T

ref = {}
for line in open(os.path.join(root, "verify", "ifaa.txt")):
    code, lat = line.strip().split(" ", 1)
    ref["A" + code] = lat
for row in json.load(open(os.path.join(root, 'verify', 'ifaa-head-bones.json'), encoding='utf-8')):
    if row['code'] in T:
        ref[row['code']] = row['lat']
# The website contains later nomenclature revisions. These three skull entries
# are checked against the printed TA98, Kolesnikov 2003, pp. 12–13. Assert the
# raw electronic values before applying the documented edition reconciliation.
printed_head = {
    'A02.1.03.031': ('septum intersinuale frontale', 'septum sinuum frontalium'),
    'A02.1.05.017': ('apertura sinus sphenoidalis', 'septum sinuum sphenoidalium'),
    'A02.1.05.018': ('septum sinuum sphenoidalium', 'apertura sinus sphenoidalis'),
}
for code, (electronic, printed) in printed_head.items():
    assert ref[code] == electronic, (code, 'Unexpected IFAA revision')
    assert T[code][0] == printed, (code, 'Printed TA98 mismatch')
    ref[code] = printed
print('Skull edition reconciliation: 3 documented entries checked against printed TA98')
print("only in IFAA list:", sorted(set(ref) - set(T)))
print("only in atlas:", sorted(set(T) - set(ref)))
diff = 0
for c in sorted(set(ref) & set(T)):
    r = ref[c].strip("()").split(";")[0].strip()
    m = T[c][0].split(";")[0].strip()
    if r != m or ref[c].startswith("(") != (T[c][2] in ("inc", "ta_parentheses")):
        diff += 1
        print("DIFF", c, "| IFAA:", ref[c], "| atlas:", T[c][0], T[c][2])
print(len(ref), "terms compared,", diff, "differences")
assert not (set(ref) ^ set(T)), 'TA98 term sets differ'
assert diff == 3, 'Expected exactly the 3 documented legacy differences'

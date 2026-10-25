"""Per-owner contralateral comparison of sampled source-mesh penetration (no mesh changes).

Left rows: stage6 remaining20 diagnostics (native BP3D 3.0 left and live admitted neighbours).
Right rows: verify_right_baseline_depth.py on the accepted right live assets, same algorithm.
A pair passes only when the left depth reproduces the accepted right depth of the same pair
(same-source pair) or, at a boundary with an admitted mirrored neighbour, stays within the
deepest accepted right pair of that joint class. This is an educational consistency rule,
not a cartilage, joint-space or clinical tolerance.
"""
import collections
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
LEFT = root/"research/evidence-runs/stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj/comparison-depth.json"
RIGHT = root/sys.argv[2]
SAME_SOURCE_TOLERANCE_MM = 0.15
TARGETS = ["talus", "calcaneus", "cuboid", "cuneiform_lat", "metatarsal_1", "metatarsal_2", "metatarsal_3",
           "metatarsal_4", "metatarsal_5", "toe_prox_1", "toe_dist_1", "toe_prox_5", "toe_mid_5", "toe_dist_5",
           "metacarpal_1", "metacarpal_3"]
# Admitted left neighbours that are reflections of right bones, not native left sources.
MIRRORED = {"sesamoid_pedis", "toe_prox_2", "toe_prox_3", "toe_prox_4", "toe_mid_2", "toe_mid_3", "toe_mid_4",
            "toe_dist_2", "toe_dist_3", "toe_dist_4"}
CLASS = lambda a, b: ("MTP/MCP" if {a.split("_")[0], b.split("_")[0]} in ({"metatarsal", "toe"}, {"metacarpal", "phalanx"})
                      or "sesamoid_pedis" in (a, b) else "other")

read = lambda p: json.loads(Path(p).read_text(encoding="utf8"))
right = {}
for r in read(RIGHT)["rows"]:
    assert r["complete"], r
    key = tuple(sorted([r["a"].split(":")[1], r["b"].split(":")[1]]))
    right[key] = max(right.get(key, 0.0), r["maxSamplePenetrationMM"])
left = collections.defaultdict(float)
for r in read(LEFT)["rows"]:
    assert r["complete"], r
    (va, a), (vb, b) = r["a"].split("__"), r["b"].split("__")
    if "mirror" in (va, vb) or {va, vb} == {"live"}:
        continue  # Only the final native configuration: native target with native/live neighbour.
    key = tuple(sorted([a.removesuffix("_left"), b.removesuffix("_left")]))
    left[key] = max(left[key], r["maxSamplePenetrationMM"])
class_max = collections.defaultdict(float)
for (a, b), depth in right.items():
    class_max[CLASS(a, b)] = max(class_max[CLASS(a, b)], depth)

pairs, decisions = [], {}
for key, depth in sorted(left.items()):
    if not set(key) & set(TARGETS):
        continue
    mixed = bool(set(key) & MIRRORED)
    baseline = right.get(key)
    if mixed:
        limit, rule = class_max[CLASS(*key)], "mixed_boundary_within_deepest_accepted_right_class"
    elif baseline is None:
        limit, rule = None, "no_right_baseline"
    else:
        limit, rule = baseline+SAME_SOURCE_TOLERANCE_MM, "same_source_reproduces_right_baseline"
    passed = limit is not None and depth <= limit
    pairs.append(dict(pair=list(key), leftDepthMM=round(depth, 6), rightBaselineMM=None if baseline is None else round(baseline, 6),
                      differenceMM=None if baseline is None else round(depth-baseline, 6), mixedWithMirroredNeighbour=mixed,
                      jointClass=CLASS(*key), limitMM=None if limit is None else round(limit, 6), rule=rule, passed=passed))
for bone in TARGETS:
    rows = [p for p in pairs if bone in p["pair"]]
    decisions[bone+"_left"] = dict(pairs=len(rows), passed=all(p["passed"] for p in rows),
                                   maxLeftDepthMM=max((p["leftDepthMM"] for p in rows), default=0.0),
                                   mixedBoundaries=[p["pair"] for p in rows if p["mixedWithMirroredNeighbour"]])
result = dict(leftEvidence=LEFT.relative_to(root).as_posix(), rightEvidence=RIGHT.relative_to(root).as_posix(),
              sameSourceToleranceMM=SAME_SOURCE_TOLERANCE_MM, rightClassMaximaMM=dict(class_max), pairs=pairs,
              decisions=decisions, allPassed=all(d["passed"] for d in decisions.values()),
              scope="Educational consistency with the accepted right model of the same BodyParts3D 3.0 source. "
                    "Not cartilage, joint-space, clinical or full anatomical acceptance; intersections remain source defects.")
with (run/"baseline-comparison.json").open("x", encoding="utf8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(dict(allPassed=result["allPassed"], pairs=len(pairs),
                      failed=[p["pair"] for p in pairs if not p["passed"]],
                      maxSameSourceDifferenceMM=max(abs(p["differenceMM"]) for p in pairs if p["differenceMM"] is not None and not p["mixedWithMirroredNeighbour"]))))

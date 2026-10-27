"""Left connective-tissue counterparts for CAT-SOFT-TISSUE-BILATERAL (BodyParts3D 3.0 names only).

Every right structure of manifest.OTHER / manifest_leg.OTHER is mapped to the left file of the
same BP3D concept by exact name ("right X" -> "left X", "of right Y" -> "of left Y").
Nothing is inferred from geometry; the review compares the left file with the reflected right one.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest
import manifest_leg
from left_limb_muscles import ID2NAME, NAME2ID, left_name

REGION = {**{k: 'arm' for k in manifest.OTHER}, **{k: 'leg' for k in manifest_leg.OTHER}}


def table():
    rows = []
    for key, region in REGION.items():
        (right_fma,) = (manifest.OTHER if region == 'arm' else manifest_leg.OTHER)[key]
        right = ID2NAME[right_fma]
        left = left_name(right)
        rows.append(dict(region=region, right=key, left=key + '_left', rightFMA=right_fma, rightName=right,
                         leftName=left, leftFMA=NAME2ID.get(left)))
    return rows


if __name__ == '__main__':
    import json
    print(json.dumps(table(), ensure_ascii=False, indent=1))

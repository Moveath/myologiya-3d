"""Left limb muscle correspondence for CAT-MUSCLE-BILATERAL (BodyParts3D 3.0 names only).

Every right manifest part is mapped to the left file of the same BP3D concept by exact name
("right X" -> "left X"; "of right foot" -> "of left foot"). A muscle that already has a left
card in another region (trunk/neck) is not duplicated here. Nothing is inferred from geometry.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest
import manifest_leg

_tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bp', 'all_named.tsv')
ID2NAME, NAME2ID = {}, {}
for line in open(_tsv, encoding='utf-8'):
    i, n = line.rstrip('\n').split('\t')
    ID2NAME[i] = n
    NAME2ID.setdefault(n, i)

# Right arm-region shoulder-girdle muscles whose left instances already exist as trunk/neck cards
# with admitted regional geometry; the left side is represented there, not duplicated in the arm.
CROSS_REGION_LEFT = {
    'pectoralis_major': 'thorax_pectoralis_major_left', 'pectoralis_minor': 'thorax_pectoralis_minor_left',
    'subclavius': 'thorax_subclavius_left', 'serratus_anterior': 'thorax_serratus_anterior_left',
    'latissimus_dorsi': 'thorax_latissimus_dorsi_left', 'trapezius': 'thorax_trapezius_left',
    'rhomboid_major': 'thorax_rhomboid_major_left', 'rhomboid_minor': 'thorax_rhomboid_minor_left',
    'levator_scapulae': 'neck_levator_scapulae_left',
}


def left_name(name):
    for a, b in ((' of right ', ' of left '), ('right ', 'left ')):
        if a in name:
            return name.replace(a, b, 1)
    raise KeyError('No side token: ' + name)


def table():
    rows = []
    for region, muscles in (('arm', manifest.MUSCLES), ('leg', manifest_leg.MUSCLES)):
        for muscle, parts in muscles.items():
            mapped = []
            for fid, part in parts:
                right = ID2NAME[fid]
                left = left_name(right)
                mapped.append(dict(part=part, rightFMA=fid, rightName=right, leftName=left, leftFMA=NAME2ID.get(left)))
            rows.append(dict(region=region, right=muscle, left=CROSS_REGION_LEFT.get(muscle, muscle + '_left'),
                             crossRegion=muscle in CROSS_REGION_LEFT, parts=mapped,
                             sourceComplete=all(p['leftFMA'] for p in mapped)))
    return rows


if __name__ == '__main__':
    import json
    print(json.dumps(table(), ensure_ascii=False, indent=1))

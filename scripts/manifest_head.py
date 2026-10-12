"""Skull and muscles of facial expression/mastication from BodyParts3D.

Both sides are actual source meshes, never mirrored. Teeth are context meshes.
Source/license: BodyParts3D, DBCLS, CC BY-SA 2.1 Japan.
"""
from pathlib import Path

NAME2ID = dict(line.rstrip('\n').split('\t')[::-1] for line in
               (Path(__file__).resolve().parents[1] / 'bp/all_named.tsv').open(encoding='utf-8'))

def ids(*names):
    return [NAME2ID[name] for name in names]

SINGLE_BONES = {
    'frontal': 'frontal bone', 'occipital': 'occipital bone',
    'sphenoid': 'sphenoid bone', 'ethmoid': 'ethmoid',
    'vomer': 'vomer', 'mandible': 'mandible',
}
PAIRED_BONES = {
    'parietal': 'parietal bone', 'temporal': 'temporal bone',
    'maxilla': 'maxilla', 'zygomatic': 'zygomatic bone',
    'palatine': 'palatine bone', 'nasal': 'nasal bone',
    'lacrimal': 'lacrimal bone', 'inferior_concha': 'inferior nasal concha',
}
BONES = {key: ids(name) for key, name in SINGLE_BONES.items()}
for key, name in PAIRED_BONES.items():
    for side in ('right', 'left'):
        BONES[f'{key}_{side}'] = ids(f'{side} {name}')

MUSCLES = {}
for side in ('right', 'left'):
    def add(key, *parts):
        MUSCLES[f'{key}_{side}'] = [(NAME2ID[name.format(side=side)], part) for name, part in parts]
    add('occipitofrontalis', ('{side} frontalis', 'frontal'), ('{side} occipitalis', 'occipital'))
    add('temporoparietalis', ('{side} temporoparietalis', None))
    add('orbicularis_oculi', ('orbital part of {side} orbicularis oculi', 'orbital'),
        ('palpebral part of {side} orbicularis oculi', 'palpebral'))
    add('masseter', ('superficial part of {side} masseter', 'superficial'),
        ('deep part of {side} masseter', 'deep'))
    add('lateral_pterygoid', ('upper head of {side} lateral pterygoid', 'upper'),
        ('lower head of {side} lateral pterygoid', 'lower'))
    for key, name in {
        'temporalis': 'temporalis', 'medial_pterygoid': 'medial pterygoid',
        'corrugator_supercilii': 'corrugator supercilii',
        'levator_labii_superioris': 'levator labii superioris',
        'levator_nasolabialis': 'levator labii superioris alaeque nasi',
        'levator_anguli_oris': 'levator anguli oris',
        'zygomaticus_major': 'zygomaticus major', 'zygomaticus_minor': 'zygomaticus minor',
        'depressor_labii_inferioris': 'depressor labii inferioris',
        'depressor_anguli_oris': 'depressor anguli oris',
        'mentalis': 'mentalis', 'buccinator': 'buccinator', 'risorius': 'risorius',
        'nasalis': 'nasalis', 'depressor_septi_nasi': 'depressor septi nasi', 'procerus': 'procerus',
    }.items():
        add(key, ('{side} ' + name, None))
MUSCLES['orbicularis_oris'] = [(NAME2ID['orbicularis oris'], None)]
OTHER = {'epicranial_aponeurosis': ids('aponeurosis of epicranius')}
CONTEXT = [fid for name, fid in NAME2ID.items() if 'tooth' in name]

def all_ids():
    return [fid for parts in MUSCLES.values() for fid, _ in parts] + [
        fid for group in (BONES, OTHER) for values in group.values() for fid in values] + CONTEXT

if __name__ == '__main__':
    print(f'{len(BONES)} bones, {len(MUSCLES)} muscle instances, {len(all_ids())} source meshes')

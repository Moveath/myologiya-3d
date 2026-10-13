"""Neck source meshes, BodyParts3D 3.0 / DBCLS, CC BY-SA 2.1 Japan.

Each side uses its own source file. No mirroring or invented subdivision.
Context is not counted as an independently reviewed structure of this module.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME2ID = dict(line.rstrip('\n').split('\t')[::-1] for line in
               (ROOT / 'bp/all_named.tsv').open(encoding='utf-8'))
def ids(*names):
    return [NAME2ID[name] for name in names]

BONES = {'hyoid': ids('hyoid bone'), 'atlas': ids('atlas'), 'axis': ids('axis')}
for number, word in enumerate(['third', 'fourth', 'fifth', 'sixth', 'seventh'], 3):
    BONES[f'cervical_{number}'] = ids(f'{word} cervical vertebra')

SIMPLE_MUSCLES = {
    'platysma': 'platysma', 'sternocleidomastoid': 'sternocleidomastoid',
    'stylohyoid': 'stylohyoid', 'mylohyoid': 'mylohyoid', 'geniohyoid': 'geniohyoid',
    'sternohyoid': 'sternohyoid', 'omohyoid': 'omohyoid',
    'sternothyroid': 'sternothyroid', 'thyrohyoid': 'thyrohyoid',
    'scalenus_anterior': 'scalenus anterior', 'scalenus_medius': 'scalenus medius',
    'scalenus_posterior': 'scalenus posterior', 'longus_capitis': 'longus capitis',
    'rectus_capitis_anterior': 'rectus capitis anterior',
    'rectus_capitis_lateralis': 'rectus capitis lateralis',
    'rectus_capitis_posterior_major': 'rectus capitis posterior major',
    'rectus_capitis_posterior_minor': 'rectus capitis posterior minor',
    'obliquus_capitis_superior': 'obliquus capitis superior',
    'obliquus_capitis_inferior': 'obliquus capitis inferior',
    'splenius_capitis': 'splenius capitis', 'splenius_cervicis': 'splenius cervicis',
    'iliocostalis_cervicis': 'iliocostalis cervicis',
    'longissimus_capitis': 'longissimus capitis', 'longissimus_cervicis': 'longissimus cervicis',
    'spinalis_cervicis': 'spinalis cervicis',
    'semispinalis_capitis': 'semispinalis capitis', 'semispinalis_cervicis': 'semispinalis cervicis',
}
MUSCLES = {}
for side in ('right', 'left'):
    for key, name in SIMPLE_MUSCLES.items():
        MUSCLES[f'{key}_{side}'] = [(NAME2ID[f'{side} {name}'], None)]
    MUSCLES[f'digastric_{side}'] = [
        (NAME2ID[f'anterior belly of {side} digastric'], 'anterior'),
        (NAME2ID[f'posterior belly of {side} digastric'], 'posterior')]
    MUSCLES[f'longus_colli_{side}'] = [
        (NAME2ID[f'superior oblique part of {side} longus colli'], 'superior_oblique'),
        (NAME2ID[f'vertical intermediate part of {side} longus colli'], 'vertical'),
        (NAME2ID[f'inferior oblique part of {side} longus colli'], 'inferior_oblique')]
    MUSCLES[f'neck_levator_scapulae_{side}'] = [(NAME2ID[f'{side} levator scapulae'], None)]
    MUSCLES[f'neck_trapezius_{side}'] = [
        (NAME2ID[f'{part} part of {side} trapezius'], part)
        for part in ('descending', 'transverse', 'ascending')]

OTHER = {}
CONTEXT = ids('occipital bone', 'mandible', 'right temporal bone', 'left temporal bone',
              'right clavicle', 'left clavicle', 'manubrium', 'body of sternum',
              'right scapula', 'left scapula', 'thyroid cartilage',
              'right first rib', 'left first rib', 'right second rib', 'left second rib')
for word in ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']:
    CONTEXT += ids(f'{word} thoracic vertebra')

def all_ids():
    return [fid for parts in MUSCLES.values() for fid, _ in parts] + [
        fid for values in BONES.values() for fid in values] + CONTEXT

if __name__ == '__main__':
    print(len(BONES), 'bones;', len(MUSCLES), 'muscles;', len(all_ids()), 'source objects')

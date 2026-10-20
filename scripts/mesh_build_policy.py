"""Bone preservation rules shared by the builder and its regression tests."""
import math


def bone_settings(environ):
    ratio = float(environ.get('BONE_RATIO', '1'))
    cap = int(environ['BONE_MAX']) if 'BONE_MAX' in environ else math.inf
    if ratio != 1 or cap <= 0:
        raise ValueError('Bone decimation is forbidden: BONE_RATIO must be 1; BONE_MAX must be positive.')
    return ratio, cap


def bone_target(face_count, cap):
    if cap < face_count:
        raise ValueError(f'BONE_MAX={cap} would discard bone triangles ({face_count}); remove the cap.')
    return face_count

"""Candidate MCP-I sesamoids from the Visible Human Male frozen CT (method F, CAT-HAND-SESAMOIDS).

Source: NLM Visible Human Project, Male, radiological/frozenCT PNG slices 1700-1849 (one scan
block; 0.9375 mm pixels, 1 mm slices; headers checked). Use: NLM Terms and Conditions
(no fee, redistribution with "Courtesy of the U.S. National Library of Medicine", no endorsement).
The VHP male is a different body from BodyParts3D, so nothing is copied by coordinates:
  1. the two nodules at each thumb MCP joint are identified visually on gridded slice crops
     (NODULES: centre voxel per nodule; overlays in RUN for review). At 1 mm voxels one nodule of
     each pair touches the joint, so automatic "two separate components" detection is not reliable;
  2. seeded watershed on inverted intensity separates each nodule from the bones and soft tissue;
     a threshold sweep records at which level each nodule separates from the bone chain;
  3. each nodule becomes an isosurface (local half-maximum, cubic upsampling, marching tetrahedra);
  4. the distal I metacarpal of the CT is registered to the BodyParts3D I metacarpal of the same
     side by ICP with uniform scale, from 12 roll starts (ambiguity is reported, not hidden);
  5. the same transform places the nodules; placement, overlap, palmar relation (FPB, adductor
     pollicis, FPL meshes) and radial/ulnar identity (ulnar = nearer the II metacarpal) are measured.
Writes RUN/{headers,segmentation,registration,placement}.json, overlay PNGs and candidate GLBs in
research/cache/vhp-sesamoids/. Nothing is published by this script.
Usage: python scripts/vhp_thumb_sesamoids.py RUN
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys
import zlib
import numpy as np
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'verify'))
from geometry_distance import SurfaceQuery  # noqa: E402

run = Path(sys.argv[1]).resolve()
CT = ROOT / 'research/cache/vhp-male-frozenct'
OUT = ROOT / 'research/cache/vhp-sesamoids'
FIRST, LAST = 1700, 1849
# Visually identified nodule centres (column, row, slice) in the 512x512 frozen CT; see RUN/*-joint.png.
# A: palmar edge of the joint, towards the midline (thumb's radial side in this hand posture);
# B: beside the joint, towards the index finger. Identity is decided after registration, not here.
NODULES = {'left': {'A': (352.3, 113.8, 1798.5), 'B': (360.0, 106.8, 1801.0)},
           'right': {'A': (200.5, 104.3, 1790.0), 'B': (193.6, 96.6, 1794.0)}}
ATLAS = {'left': dict(mc1='metacarpal_1_left', mc2='metacarpal_2_left', pp1='phalanx_prox_1_left', suffix='_left'),
         'right': dict(mc1='metacarpal_1', mc2='metacarpal_2', pp1='phalanx_prox_1', suffix='')}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def header(n):
    text = (CT / f'cvm{n}f.txt').read_bytes().replace(b'\0', b'').decode('latin1')
    get = lambda label: re.search(re.escape(label) + r'\.*: *(-?[\d.]+)', text).group(1)
    return dict(slice=n, location=float(get('Image location')), pixel=float(get('Image pixel size - X')),
                thickness=float(get('Slice Thickness (mm)')), series=int(get('Series number for this image')),
                R0=float(get('R Coord of Top Left Hand Corner')), A0=float(get('A Coord of Top Left Hand Corner')))


def slice_png(n):
    data = (CT / f'cvm{n}f.png').read_bytes()
    pos, idat = 8, b''
    while pos < len(data):
        size, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + size]
        pos += 12 + size
        if kind == b'IHDR':
            w, h, depth, ctype = struct.unpack('>IIBB', body[:10])
            assert depth == 16 and ctype == 0
        elif kind == b'IDAT':
            idat += body
    raw = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(h, 2 * w + 1)
    assert (raw[:, 0] == 0).all(), 'PNG filter 0 expected'
    return raw[:, 1:].copy().view('>u2').astype(np.float32)


def write_png(path, rgb):
    rgb = np.ascontiguousarray(rgb.astype(np.uint8))
    h, w = rgb.shape[:2]
    raw = b''.join(b'\0' + rgb[y].tobytes() for y in range(h))
    chunk = lambda t, b: struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) +
                     chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


headers = [header(n) for n in range(FIRST, LAST + 1)]
assert all(h['pixel'] == 0.9375 and h['thickness'] == 1 and h['series'] == headers[0]['series'] for h in headers)
assert all(b['location'] - a['location'] == -1 for a, b in zip(headers, headers[1:])), 'non-contiguous block'
PX, R0, A0, S0 = headers[0]['pixel'], headers[0]['R0'], headers[0]['A0'], headers[0]['location']
V = np.stack([slice_png(n) for n in range(FIRST, LAST + 1)])
sources = {f'cvm{n}f.{ext}': sha(CT / f'cvm{n}f.{ext}') for n in range(FIRST, LAST + 1) for ext in ('png', 'txt')}


def to_atlas_mm(z, row, col):
    """Voxel centre -> atlas-axis frame in mm: X = patient left, Y = superior, Z = anterior."""
    R = R0 - (np.asarray(col) + 0.5) * PX
    A = A0 - (np.asarray(row) + 0.5) * PX
    S = S0 - np.asarray(z, dtype=float)
    return np.stack([-R, S, A], axis=-1)


def marching_tetrahedra(F, level, spacing, origin):
    """Isosurface of F > level on a regular grid (z, y, x); consistent outward winding."""
    nz, ny, nx = F.shape
    gid = np.arange(F.size).reshape(F.shape)
    corners = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)]
    tets = [(0, 5, 1, 6), (0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6)]
    cz, cy, cx = np.meshgrid(np.arange(nz - 1), np.arange(ny - 1), np.arange(nx - 1), indexing='ij')
    cz, cy, cx = cz.ravel(), cy.ravel(), cx.ravel()
    cid = [gid[cz + dz, cy + dy, cx + dx] for dz, dy, dx in corners]
    flat = F.ravel()
    pos = np.stack(np.unravel_index(np.arange(F.size), F.shape), axis=1).astype(float)  # (z, y, x)
    keys, faces, outward = [], [], []

    def edge(a, b):
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        return lo * F.size + hi

    for tet in tets:
        ids = np.stack([cid[t] for t in tet], axis=1)
        inside = flat[ids] > level
        count = inside.sum(axis=1)
        for k in (1, 3):
            sel = count == k
            if not sel.any():
                continue
            ins = inside[sel] if k == 1 else ~inside[sel]
            t = ids[sel]
            lone = t[np.arange(len(t)), ins.argmax(axis=1)]
            others = np.stack([t[i][~ins[i]] for i in range(len(t))])
            tri = np.stack([edge(lone, others[:, j]) for j in range(3)], axis=1)
            sign = 1 if k == 1 else -1
            out = sign * (pos[others].mean(axis=1) - pos[lone])
            keys.append(tri); outward.append(out)
        sel = count == 2
        if sel.any():
            t, ins = ids[sel], inside[sel]
            a = np.stack([t[i][ins[i]] for i in range(len(t))])
            b = np.stack([t[i][~ins[i]] for i in range(len(t))])
            q = np.stack([edge(a[:, 0], b[:, 0]), edge(a[:, 0], b[:, 1]), edge(a[:, 1], b[:, 1]), edge(a[:, 1], b[:, 0])], axis=1)
            out = pos[b].mean(axis=1) - pos[a].mean(axis=1)
            keys += [q[:, [0, 1, 2]], q[:, [0, 2, 3]]]; outward += [out, out]
    keys, outward = np.vstack(keys), np.vstack(outward)
    unique, inverse = np.unique(keys.ravel(), return_inverse=True)
    lo, hi = unique // F.size, unique % F.size
    fl, fh = flat[lo], flat[hi]
    t = ((level - fl) / (fh - fl))[:, None]
    verts = pos[lo] + t * (pos[hi] - pos[lo])
    tri = inverse.reshape(-1, 3)
    normal = np.cross(verts[tri[:, 1]] - verts[tri[:, 0]], verts[tri[:, 2]] - verts[tri[:, 0]])
    flip = (normal * outward).sum(axis=1) < 0
    tri[flip] = tri[flip][:, [0, 2, 1]]
    return verts * spacing + origin, tri


def atlas_meshes():
    out = {}
    for sec in ('arm',):
        index = json.loads((ROOT / f'research/cache/atlas-geometry/{sec}.json').read_text(encoding='utf8'))
        raw = (ROOT / f'research/cache/atlas-geometry/{sec}.bin').read_bytes()
        Vs = np.frombuffer(raw[:index['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(float) * 1000
        Fs = np.frombuffer(raw[index['vertexBytes']:], dtype=np.uint32).reshape(-1, 3).astype(np.int64)
        for n in index['nodes']:
            kind, key = n['name'].split('|')[:2]
            v = Vs[n['vertexOffset']:n['vertexOffset'] + n['vertexCount']]
            f = Fs[n['faceOffset']:n['faceOffset'] + n['faceCount']]
            m = trimesh.Trimesh(vertices=v, faces=f, process=False)
            out[(kind, key)] = trimesh.util.concatenate([out[(kind, key)], m]) if (kind, key) in out else m
    return out


def closest(mesh_mm, points_mm, batch=48):
    """Batched exact closest points (mm) on a mesh; bounded memory for full-resolution bones."""
    query = SurfaceQuery(trimesh.Trimesh(vertices=np.asarray(mesh_mm.vertices) / 1000, faces=mesh_mm.faces, process=False))
    out = [query.closest(np.asarray(points_mm[i:i + batch]) / 1000) for i in range(0, len(points_mm), batch)]
    return np.vstack([o[0] for o in out]) * 1000, np.concatenate([o[1] for o in out]), np.concatenate([o[2] for o in out])


atlas = atlas_meshes()
OUT.mkdir(parents=True, exist_ok=True)
segmentation, registration, placement = {}, {}, {}
for side, marks in NODULES.items():
    centre_vox = np.mean([m for m in marks.values()], axis=0)
    c0, r0, z0 = int(round(centre_vox[0])), int(round(centre_vox[1])), int(round(centre_vox[2])) - FIRST
    seed = dict(nodules=marks, R=round(R0 - (c0 + 0.5) * PX, 1), A=round(A0 - (r0 + 0.5) * PX, 1), slice=z0 + FIRST)
    half = int(22 / PX)
    zs, ze = max(0, z0 - 60), min(len(V), z0 + 13)
    box = (slice(zs, ze), slice(r0 - half, r0 + half), slice(c0 - half, c0 + half))
    C = V[box]
    seeds = {k: np.array([z - FIRST - zs, r - (r0 - half), c - (c0 - half)]) for k, (c, r, z) in marks.items()}
    zi, yi, xi = np.indices(C.shape)
    ball = {k: ((zi - v[0]) ** 2 + ((yi - v[1]) * PX) ** 2 + ((xi - v[2]) * PX) ** 2) <= 1.2 ** 2 for k, v in seeds.items()}
    near_seed = {k: ((zi - v[0]) ** 2 + ((yi - v[1]) * PX) ** 2 + ((xi - v[2]) * PX) ** 2) <= 3.5 ** 2 for k, v in seeds.items()}
    T = 1250
    lab, n = ndimage.label(C > T, structure=np.ones((3, 3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, np.arange(1, n + 1))
    big = [i + 1 for i, sz in enumerate(sizes) if sz > 400]
    # Threshold sweep (evidence): does each nodule seed form its own component apart from >400-voxel bones?
    sweep = []
    for level_t in range(1250, 1625, 25):
        lt, nt = ndimage.label(C > level_t, structure=np.ones((3, 3, 3)))
        st = ndimage.sum(np.ones_like(lt), lt, np.arange(1, nt + 1))
        row = dict(threshold=level_t)
        for k, b in ball.items():
            ids = np.unique(lt[b & (lt > 0)])
            row[k] = 'below threshold' if not len(ids) else 'merged with bone' if any(st[i - 1] > 400 for i in ids) else f'separate {int(max(st[i - 1] for i in ids))} vox'
        sweep.append(row)
    # Seeded watershed on inverted intensity: nodule A (1), nodule B (2), bone outside both seed
    # neighbourhoods (3), soft tissue (4).
    markers = np.zeros(C.shape, np.int32)
    markers[np.isin(lab, big) & (C > 1450) & ~near_seed['A'] & ~near_seed['B']] = 3
    markers[C < 1080] = 4
    markers[ball['A'] & (C > 1150)] = 1
    markers[ball['B'] & (C > 1150)] = 2
    assert (markers == 1).any() and (markers == 2).any(), side
    cost = np.clip(3000 - C, 0, 65535).astype(np.uint16)
    shed = ndimage.watershed_ift(cost, markers)
    soft = float(np.median(C[(C > 950) & (C < 1150)]))
    nodules = []
    for k, name in ((1, 'A'), (2, 'B')):
        # Watershed labels every voxel, so the basin includes a soft-tissue halo. The nodule core is
        # its voxels above 1150; the isosurface is the local half-maximum, never below the bone level T.
        within = ((zi - seeds[name][0]) ** 2 + ((yi - seeds[name][1]) * PX) ** 2 + ((xi - seeds[name][2]) * PX) ** 2) <= 6.0 ** 2
        region = (shed == k) & (C > 1150) & within
        peak = float(np.percentile(C[region], 99))
        level = max(T, (peak + soft) / 2)
        # Only the component above the level that contains the seed: no attached cortex of the joint.
        parts, _ = ndimage.label(region & (C > level), structure=np.ones((3, 3, 3)))
        keep = np.unique(parts[ball[name] & (parts > 0)])
        assert len(keep), (side, name)
        inside = np.isin(parts, keep)
        region = inside
        zz, yy, xx = np.nonzero(region)
        lo = np.maximum([zz.min() - 3, yy.min() - 3, xx.min() - 3], 0)
        hi = np.minimum([zz.max() + 4, yy.max() + 4, xx.max() + 4], C.shape)
        patch = np.where(ndimage.binary_dilation(region, iterations=2), C, soft)[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        f = 2  # half a CT voxel (0.47 mm): finer sampling only interpolates the 0.94 mm data
        gz, gy, gx = np.meshgrid(*[np.linspace(0, d - 1, (d - 1) * f + 1) for d in patch.shape], indexing='ij')
        fine = ndimage.map_coordinates(patch, [gz, gy, gx], order=3, mode='nearest')
        verts, faces = marching_tetrahedra(fine, level, np.array([1 / f, 1 / f, 1 / f]), np.zeros(3))
        # Grid (z, row, col) -> atlas mm.
        grid = verts + lo + [zs, r0 - half, c0 - half]
        mm = to_atlas_mm(grid[:, 0] + FIRST - FIRST, grid[:, 1], grid[:, 2])
        mesh = trimesh.Trimesh(vertices=mm, faces=faces, process=True)
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.remove_unreferenced_vertices()
        # Cubic upsampling leaves sub-voxel islands of the same nodule; keep only the largest shell.
        shells = mesh.split(only_watertight=False)
        dropped = sorted(round(float(abs(s.volume)), 3) for s in shells)[:-1]
        mesh = max(shells, key=lambda s: abs(s.volume))
        trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=10)
        assert mesh.is_watertight and mesh.volume > 0, (side, k)
        ext = np.sort(mesh.extents)[::-1]
        nodules.append(dict(k=k, nodule=name, voxels=int(region.sum()), voxelsAboveLevel=int(inside.sum()), peak=round(peak), level=round(level),
                            extentsMM=ext.round(2).tolist(), volumeMM3=round(float(mesh.volume), 1), triangles=int(len(mesh.faces)),
                            droppedIslandsMM3=dropped, mesh=mesh))
    # I metacarpal of the CT: the large component closest to both nodules, split from the phalanx by
    # watershed between a proximal and a distal marker; only the distal 30 mm (head and shaft) is used.
    big_lab = np.isin(lab, big)
    blab, _ = ndimage.label(big_lab, structure=np.ones((3, 3, 3)))
    nod_centre = np.mean([np.argwhere(shed == k).mean(axis=0) for k in (1, 2)], axis=0)
    near = ndimage.distance_transform_edt(~((shed == 1) | (shed == 2)))
    chain = np.bincount(blab[(near < 4) & big_lab]).argmax() if ((near < 4) & big_lab).any() else 0
    assert chain, side
    chainmask = blab == chain
    zc = int(round(nod_centre[0]))
    m2 = np.zeros(C.shape, np.int32)
    m2[(chainmask) & (np.arange(C.shape[0])[:, None, None] < zc - 8)] = 1
    m2[(chainmask) & (np.arange(C.shape[0])[:, None, None] > zc + 6)] = 2
    m2[C < 1080] = 3
    for k in (1, 2):
        m2[shed == k] = 3
    split = ndimage.watershed_ift(cost, m2)
    mc1 = (split == 1) & (C > T)
    pts = to_atlas_mm(*[a + o for a, o in zip(np.nonzero(mc1 & ~ndimage.binary_erosion(mc1)), (zs, r0 - half, c0 - half))])
    # Distal 30 mm along the principal axis.
    centre = pts.mean(axis=0)
    axis = np.linalg.svd(pts - centre, full_matrices=False)[2][0]
    nod_mm = to_atlas_mm(*[nod_centre[i] + o for i, o in enumerate((zs, r0 - half, c0 - half))])
    if np.dot(nod_mm - centre, axis) < 0:
        axis = -axis
    proj = (pts - centre) @ axis
    src = pts[proj > proj.max() - 30]
    names = ATLAS[side]
    target = atlas[('b', names['mc1'])]
    tv = np.asarray(target.vertices)
    tc = tv.mean(axis=0)
    taxis = np.linalg.svd(tv - tc, full_matrices=False)[2][0]
    if np.dot(np.asarray(atlas[('b', names['pp1'])].vertices).mean(axis=0) - tc, taxis) < 0:
        taxis = -taxis
    head_src = src[((src - centre) @ axis) > proj.max() - 6].mean(axis=0)
    head_tgt = tv[((tv - tc) @ taxis) > ((tv - tc) @ taxis).max() - 6].mean(axis=0)
    trials = []
    rot = trimesh.geometry.align_vectors(axis, taxis)
    for roll in range(0, 360, 30):
        spin = trimesh.transformations.rotation_matrix(np.radians(roll), taxis)
        init = spin @ rot
        init[:3, 3] = head_tgt - (init[:3, :3] @ head_src)
        matrix, moved, cost_ = trimesh.registration.icp(src, tv, initial=init, threshold=1e-6, max_iterations=120, scale=True, reflection=False)
        d = closest(target, moved[::4])[1]
        trials.append(dict(roll=roll, matrix=matrix, medianMM=float(np.median(d)), p95MM=float(np.percentile(d, 95)),
                           scale=float(np.cbrt(np.linalg.det(matrix[:3, :3])))))
    trials.sort(key=lambda t: t['medianMM'])
    best = trials[0]
    # Distinct optima: other starts whose result rotates the nodules elsewhere with similar fit.
    nod_mm_all = [np.asarray(n['mesh'].vertices).mean(axis=0) for n in nodules]
    spread = []
    for t in trials[1:]:
        if t['medianMM'] <= best['medianMM'] * 1.15:
            dev = max(np.linalg.norm(trimesh.transform_points([p], t['matrix'])[0] - trimesh.transform_points([p], best['matrix'])[0]) for p in nod_mm_all)
            spread.append(dict(roll=t['roll'], medianMM=round(t['medianMM'], 3), nodulesShiftMM=round(float(dev), 2)))
    registration[side] = dict(sourcePoints=int(len(src)), target=names['mc1'], bestRoll=best['roll'], medianMM=round(best['medianMM'], 3),
                              p95MM=round(best['p95MM'], 3), scale=round(best['scale'], 4),
                              trials=[dict(roll=t['roll'], medianMM=round(t['medianMM'], 3), p95MM=round(t['p95MM'], 3), scale=round(t['scale'], 4)) for t in trials],
                              nearEqualAlternatives=spread, matrix=best['matrix'].round(6).tolist())
    # Placement checks in the atlas frame.
    mc2 = np.asarray(atlas[('b', names['mc2'])].vertices).mean(axis=0)
    placed = []
    for n in nodules:
        mesh = n['mesh'].copy()
        mesh.apply_transform(best['matrix'])
        row = dict(k=n['k'], nodule=n['nodule'], centreMM=mesh.vertices.mean(axis=0).round(2).tolist(), extentsMM=np.sort(mesh.extents)[::-1].round(2).tolist(),
                   volumeMM3=round(float(mesh.volume), 1), distanceToMC2MM=round(float(np.linalg.norm(mesh.vertices.mean(axis=0) - mc2)), 2))
        for key in [('b', names['mc1']), ('b', names['pp1']), ('b', names['mc2']),
                    ('m', 'flexor_pollicis_brevis' + names['suffix']), ('m', 'adductor_pollicis' + names['suffix']),
                    ('m', 'flexor_pollicis_longus' + names['suffix']), ('m', 'abductor_pollicis_brevis' + names['suffix'])]:
            other = atlas[key]
            near_pts, dist, tri = closest(other, mesh.vertices)
            normals = other.face_normals[tri]
            signed = np.where(((mesh.vertices - near_pts) * normals).sum(axis=1) < 0, -dist, dist)
            # Bones are closed meshes with outward normals: signed depth. Muscle meshes are not closed: unsigned only.
            row[key[1]] = (dict(minMM=round(float(signed.min()), 2), penetratingVertices=int((signed < 0).sum())) if key[0] == 'b'
                           else dict(minUnsignedMM=round(float(dist.min()), 2)))
        placed.append((row, mesh))
    ulnar = min(placed, key=lambda r: r[0]['distanceToMC2MM'])
    for row, mesh in placed:
        identity = 'ulnar' if row is ulnar[0] else 'radial'
        row['identity'] = identity
        row['agreesWithCTPosture'] = (identity == 'ulnar') == (row['nodule'] == 'B')
        bone = f'sesamoid_mcp1_{identity}_{side}'
        mesh.apply_scale(0.001)
        scene = trimesh.Scene()
        scene.add_geometry(mesh, node_name=f'b|{bone}', geom_name=f'b|{bone}')
        path = OUT / f'{bone}.glb'
        path.write_bytes(scene.export(file_type='glb', include_normals=True))
        row.update(bone=bone, candidateFile=path.relative_to(ROOT).as_posix(), candidateSHA256=sha(path), triangles=int(len(mesh.faces)))
    placement[side] = [r for r, _ in placed]
    segmentation[side] = dict(seed=seed, crop=dict(slices=[FIRST + zs, FIRST + ze - 1]), sweep=sweep, chosenThreshold=T,
                              softTissue=round(soft), nodules=[{k: v for k, v in n.items() if k != 'mesh'} for n in nodules],
                              mc1Voxels=int(mc1.sum()))
    # Evidence overlays: every slice through the nodules, nodules red/blue, I metacarpal green.
    zr = sorted({int(z) for k in (1, 2) for z in np.nonzero(shed == k)[0]})
    tiles = []
    for z in range(max(0, zr[0] - 3), min(C.shape[0], zr[-1] + 4)):
        g = np.clip((C[z] - 950) / 1050 * 255, 0, 255)
        rgb = np.stack([g, g, g], axis=-1)
        rgb[(shed[z] == 1) & (C[z] > T - 100)] = [230, 60, 60]
        rgb[(shed[z] == 2) & (C[z] > T - 100)] = [60, 120, 240]
        rgb[mc1[z]] = rgb[mc1[z]] * 0.5 + np.array([40, 200, 80]) * 0.5
        tiles.append(np.kron(rgb, np.ones((4, 4, 1))))
    rows = [np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)]
    width = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0))) for r in rows]
    write_png(run / f'{side}-joint.png', np.vstack(rows))

dump = lambda name, value: (run / name).open('x', encoding='utf8').write(json.dumps(value, ensure_ascii=False, indent=1))
dump('headers.json', dict(slices=[FIRST, LAST], pixelMM=PX, sliceMM=1, series=headers[0]['series'], firstLocation=S0, sources=sources,
                          dataset='NLM Visible Human Project, Male, PNG_format/radiological/frozenCT',
                          url='https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/PNG_format/radiological/frozenCT/',
                          terms='https://www.nlm.nih.gov/databases/download/terms_and_conditions.html'))
dump('segmentation.json', segmentation)
dump('registration.json', registration)
dump('placement.json', placement)
print(json.dumps(dict(registration={s: {k: r[k] for k in ('bestRoll', 'medianMM', 'p95MM', 'scale', 'nearEqualAlternatives')} for s, r in registration.items()},
                      segmentation={s: dict(threshold=v['chosenThreshold'], nodules=[{k: n[k] for k in ('voxels', 'peak', 'level', 'extentsMM', 'volumeMM3')} for n in v['nodules']]) for s, v in segmentation.items()},
                      placement=placement), ensure_ascii=False, indent=1))

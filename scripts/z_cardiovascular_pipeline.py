"""Z-Anatomy cardiovascular sources registered to the atlas frame (CV-GEO-MISSING, LOG-20261026-03).

Input: research/cache/z-cardiovascular/z-cv-export.json from scripts/export_z_cardiovascular.py (Blender world space of the pinned
Z-Anatomy Startup.blend, commit 04d15340), the atlas geometry cache (tools/export-atlas-geometry.mjs) and the
published BodyParts3D cardiovascular GLBs. Nothing in the atlas is moved; only Z-Anatomy data are registered.

Stages (python scripts/z_cardiovascular_pipeline.py STAGE RUN):
  register — rigid ICP (no scale, no reflection) of Z-Anatomy reference bones to the same atlas bones:
             one transform per limb bone, the rib cage, and the heart (Z chambers to the BodyParts3D heart wall).
  vessels  — limb vessels follow their own bones: every vertex/centreline point is moved by the rigid transforms
             of the nearby Z bones blended by inverse distance (power 4), so a vessel keeps its distance to the
             bone it runs along; trunk vessels use the rib-cage or heart transform. Each vessel is reviewed for
             side, centreline inside atlas bones, continuity with its atlas parent vessel and calibre.
  masks    — face masks of existing BodyParts3D meshes (no new triangles): heart chambers from the nearest
             registered Z chamber, pulmonary trunk from the registered Z trunk, thoracic/abdominal aorta at the
             lower border of the atlas T12 body.
  publish  — admission rule for the registered Z-Anatomy objects (below), GLBs of admitted vessels and of the aortic
             valve cusps into site/models/z-anatomy/cardiovascular/ with licence and provenance.
Each stage writes one JSON into RUN (never overwrites); arrays go to research/cache/z-cardiovascular/build/ (outside git).

Admission of a registered vessel: correct side; centreline at most 2 mm inside an atlas bone unless the same
penetration exists in the Z-Anatomy source itself (kept and stated as a source defect); nearest end within 10 mm of
the surface of its parent vessel model; calibre recorded. Failing vessels stay cards without geometry.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/z-cardiovascular'
BUILD = CACHE / 'build'
EXPORT = CACHE / 'z-cv-export.json'
CV = ROOT / 'site/models/bodyparts3d-3.0/cardiovascular'
SOURCE = 'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend'
# Earlier labelled-vertebra registration of the same blend (stage 7); used only as the ICP start.
START = ROOT / 'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF/z-multifidus-registration.json'
ORD = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth']
SIDE = {'r': 'right', 'l': 'left'}
LIMB_BONES = {
    'arm': [('Clavicle', 'clavicle'), ('Scapula', 'scapula'), ('Humerus', 'humerus'), ('Radius', 'radius'), ('Ulna', 'ulna'),
            ('Scaphoid bone', 'scaphoid'), ('Lunate bone', 'lunate'), ('Triquetrum bone', 'triquetrum'), ('Pisiform bone', 'pisiform'),
            ('Trapezium bone', 'trapezium'), ('Hamate bone', 'hamate'), ('Capitate bone', 'capitate'),
            ('First metacarpal bone', 'metacarpal_1'), ('Second metacarpal bone', 'metacarpal_2'), ('Fifth metacarpal bone', 'metacarpal_5')],
    'leg': [('Hip bone', 'hip_bone'), ('Femur', 'femur'), ('Tibia', 'tibia'), ('Fibula', 'fibula'), ('Talus', 'talus'), ('Calcaneus', 'calcaneus'),
            ('Navicular bone', 'navicular'), ('Cuboid bone', 'cuboid'), ('Medial cuneiform bone', 'cuneiform_med'), ('First metatarsal bone', 'metatarsal_1')],
}
# Group fits use the long bones only; hand and foot bones get their own fit started from the group fit.
GROUP_BONES = {'arm': 5, 'leg': 4}
CHAMBERS = {'cv_atrium_right': 'Right atrium', 'cv_ventricle_right': 'Right ventricle', 'cv_atrium_left': 'Left atrium', 'cv_ventricle_left': 'Left ventricle'}
# Card id -> (Z object, section, carrier: limb or trunk/heart, atlas parent vessel for continuity, parent kind)
VESSELS = {}
for s, side in SIDE.items():
    for card, name, parent in [('a_axillary', 'Axillary artery', 'cv_a_subclavian_'), ('a_brachial', 'Brachial artery', 'cv_a_axillary_'),
                               ('a_radial', 'Radial artery', 'cv_a_brachial_'), ('a_ulnar', 'Ulnar artery', 'cv_a_brachial_'),
                               ('v_axillary', 'Axillary vein', 'cv_v_subclavian_'), ('v_cephalic', 'Cephalic vein', 'cv_v_axillary_'),
                               ('v_basilic', 'Basilic vein', 'cv_v_axillary_'), ('v_brachial', 'Brachial veins', 'cv_v_axillary_')]:
        VESSELS[f'cv_{card}_{side}'] = (f'{name}.{s}', 'arm', 'arm', parent + side)
    for card, name, parent in [('a_femoral', 'Femoral artery', 'cv_a_iliac_external_'), ('a_popliteal', 'Popliteal artery', 'cv_a_femoral_'),
                               ('a_tibial_anterior', 'Anterior tibial artery', 'cv_a_popliteal_'),
                               ('a_tibial_posterior', 'Posterior tibial artery', 'cv_a_popliteal_'),
                               ('a_fibular', 'Fibular artery', 'cv_a_tibial_posterior_'),
                               ('v_femoral', 'Femoral vein', 'cv_v_iliac_external_'), ('v_popliteal', 'Popliteal vein', 'cv_v_femoral_'),
                               ('v_saphenous_great', 'Great saphenous vein', 'cv_v_femoral_'),
                               ('v_saphenous_small', 'Small saphenous vein', 'cv_v_popliteal_')]:
        VESSELS[f'cv_{card}_{side}'] = (f'{name}.{s}', 'leg', 'leg', parent + side)
VESSELS.update({'cv_v_azygos': ('Azygos vein', 'trunk', 'trunk', 'cv_v_cava_superior'),
                'cv_v_hemiazygos': ('Hemi-azygos vein', 'trunk', 'trunk', 'cv_v_azygos'),
                'cv_v_portal': ('Hepatic portal vein', 'trunk', 'trunk', 'cv_v_mesenteric_superior'),
                'cv_v_coronary_sinus': ('Coronary sinus', 'trunk', 'heart', 'cv_heart')})
VALVE = {'cv_valve_aortic': ['Right coronary leaflet', 'Left coronary leaflet', 'Non-coronary leaflet']}


def write_json(path, value):
    with path.open('x', encoding='utf8') as fh:
        json.dump(value, fh, ensure_ascii=False, indent=1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atlas_nodes(section):
    cache = ROOT / 'research/cache/atlas-geometry'
    index = json.loads((cache / f'{section}.json').read_text(encoding='utf8'))
    for source in index['sources']:
        if sha(ROOT / source['file']) != source['sha256']:
            raise SystemExit(f'Stale geometry cache for {section}')
    raw = (cache / f'{section}.bin').read_bytes()
    V = np.frombuffer(raw[:index['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(raw[index['vertexBytes']:], dtype=np.uint32).reshape(-1, 3).astype(np.int64)
    nodes = {}
    for node in index['nodes']:
        nodes.setdefault(node['name'], []).append((V[node['vertexOffset']:node['vertexOffset'] + node['vertexCount']],
                                                    F[node['faceOffset']:node['faceOffset'] + node['faceCount']]))
    out = {}
    for name, chunks in nodes.items():
        vs, fs, off = [], [], 0
        for v, f in chunks:
            vs.append(v); fs.append(f + off); off += len(v)
        out[name] = trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=False)
    return out, index['sources']


def cv_mesh(card):
    return trimesh.load(CV / f'{card}.glb', force='mesh', process=False)


def icp(src, dst, start):
    matrix, _, _ = trimesh.registration.icp(src, dst, initial=start, threshold=1e-9, max_iterations=80, reflection=False, scale=False)
    d = cKDTree(dst).query(trimesh.transform_points(src, matrix))[0] * 1000
    return matrix, dict(medianMM=round(float(np.median(d)), 3), p95MM=round(float(np.percentile(d, 95)), 3), points=len(src))


def rotation_deg(a, b):
    r = (np.linalg.inv(a) @ b)[:3, :3]
    return round(float(np.degrees(np.arccos(np.clip((np.trace(r) - 1) / 2, -1, 1)))), 2)


def register(run, Z):
    start = np.array(json.loads(START.read_text(encoding='utf8'))[0]['matrix_source_blender_to_atlas_three'])
    zv = lambda n: np.array(Z[n]['vertices'])
    result, sources = {}, {}
    trunk, sources['trunk'] = atlas_nodes('trunk')
    pairs = [(f'{o} rib.{s}', f'b|rib_{i + 1}_{SIDE[s]}') for i, o in enumerate(ORD) for s in 'rl']
    pairs += [('Body of sternum', 'b|sternum|FMA7487'), ('Manubrium of sternum', 'b|sternum|FMA7486')]
    M, stats = icp(np.vstack([zv(z) for z, _ in pairs]), np.vstack([trunk[a].vertices for _, a in pairs]), start)
    result['trunk'] = dict(matrix=M.tolist(), bones=[a for _, a in pairs], **stats)
    heart = cv_mesh('cv_heart')
    surface = trimesh.sample.sample_surface(heart, 400000, seed=3)[0]
    H, stats = icp(np.vstack([zv(n) for n in CHAMBERS.values()]), surface, M)
    result['heart'] = dict(matrix=H.tolist(), target='cv_heart (BodyParts3D wall of heart)', startFrom='trunk',
                           shiftFromTrunkMM=(np.linalg.inv(M) @ H)[:3, 3].__mul__(1000).round(2).tolist(), rotationFromTrunkDeg=rotation_deg(M, H), **stats)
    for limb, bones in LIMB_BONES.items():
        nodes, sources[limb] = atlas_nodes(limb)
        for s, side in SIDE.items():
            pairs = [(f'{z}.{s}', f'b|{a}' + ('' if side == 'right' else '_left')) for z, a in bones]
            group = pairs[:GROUP_BONES[limb]]
            G, gstats = icp(np.vstack([zv(z) for z, _ in group]), np.vstack([nodes[a].vertices for _, a in group]), start)
            result[f'{limb}_{side}'] = dict(matrix=G.tolist(), bones=[a for _, a in group], **gstats)
            for z, a in pairs:
                B, bstats = icp(zv(z), nodes[a].vertices, G)
                result[f'{limb}_{side}:{z}'] = dict(matrix=B.tolist(), atlasBone=a, zBone=z, fromGroupShiftMM=((np.linalg.inv(G) @ B)[:3, 3] * 1000).round(2).tolist(),
                                                    fromGroupRotationDeg=rotation_deg(G, B), **bstats)
            # A small hand/foot bone whose fit departs from its neighbours (ICP slid onto another surface) is not a carrier.
            distal = [f'{limb}_{side}:{z}' for z, _ in pairs[GROUP_BONES[limb]:]]
            median = np.median([result[k]['fromGroupShiftMM'] for k in distal], axis=0)
            for k in distal:
                result[k]['outlier'] = bool(np.linalg.norm(np.array(result[k]['fromGroupShiftMM']) - median) > 8.0)
    write_json(run / 'z-registration.json', dict(source=SOURCE, export=dict(file=EXPORT.relative_to(ROOT).as_posix(), sha256=sha(EXPORT)), start=START.relative_to(ROOT).as_posix(), method='rigid ICP, no scale or reflection',
                                                 atlasGeometry=sources, heartSource=dict(file='site/models/bodyparts3d-3.0/cardiovascular/cv_heart.glb', sha256=sha(CV / 'cv_heart.glb')),
                                                 transforms=result))
    print(json.dumps({k: {x: v[x] for x in ('medianMM', 'p95MM')} for k, v in result.items()}, indent=0))


def load_registration(run):
    return json.loads((run / 'z-registration.json').read_text(encoding='utf8'))['transforms']


def blended(points, carriers):
    """Inverse-distance (power 4) blend of rigid bone transforms; carriers = [(Z bone vertices, matrix)]."""
    points = np.asarray(points, dtype=float)
    d = np.stack([cKDTree(v).query(points)[0] for v, _ in carriers], 1) + 1e-4
    w = 1 / d ** 4
    w /= w.sum(1, keepdims=True)
    moved = np.stack([trimesh.transform_points(points, np.array(m)) for _, m in carriers], 1)
    return np.einsum('ij,ijk->ik', w, moved), w


def centreline(row):
    pts, radii, ends = [], [], []
    depth = row['curve']['bevel_depth']
    for spline in row['curve']['splines']:
        ends += [len(pts), len(pts) + len(spline['points']) - 1]
        for p in spline['points']:
            pts.append(p['co']); radii.append(p['radius'] * depth)
    return np.array(pts), np.array(radii), sorted(set(ends))


def signed_inside(mesh, samples=200000):
    pts, faces = trimesh.sample.sample_surface(mesh, samples, seed=11)
    tree, normals = cKDTree(pts), mesh.face_normals[faces]
    def test(points):
        d, i = tree.query(points)
        return np.einsum('ij,ij->i', points - pts[i], normals[i]) < 0, d
    return test


def vessels(run, Z):
    reg = load_registration(run)
    BUILD.mkdir(parents=True, exist_ok=True)
    zv = lambda n: np.array(Z[n]['vertices'])
    atlas = {sec: atlas_nodes(sec)[0] for sec in ('arm', 'leg', 'trunk')}
    bone_tests = {}
    rows = {}
    for card, (zname, section, carrier, parent) in VESSELS.items():
        row = Z[zname]
        V, F = np.array(row['vertices']), np.array(row['faces'])
        if row['determinant'] < 0:
            F = F[:, ::-1]  # authored mirror objects: keep outward winding after world transform
        line, radii, ends = centreline(row)
        if carrier in ('arm', 'leg'):
            side = 'right' if zname.endswith('.r') else 'left'
            s = zname[-1]
            bones = [z for z, _ in LIMB_BONES[carrier] if not reg[f'{carrier}_{side}:{z}.{s}'].get('outlier')]
            carriers = [(zv(f'{z}.{s}'), reg[f'{carrier}_{side}:{z}.{s}']['matrix']) for z in bones]
            if carrier == 'arm':  # the axillary vessels begin at the first rib
                carriers.append((np.vstack([zv(f'First rib.{s}'), zv(f'Second rib.{s}')]), reg['trunk']['matrix']))
            moved, weights = blended(V, carriers)
            moved_line, _ = blended(line, carriers)
            dominant = [bones[i] if i < len(bones) else 'ribs' for i in np.bincount(weights.argmax(1), minlength=len(carriers)).argsort()[::-1][:2]]
        else:
            M = np.array(reg[carrier]['matrix'])
            moved, moved_line, dominant = trimesh.transform_points(V, M), trimesh.transform_points(line, M), [carrier]
            side = 'unseparated'
        mesh = trimesh.Trimesh(moved, F, process=False)
        # Review: side, centreline inside atlas bones, continuity with the parent vessel, calibre.
        nodes = atlas[section]
        inside_any, depth, nearest_bone = np.zeros(len(moved_line), bool), np.zeros(len(moved_line)), {}
        for name, bone in nodes.items():
            if not name.startswith('b|'):
                continue
            if np.min(np.linalg.norm(bone.bounds.mean(0) - moved_line.mean(0))) > 0.6:
                continue
            key = (section, name)
            if key not in bone_tests:
                bone_tests[key] = signed_inside(bone)
            inside, dist = bone_tests[key](moved_line)
            hit = inside & (dist < 0.02)
            depth = np.where(hit, np.maximum(depth, dist), depth)
            inside_any |= hit
            nearest_bone[name[2:]] = round(float(dist.min() * 1000), 1)
        review = dict(zObject=zname, section=section, carrier=carrier, dominantCarriers=dominant, vertices=len(moved), triangles=len(F),
                      centroidXmm=round(float(moved[:, 0].mean() * 1000), 1),
                      diameterMM=[round(float(radii.min() * 2000), 1), round(float(radii.max() * 2000), 1)],
                      centrelineInsideBone=int(inside_any.sum()), centrelinePoints=len(moved_line), maxDepthInBoneMM=round(float(depth.max() * 1000), 2),
                      splineEnds=len(ends),
                      nearestBonesMM=dict(sorted(nearest_bone.items(), key=lambda kv: kv[1])[:3]))
        review['sideOK'] = side == 'unseparated' or (review['centroidXmm'] < 0) == (side == 'right')
        rows[card] = dict(review=review, line=moved_line, radii=radii, ends=ends, mesh=mesh, parent=parent)
    # Continuity: proximal end of each vessel to its parent (atlas BodyParts3D model or another registered vessel).
    published = {}
    for card, item in rows.items():
        parent = item['parent']
        if parent in rows:
            target = np.asarray(rows[parent]['mesh'].vertices)
            kind = 'registered Z-Anatomy vessel'
        elif (CV / f'{parent}.glb').exists():
            target = trimesh.sample.sample_surface(cv_mesh(parent), 50000, seed=5)[0]
            kind = 'atlas BodyParts3D model'
        else:
            item['review']['continuity'] = dict(parent=parent, status='parent without model')
            continue
        tree = cKDTree(target)
        d = tree.query(item['line'][item['ends']])[0] * 1000
        surface = tree.query(np.asarray(item['mesh'].vertices))[0] * 1000
        # Gap between the nearest spline end (centre) and the parent surface, minus this vessel's radius there.
        j = int(np.argmin(d))
        item['review']['continuity'] = dict(parent=parent, parentKind=kind, nearestEndToParentMM=round(float(d[j]), 1),
                                            gapMM=round(max(0.0, float(d[j] - item['radii'][item['ends'][j]] * 1000)), 1),
                                            nearestSurfaceMM=round(float(surface.min()), 1))
    for card, item in rows.items():
        np.savez(BUILD / f'{card}.npz', vertices=np.asarray(item['mesh'].vertices), faces=np.asarray(item['mesh'].faces), line=item['line'], radii=item['radii'])
        published[card] = item['review']
    write_json(run / 'z-vessel-review.json', dict(method='bone-blended rigid transforms (limbs), rib-cage or heart transform (trunk)', vessels=published))
    for card, r in published.items():
        c = r.get('continuity', {})
        print(card.ljust(30), 'side', r['sideOK'], 'diam', r['diameterMM'], 'inBone', r['centrelineInsideBone'], r['maxDepthInBoneMM'], 'ends', r['splineEnds'],
              'gap', c.get('gapMM'), 'surf', c.get('nearestSurfaceMM'), 'near', r['nearestBonesMM'])


MASK_DIR = CV / 'masks'
VESSEL_STUBS = ['cv_v_cava_superior', 'cv_v_cava_inferior', 'cv_v_pulmonary_veins', 'cv_a_aorta_ascending', 'cv_a_pulmonary_arteries']
CHAMBER_MARGIN_MM, CHAMBER_MAX_MM, STUB_MM = 1.0, 3.0, 1.5
TRUNK_MM = 4.0


def face_mask(parent, faces, method, extra):
    path = CV / f'{parent}.glb'
    return dict(parent=parent, parentFile=path.relative_to(ROOT / 'site').as_posix(), parentSha256=sha(path),
                parentFaces=int(extra.pop('parentFaces')), faces=sorted(int(f) for f in faces), faceCount=int(len(faces)), method=method, **extra)


def masks(run, Z):
    """Face masks of published BodyParts3D meshes; the meshes themselves are not changed."""
    reg = load_registration(run)
    H = np.array(reg['heart']['matrix'])
    out, review = {}, {}
    heart = cv_mesh('cv_heart')
    centres = heart.triangles_center
    D = np.stack([cKDTree(trimesh.transform_points(np.array(Z[z]['vertices']), H)).query(centres)[0] * 1000 for z in CHAMBERS.values()], 1)
    best, order = np.sort(D, 1), D.argmin(1)
    stub = np.zeros(len(centres), bool)
    for v in VESSEL_STUBS:
        stub |= cKDTree(trimesh.sample.sample_surface(cv_mesh(v), 200000, seed=2)[0]).query(centres)[0] * 1000 < STUB_MM
    confident = (best[:, 1] - best[:, 0] >= CHAMBER_MARGIN_MM) & (best[:, 0] <= CHAMBER_MAX_MM) & ~stub
    for i, card in enumerate(CHAMBERS):
        faces = np.where(confident & (order == i))[0]
        out[card] = face_mask('cv_heart', faces, 'nearest registered Z-Anatomy chamber surface', dict(
            parentFaces=len(heart.faces), zObject=CHAMBERS[card], marginMM=CHAMBER_MARGIN_MM, maxDistanceMM=CHAMBER_MAX_MM,
            excludedNearVesselModelsMM=STUB_MM, areaCm2=round(float(heart.area_faces[faces].sum() * 1e4), 1)))
    review['heart'] = dict(faces=len(heart.faces), confident=int(confident.sum()), ambiguous=int(((best[:, 1] - best[:, 0]) < CHAMBER_MARGIN_MM).sum()),
                           tooFar=int((best[:, 0] > CHAMBER_MAX_MM).sum()), vesselContact=int(stub.sum()),
                           registration={k: reg['heart'][k] for k in ('medianMM', 'p95MM', 'shiftFromTrunkMM', 'rotationFromTrunkDeg')})
    # Pulmonary trunk inside the combined BodyParts3D pulmonary arterial tree.
    tree = cv_mesh('cv_a_pulmonary_arteries')
    zt = trimesh.transform_points(np.array(Z['Pulmonary trunk']['vertices']), H)
    axis = np.linalg.svd(zt - zt.mean(0))[2][0]
    proj, span = (tree.triangles_center - zt.mean(0)) @ axis, (zt - zt.mean(0)) @ axis
    near = cKDTree(zt).query(tree.triangles_center)[0] * 1000
    faces = np.where((near <= TRUNK_MM) & (proj >= span.min()) & (proj <= span.max()))[0]
    out['cv_a_pulmonary_trunk'] = face_mask('cv_a_pulmonary_arteries', faces, 'faces of the combined tree within 4 mm of the registered Z-Anatomy pulmonary trunk and inside its axial extent',
                                            dict(parentFaces=len(tree.faces), zObject='Pulmonary trunk', maxDistanceMM=TRUNK_MM, lengthMM=round(float(np.ptp(span) * 1000), 1),
                                                 areaCm2=round(float(tree.area_faces[faces].sum() * 1e4), 1)))
    # Thoracic / abdominal aorta: the BodyParts3D descending aorta divided at the lower border of the atlas T12 body.
    trunk = atlas_nodes('trunk')[0]
    t12 = np.asarray(trunk['b|thoracic_12'].vertices)
    body = t12[(t12[:, 2] >= np.median(t12[:, 2])) & (np.abs(t12[:, 0] - np.median(t12[:, 0])) < 0.015)]
    level = float(np.percentile(body[:, 1], 2))
    aorta = cv_mesh('cv_a_aorta_descending')
    cy = aorta.triangles_center[:, 1]
    zline = trimesh.transform_points(centreline(Z['Thoracic aorta'])[0], np.array(reg['trunk']['matrix']))
    diaphragm = trunk.get('m|thorax_diaphragm|') or trunk.get('m|thorax_diaphragm')
    hiatus = None
    if diaphragm is not None:
        rows = aorta.vertices[np.argsort(aorta.vertices[:, 1])]
        dd = cKDTree(np.asarray(diaphragm.vertices)).query(aorta.vertices)[0] * 1000
        close = aorta.vertices[dd < 3.0]
        hiatus = dict(lowestContactY=round(float(close[:, 1].min()), 4), highestContactY=round(float(close[:, 1].max()), 4)) if len(close) else None
    for card, faces in (('cv_a_aorta_thoracic', np.where(cy >= level)[0]), ('cv_a_aorta_abdominal', np.where(cy < level)[0])):
        out[card] = face_mask('cv_a_aorta_descending', faces, 'descending aorta divided by the horizontal plane at the lower border of the atlas T12 vertebral body',
                              dict(parentFaces=len(aorta.faces), planeY=round(level, 4), areaCm2=round(float(aorta.area_faces[faces].sum() * 1e4), 1)))
    review['aorta'] = dict(planeY=round(level, 4), aortaY=[round(float(aorta.bounds[0][1]), 4), round(float(aorta.bounds[1][1]), 4)],
                           zAnatomyThoracicEndY=round(float(zline[:, 1].min()), 4), diaphragmContact=hiatus)
    MASK_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for card, mask in out.items():
        data = (json.dumps(mask, separators=(',', ':')) + '\n').encode()
        target = MASK_DIR / f'{card}.json'
        if target.exists():
            assert target.read_bytes() == data, f'Refusing to overwrite {target}'
        else:
            target.write_bytes(data)
        summary[card] = dict(file=target.relative_to(ROOT / 'site').as_posix(), sha256=hashlib.sha256(data).hexdigest(),
                             **{k: v for k, v in mask.items() if k not in ('faces',)})
    write_json(run / 'z-mask-review.json', dict(review=review, masks=summary))
    print(json.dumps(dict(review=review, masks={k: (v['faceCount'], v['parentFaces'], v.get('areaCm2')) for k, v in summary.items()}), ensure_ascii=False, indent=1))


Z_OUT = ROOT / 'site/models/z-anatomy/cardiovascular'
MAX_BONE_DEPTH_MM, MAX_GAP_MM = 2.0, 10.0
Z_LICENCE = """Z-Anatomy — Models of human anatomy, https://github.com/Z-Anatomy/Models-of-human-anatomy (commit 04d15340bad66394659c0e3b3ff9d9bb0924f6ca, Startup.blend).
Licence: Creative Commons Attribution-ShareAlike 4.0 International, https://creativecommons.org/licenses/by-sa/4.0/ (Z-Anatomy License.txt; the NC exceptions there cover the inner ear and kidney sets, not these objects).
Z-Anatomy builds on BodyParts3D (© DBCLS, CC BY-SA 2.1 Japan).
Changes: Blender evaluation of the authored vessel curves (bevel surface) and leaflet meshes in world space; rigid registration to the atlas bones
(limb vessels: inverse-distance blend of per-bone rigid transforms; trunk: rib cage; heart: heart wall); winding fixed for mirrored source objects;
smooth normals. No reshaping, smoothing or decimation. Derived files remain CC BY-SA 4.0; preserve attribution and licence; no endorsement implied.
Educational schematic models: vessel course and calibre follow the source author's curves, not a segmented specimen; junctions with the
BodyParts3D models and relations to the atlas muscles are approximate.
Учебные схематические модели Z-Anatomy: ход и диаметр сосудов — по авторским кривым источника, стыки приблизительны.
"""


def source_penetration(Z, zname, carrier):
    """Depth (mm) of the vessel centreline inside the Z-Anatomy source bones themselves."""
    line = centreline(Z[zname])[0]
    s = zname[-1]
    deepest = 0.0
    for z, _ in LIMB_BONES[carrier]:
        row = Z[f'{z}.{s}']
        faces = np.array(row['faces'])
        mesh = trimesh.Trimesh(np.array(row['vertices']), faces[:, ::-1] if row['determinant'] < 0 else faces, process=False)
        inside, dist = signed_inside(mesh)(line)
        hit = inside & (dist < 0.02)
        if hit.any():
            deepest = max(deepest, float(dist[hit].max() * 1000))
    return round(deepest, 2)


def glb_of(card, vertices, faces):
    from geometry_export_guard import stable_vertex_normals
    mesh = trimesh.Trimesh(np.asarray(vertices, dtype=np.float64), np.asarray(faces), process=False)
    mesh.merge_vertices()
    mesh.vertex_normals = stable_vertex_normals(mesh.vertices, mesh.faces)
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name='s|' + card, geom_name='s|' + card)
    return scene.export(file_type='glb', include_normals=True), mesh


def publish(run, Z):
    review = json.loads((run / 'z-vessel-review.json').read_text(encoding='utf8'))['vessels']
    reg = load_registration(run)
    Z_OUT.mkdir(parents=True, exist_ok=True)
    admitted, excluded, files = {}, {}, []
    for card, r in review.items():
        reasons, notes = [], []
        if not r['sideOK']:
            reasons.append('wrong side')
        if r['maxDepthInBoneMM'] > MAX_BONE_DEPTH_MM:
            source = source_penetration(Z, r['zObject'], r['carrier']) if r['carrier'] in LIMB_BONES else 0.0
            if source >= MAX_BONE_DEPTH_MM:
                notes.append(f'В источнике Z-Anatomy осевая линия сосуда сама проходит в кости на {source} мм; после переноса — {r["maxDepthInBoneMM"]} мм.')
                r['sourcePenetrationMM'] = source
            else:
                reasons.append(f'centreline {r["maxDepthInBoneMM"]} mm inside an atlas bone')
        gap = r.get('continuity', {}).get('gapMM')
        if gap is not None and gap > MAX_GAP_MM:
            reasons.append(f'{gap} mm from its parent vessel {r["continuity"]["parent"]}')
        elif gap:
            notes.append(f'Зазор до модели «{r["continuity"]["parent"]}» около {gap} мм.')
        if reasons:
            excluded[card] = dict(reasons=reasons, review=r)
            continue
        arrays = np.load(BUILD / f'{card}.npz')
        data, mesh = glb_of(card, arrays['vertices'], arrays['faces'])
        target = Z_OUT / f'{card}.glb'
        if target.exists():
            assert target.read_bytes() == data, f'Refusing to overwrite {target}'
        else:
            target.write_bytes(data)
        admitted[card] = dict(file=target.relative_to(ROOT / 'site').as_posix(), sha256=hashlib.sha256(data).hexdigest(), zObject=r['zObject'],
                              triangles=int(len(mesh.faces)), kind='vessel-curve', notes=notes, review=r)
    # Aortic valve: the three Z-Anatomy cusps registered with the heart transform.
    H = np.array(reg['heart']['matrix'])
    vs, fs, off = [], [], 0
    for z in VALVE['cv_valve_aortic']:
        row = Z[z]
        faces = np.array(row['faces'])
        faces = faces[:, ::-1] if row['determinant'] < 0 else faces
        vs.append(trimesh.transform_points(np.array(row['vertices']), H)); fs.append(faces + off); off += len(row['vertices'])
    V, F = np.vstack(vs), np.vstack(fs)
    aorta = cv_mesh('cv_a_aorta_ascending')
    to_aorta = cKDTree(trimesh.sample.sample_surface(aorta, 100000, seed=4)[0]).query(V)[0] * 1000
    to_lv = cKDTree(trimesh.transform_points(np.array(Z['Left ventricle']['vertices']), H)).query(V)[0] * 1000
    valve_review = dict(cusps=VALVE['cv_valve_aortic'], toAscendingAortaMedianMM=round(float(np.median(to_aorta)), 2),
                        toAscendingAortaMinMM=round(float(to_aorta.min()), 2), toLeftVentricleMedianMM=round(float(np.median(to_lv)), 2),
                        heartRegistration={k: reg['heart'][k] for k in ('medianMM', 'p95MM')})
    if valve_review['toAscendingAortaMedianMM'] <= 3.0:
        data, mesh = glb_of('cv_valve_aortic', V, F)
        target = Z_OUT / 'cv_valve_aortic.glb'
        if target.exists():
            assert target.read_bytes() == data, f'Refusing to overwrite {target}'
        else:
            target.write_bytes(data)
        admitted['cv_valve_aortic'] = dict(file=target.relative_to(ROOT / 'site').as_posix(), sha256=hashlib.sha256(data).hexdigest(),
                                           zObject=' + '.join(VALVE['cv_valve_aortic']), triangles=int(len(mesh.faces)), kind='leaflet-meshes',
                                           notes=['Три полулунные заслонки Z-Anatomy, совмещённые со стенкой сердца атласа; лежат у корня восходящей аорты.'],
                                           review=valve_review)
    else:
        excluded['cv_valve_aortic'] = dict(reasons=['cusps not at the aortic root'], review=valve_review)
    licence = Z_LICENCE + '\nFiles: ' + '; '.join(f'{k}.glb ({v["zObject"]})' for k, v in admitted.items()) + '\n'
    for name, data in (('LICENSE-MODELS.txt', licence.encode('utf8')),
                       ('provenance.json', (json.dumps(dict(source='Z-Anatomy/Models-of-human-anatomy@04d15340bad66394659c0e3b3ff9d9bb0924f6ca', blend=SOURCE,
                                                            license='CC BY-SA 4.0', evidence=run.relative_to(ROOT).as_posix(),
                                                            registration={k: {x: v[x] for x in ('medianMM', 'p95MM')} for k, v in reg.items()},
                                                            files={k: {x: v[x] for x in ('file', 'sha256', 'zObject', 'triangles', 'kind')} for k, v in admitted.items()},
                                                            educationalAcceptance=True, fullAnatomicalAcceptance=False), ensure_ascii=False, indent=1) + '\n').encode('utf8'))):
        target = Z_OUT / name
        if target.exists():
            assert target.read_bytes() == data, f'Refusing to overwrite {target}'
        else:
            target.write_bytes(data)
    write_json(run / 'z-publish.json', dict(rule=dict(maxCentrelineDepthInBoneMM=MAX_BONE_DEPTH_MM, maxGapToParentMM=MAX_GAP_MM,
                                                       sourceDefectsKept=True), admitted=admitted, excluded=excluded))
    print(json.dumps(dict(admitted=len(admitted), excluded={k: v['reasons'] for k, v in excluded.items()},
                          notes={k: v['notes'] for k, v in admitted.items() if v['notes']}), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    stage, run = sys.argv[1], Path(sys.argv[2]).resolve()
    Z = json.loads(EXPORT.read_text(encoding='utf8'))['objects']
    {'register': register, 'vessels': vessels, 'masks': masks, 'publish': publish}[stage](run, Z)

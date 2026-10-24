"""Deterministic, source-bound annotation recipes. Geometry checks never grant admission.

Build to a unique evidence directory. Publishing requires explicit digest-bound decisions.
Only exact main/fallback vertex and oriented-face bijections are supported, not registration
between specimens. The catalogue and source snapshots are checked against current assets.
"""
import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'source-mask-recipes-v1'

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local_path(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Path outside project')
    return path

def read_json(name):
    return json.loads(local_path(name).read_text(encoding='utf8'))

def checked_json(ref):
    path = local_path(ref['path'])
    if file_hash(path) != ref['sha256']:
        raise ValueError('Changed annotation/source snapshot: ' + ref['path'])
    return json.loads(path.read_text(encoding='utf8'))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def edges_of(faces):
    return Counter(tuple(sorted((int(a), int(b)))) for f in faces for a, b in zip(f, np.roll(f, -1)))

def component_count(edges):
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b); graph[b].add(a)
    unseen = set(graph); count = 0
    while unseen:
        count += 1; todo = [unseen.pop()]
        while todo:
            new = graph[todo.pop()] & unseen
            unseen.difference_update(new); todo.extend(new)
    return count

def select(recipe, row):
    """No pin-distance selectors. Inputs are explicit reviewed source indices or whole named primitives."""
    selector = recipe['selector']; kind = selector['kind']
    if kind == 'named_primitive':
        require(selector['name'] == row['mesh'] and selector['wholeOwner'] is True,
                'Named primitive must identify a whole owner, never an inferred bone part')
        return list(range(len(row['indices']) // 3)), []
    require(kind in ('indexed_surface', 'edge_cycle', 'edge_path'), 'Unknown selector')
    value = checked_json(selector['annotation'])
    for key in selector['pointer']:
        value = value[key]
    return (value, []) if kind == 'indexed_surface' else ([], value)

def validate_mask(recipe, row, faces, edges):
    v = np.asarray(row['positions']).reshape(-1, 3)
    f = np.asarray(row['indices']).reshape(-1, 3)
    require(np.isfinite(v).all(), 'Nonfinite source vertices')
    require(bool(faces) != bool(edges), 'Select faces OR edges')
    require(all(type(i) is int and 0 <= i < len(f) for i in faces), 'Invalid face index')
    require(len(set(faces)) == len(faces), 'Duplicate face IDs')
    require(all(len(e) == 2 and all(type(i) is int and 0 <= i < len(v) for i in e) and e[0] != e[1] for e in edges), 'Invalid edge IDs')
    all_edges = edges_of(f)
    canonical = [tuple(sorted(e)) for e in edges]
    require(len(set(canonical)) == len(canonical), 'Duplicate edge')
    require(all(e in all_edges for e in canonical), 'Edge not in original source')
    selected = f[faces] if faces else np.empty((0, 3), dtype=int)
    boundary = sorted(e for e, n in edges_of(selected).items() if n == 1)
    points = np.unique(selected) if faces else np.unique(edges)
    side = recipe.get('side')
    if side in ('left', 'right'):
        require(bool(np.all(v[points, 0] > 0) if side == 'left' else np.all(v[points, 0] < 0)), 'Wrong side in published Three.js frame')
    if faces:
        area = trimesh.Trimesh(v, selected, process=False).area_faces
        require(np.all(area > 0), 'Degenerate selected triangle')
        require(len({tuple(sorted(x)) for x in selected}) == len(faces), 'Duplicate triangle geometry')
        require(component_count(edges_of(selected)) == 1, 'Disconnected surface requires separate recipes')
        require(max(edges_of(selected).values()) <= 2, 'Nonmanifold selected edge')
    else:
        degree = Counter(i for e in edges for i in e)
        require(component_count(edges) == 1, 'Disconnected line')
        if recipe['selector']['kind'] == 'edge_cycle':
            require(all(n == 2 for n in degree.values()), 'Contour must be a simple cycle')
        else:
            require(sum(n == 1 for n in degree.values()) == 2 and all(n <= 2 for n in degree.values()), 'Path must have two endpoints and no branches')
    return dict(faces=len(faces), edges=len(edges), vertices=len(points),
                areaM2=float(area.sum()) if faces else None,
                boundaryEdges=[list(e) for e in boundary],
                components=1, sideChecked=side, anatomyProven=False)

def exact_remap(a, b):
    d, mapping = cKDTree(np.asarray(b['positions']).reshape(-1, 3)).query(np.asarray(a['positions']).reshape(-1, 3))
    require(max(d) == 0 and len(set(mapping)) == len(mapping) == len(b['positions']) // 3, 'No approximate transfer')
    af = np.asarray(a['indices']).reshape(-1, 3); bf = np.asarray(b['indices']).reshape(-1, 3)
    key = lambda f: min(tuple(f), tuple(np.roll(f, 1)), tuple(np.roll(f, 2)))
    lookup = {key(f): i for i, f in enumerate(bf)}
    require(len(lookup) == len(bf) == len(af), 'Different oriented topology')
    mapped = [lookup.get(key(mapping[f])) for f in af]
    require(None not in mapped and len(set(mapped)) == len(af), 'Winding/topology changed')
    return mapping, mapped

def binding(region):
    return {k: region[k] for k in ('id', 'bone', 'pinIds', 'variants')}

def admission(recipe, region, review):
    if review:
        require(review['recipeHash'] == digest(recipe), 'Decision invalidated by recipe change')
        require(review['level'] in ('confirmed', 'educational', 'draft'), 'Invalid admission level')
        require(review['scope'] and review['reason'] and review['reviewedBy'] and review['date'], 'Incomplete decision')
        if review['level'] != 'draft':
            require(review['explicitAdmission'] is True and review['evidence'] and recipe['refs'] and recipe['notice'], 'Missing explicit evidence/admission/limitation')
            require(all(local_path(p).is_file() for p in review['evidence']), 'Missing review evidence')
        level = review['level']
    else:
        level = 'draft'
    return dict(level=level, explicit=bool(review and review.get('explicitAdmission')),
                scope=review['scope'] if review else 'unreviewed', reviewId=recipe['id'],
                bindingHash=digest(binding(region)))

def compile_batch(config, decisions, catalogue):
    require(config['schema'] == VERSION, 'Unknown recipe schema')
    require(decisions['schema'] == 'explicit-mask-admissions-v1', 'Unknown admission schema')
    require(len({r['id'] for r in config['recipes']}) == len(config['recipes']), 'Duplicate region ID')
    require(len({d['id'] for d in decisions['decisions']}) == len(decisions['decisions']), 'Duplicate decision ID')
    for path, expected in catalogue['sources'].items():
        require(file_hash(local_path(path)) == expected, 'Stale catalogue snapshot: ' + path)
    pins = {p['id']: p for p in catalogue['pins']}
    require(len(pins) == len(catalogue['pins']), 'Duplicate catalogue ID')
    resources = [checked_json(ref) for ref in config['resources']]
    require(bool(resources), 'At least one source variant is required')
    for resource in resources:
        payload = local_path('site/' + resource['file']).read_bytes()
        if resource.get('encoding', 'base64' if resource['file'].endswith('.txt') else 'binary') == 'base64':
            payload = base64.b64decode(payload)
        require(hashlib.sha256(payload).hexdigest() == resource['sha256'], 'Published GLB changed')
    reviews = {d['id']: d for d in decisions['decisions']}
    require(set(reviews) <= {r['id'] for r in config['recipes']}, 'Orphaned decision')
    regions = []; checks = []; guides = []
    cache = {}
    for recipe in config['recipes']:
        require(recipe['bone'] in catalogue['bones'], 'Unknown bone')
        require(recipe['pinIds'] and len(set(recipe['pinIds'])) == len(recipe['pinIds']), 'Invalid pin bindings')
        require(all(p in pins and pins[p]['b'] == recipe['bone'] for p in recipe['pinIds']), 'Incorrect catalogue owner/ID')
        rows = []
        for resource in resources:
            matches = [r for r in resource['rows'] if r['bone'] == recipe['bone']]
            require(len(matches) == 1, 'Ambiguous source primitive; split source before annotation')
            rows.append(matches[0])
        a = rows[0]
        faces, edges = select(recipe, a)
        metrics = validate_mask(recipe, a, faces, edges)
        variants = []
        for i, (row, resource) in enumerate(zip(rows, resources)):
            ff, ee = faces, edges
            if i:
                key = (recipe['bone'], i)
                if key not in cache:
                    cache[key] = exact_remap(a, row)
                mapping, mapped = cache[key]
                ff, ee = [int(mapped[j]) for j in faces], [[int(mapping[j]) for j in e] for e in edges]
            validate_mask(recipe, row, ff, ee)
            variants.append(dict(file=resource['file'], sourceHash=resource['sha256'], geometryHash=row['geometryHash'], primitive=0,
                                 faceCount=len(row['indices']) // 3, vertexCount=len(row['local']) // 3, faces=ff, edges=ee))
        region = {k: v for k, v in recipe.items() if k not in ('selector',)}
        region['variants'] = variants
        review = reviews.get(recipe['id'])
        region['admission'] = admission(recipe, region, review)
        region['provenance'] = dict(algorithm=VERSION, recipeHash=digest(recipe), decisionHash=digest(review) if review else None,
                                    sourceSnapshots=config['resources'], selector=recipe['selector'])
        regions.append(region)
        checks.append(dict(id=recipe['id'], admission=region['admission']['level'], **metrics))
        if faces:
            guides.append(dict(id=recipe['id'] + ':technical-boundary', bone=recipe['bone'],
                               parent=recipe['id'], edges=metrics['boundaryEdges'], status='review-only',
                               notice='Техническая граница выборки, не анатомический контур. В атлас не экспортируется.'))
    return dict(schema='anatomical-regions-v2', completeAnatomicalAcceptance=False, regions=regions), checks, guides

def write_new(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, separators=(',', ':')); stream.write('\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run'); parser.add_argument('--publish', action='store_true')
    parser.add_argument('--publish-only', action='store_true', help='Revalidate saved candidates before publication')
    parser.add_argument('--config', default='scripts/skull_region_recipes.json')
    parser.add_argument('--decisions', default='scripts/skull_region_admissions.json')
    args = parser.parse_args(); run = local_path(args.run)
    require(run.is_dir(), 'Allocate unique evidence run first')
    config = read_json(args.config); decisions = read_json(args.decisions)
    manifest, checks, guides = compile_batch(config, decisions, json.loads((run / 'catalogue.json').read_text(encoding='utf8')))
    # Snapshot all inputs before publication, never overwrite historical evidence.
    if args.publish_only:
        for name, value in [('recipes.json', config), ('admissions.json', decisions), ('mask-candidates.json', manifest), ('technical-boundaries.json', guides)]:
            require(json.loads((run / name).read_text(encoding='utf8')) == value, 'Saved evidence differs: ' + name)
    else:
        write_new(run / 'recipes.json', config); write_new(run / 'admissions.json', decisions)
        write_new(run / 'mask-candidates.json', manifest)
        write_new(run / 'mask-validation.json', dict(algorithm=VERSION, checks=checks, guideCount=len(guides), noAutomaticAdmission=True))
        write_new(run / 'technical-boundaries.json', guides)
    if args.publish or args.publish_only:
        require(not (run / 'publication.json').exists(), 'This run has already been published')
        # Atomic replacement of the GENERATED annotation only; never a model or pin file.
        target = ROOT / 'site/skull-region-masks.json'
        temporary = target.with_suffix('.json.pending')
        write_new(temporary, manifest); temporary.replace(target)
        write_new(run / 'publication.json', dict(manifestHash=digest(manifest), fullAnatomicalAcceptance=False))
    print(json.dumps(dict(regions=len(checks), admissions=dict(Counter(x['admission'] for x in checks)), guides=len(guides), published=args.publish or args.publish_only)))

if __name__ == '__main__':
    main()

"""Independent structural/evidence-preservation audit of the educational release.

This checks the published inventory against upstream registries. It does not
replace source reading, anatomical review, or physical-device testing.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import struct
import sys
from threading import Thread
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


def read(name):
    return json.loads((SITE / name).read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def browser_scope_review():
    from playwright.sync_api import sync_playwright

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            executable = os.environ.get('ATLAS_CHROMIUM') or 'C:/Program Files/Google/Chrome/Application/chrome.exe'
            browser = p.chromium.launch(executable_path=executable, headless=True,
                                       args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            try:
                page = browser.new_page(viewport={'width':390, 'height':844})
                page.goto(f'http://127.0.0.1:{server.server_port}/skull-education.html?category=attachments&theme=dark&entry=local')
                page.wait_for_function('window.__education')
                return page.evaluate('''() => {
                  const failures=[],items=window.__education.data.entries.filter(r=>r.category==='attachments');
                  for(const r of items){
                    window.__education.select(r.id);
                    const expected=['origin','insertion'].filter(f=>r.attachment[f].evidenceAppliesTo==='parent_muscle').length;
                    const relational=document.querySelectorAll('.relations .badge').length;
                    const detailed=document.querySelectorAll('#details .badge').length;
                    if(expected!==relational||expected!==detailed)failures.push({id:r.id,expected,relational,detailed});
                    const link=document.querySelector('#card a').href;
                    if(!link.includes('/local.html?')||!link.includes('entry=local')||!link.includes('theme=dark'))failures.push({id:r.id,link});
                    if(document.documentElement.scrollWidth>innerWidth)failures.push({id:r.id,horizontalOverflow:true});
                  }
                  return {records:items.length,fields:items.length*2,failures,width:innerWidth,theme:'dark',emulationOnly:true};
                }''')
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


def audit(with_browser=False):
    failures = []
    checks = Counter()

    def check(name, condition, item=None):
        checks[name] += 1
        if not condition:
            failures.append({'check': name, 'item': item})

    data = read('skull-education.json')
    rows = data['entries']
    indexed = {r['id']: r for r in rows}
    bone = read('skull-educational-bones.json')
    extent = {r['id']: r for r in read('skull-geometry-review.json')['rows']}
    whole = {r['c']: r for r in read('skull-whole.json')['rows']}
    attachments = read('skull-attachment-education.json')
    source_attachments = {r['id']: r for r in read('skull-muscle-attachments.json')['items']}
    muscles = read('skull-muscle-reconstructions.json')
    ossicles = read('skull-openear-landmarks.json')['markers']
    variants = read('skull-study-variants.json')
    pins = json.JSONDecoder().raw_decode((SITE/'pins-head.js').read_text(encoding='utf8').split('push(...', 1)[1])[0]
    pin_ids = {r['id'] for r in pins}
    muscle_js = (SITE/'data-head.js').read_text(encoding='utf8').split('Object.assign(A.muscles,', 1)[1]
    main_muscles = json.JSONDecoder().raw_decode(muscle_js)[0]

    expected = {'bones': 507, 'variants': 14, 'whole': 97, 'muscles': 19, 'attachments': 78, 'ossicles': 13}
    check('unique_728_records', len(rows) == len(indexed) == 728)
    check('expected_categories', Counter(r['category'] for r in rows) == expected)
    check('measured_geometry_not_claimed', data['completeSkullGeometry'] is False)
    check('external_anatomist_not_claimed', data['independentAnatomistReview'] is False)
    check('physical_devices_not_claimed', data['physicalDeviceTests'] is False)
    check('educational_inventory_complete', data['educationalDispositionComplete'] is True)
    for file, expected_sha in data['sourceFiles'].items():
        check('compiled_source_hash_current', sha(SITE/file) == expected_sha, file)
    check('attachment_source_hash_current', attachments['sourceRegistrySha256'] == sha(SITE/attachments['sourceRegistry']))
    check('muscle_glb_hash_current', muscles['sha256'] == sha(SITE/muscles['asset']))

    all_models = {}
    link_counts = Counter()
    for r in rows:
        for key in ('ru', 'lat', 'code', 'known', 'unknown', 'limitations', 'guidance'):
            check('required_entry_content', bool(r[key]), r['id']+':'+key)
        check('entry_ref_urls_distinct', len({ref['url'] for ref in r['refs']}) >= 2, r['id'])
        for ref in r['refs']:
            check('reference_has_locator_title_https', bool(ref.get('locator') and ref.get('title') and ref['url'].startswith('https://')), r['id'])
        for m in r['models']:
            check('diagram_explained', bool(m['known'] and m['limitations'] and m['method'] and m['license']), m['id'])
            check('diagram_refs', len({ref['url'] for ref in m['refs']}) >= 2 and all(ref.get('locator') for ref in m['refs']), m['id'])
            check('diagram_definition_consistent', m['id'] not in all_models or all_models[m['id']] == m, m['id'])
            all_models[m['id']] = m
        for link in r['links']:
            u = urlparse(link['href']); q = parse_qs(u.query); path = u.path.lstrip('./')
            check('internal_link_file_exists', (SITE/(path or 'index.html')).is_file(), r['id']+':'+link['href'])
            if path == 'skull-education.html':
                link_counts['education'] += 1
                check('internal_education_id_exists', q.get('id', [''])[0] in indexed, r['id'])
            elif q.get('study') == ['landmark']:
                link_counts['landmark'] += 1
                check('atlas_landmark_exists', q.get('value', [''])[0] in pin_ids, r['id'])
            elif q.get('study') == ['muscle']:
                link_counts['muscle'] += 1
                bits = q.get('value', [''])[0].split(':', 1)
                check('atlas_muscle_exists', bits[0] in main_muscles, r['id'])
                if len(bits) > 1:
                    check('atlas_muscle_part_exists', bits[1] in main_muscles.get(bits[0], {}).get('parts', {}), r['id'])
            elif path == 'skull-detail.html':
                link_counts['detail'] += 1
                if q.get('from') == ['geometry']:
                    source = extent.get(q.get('bone', [''])[0]+':'+q.get('code', [''])[0])
                    i = int(q.get('assessment', ['0'])[0])
                    check('source_geometry_assessment_resolves', bool(source and i < len(source['assessments']) and source['assessments'][i]['viewer']['mode'] == q.get('mode', [''])[0]), r['id'])
                elif q.get('from') == ['whole']:
                    source = whole.get(q.get('code', [''])[0])
                    check('source_whole_launch_resolves', bool(source and source.get('launch') and source['launch']['mode'] == q.get('mode', [''])[0]), r['id'])
                elif 'marker' in q:
                    check('source_ossicle_marker_resolves', q['marker'][0] in {o['id'] for o in ossicles}, r['id'])
            elif path == 'skull-study.html' and 'code' in q:
                link_counts['variant'] += 1
                check('source_variant_code_resolves', q['code'][0] in {v['c'] for v in variants}, r['id'])

    for r in bone['records']:
        e = indexed[r['id']]
        check('bone_refs_preserved', e['refs'] == r['refs'], r['id'])
        check('bone_disposition_preserved', e['status'] == ('explanation' if r['status']=='educational_reconstruction' else r['status']), r['id'])
        check('bone_known_preserved', e['known'] == [r['known']], r['id'])
        if r['kind'] != 'whole':
            s = extent[r['id']]
            check('original_localization_preserved', e['originalLocalization'] == r['originalLocalization'] == s['localization'], r['id'])
            check('original_extent_preserved', e['originalExtentStatus'] == r['originalExtentStatus'] == s['status'], r['id'])
            check('original_geometry_claim_preserved', r['originalCompleteFeatureGeometry'] == s['completeFeatureGeometry'], r['id'])
            if e['status'] == 'source_model':
                check('source_model_requires_extent_complete', s['status'] == 'complete', r['id'])
        else:
            s = whole[r['c']]
            check('whole_text_current', r['known'] == s['description'] and r['unknown'] == s['geometry']['modelNote'], r['id'])
            check('whole_scope_preserved', (r['status'] == 'future_scope') == (not s['current']), r['id'])
            check('whole_geometry_claim_preserved', r['originalCompleteFeatureGeometry'] == s['geometry']['completeFeatureGeometry'], r['id'])

    inherited = []
    for r in attachments['items']:
        s = source_attachments[r['id']]; e = indexed['attachment:'+r['id']]
        check('attachment_fields_published_exactly', e['attachment'] == {'origin': r['origin'], 'insertion': r['insertion']}, r['id'])
        for f in ('origin', 'insertion'):
            sf = s[f]; ef = r[f]; is_parent = s['kind'] == 'part' and sf['scope'] == 'whole_muscle'
            check('attachment_source_text_scope_refs_preserved', all(ef[k] == sf[k] for k in ('text','scope','status','refs','representativeMarkerIds','parentMuscleMarkers')), r['id']+':'+f)
            check('parent_scope_correct', (ef['evidenceAppliesTo'] == 'parent_muscle') == is_parent, r['id']+':'+f)
            check('attachment_has_explanation', all(ef[k] for k in ('unknown', 'whyNoBoundary', 'learningGuidance')), r['id']+':'+f)
            check('attachment_two_independent_sources', len({x['independentSource'] for x in ef['refs']}) >= 2, r['id']+':'+f)
            check('no_attachment_area_invented', ef['completeAttachmentArea'] is False and ef['geometryStatus'] == 'no_measured_boundary', r['id']+':'+f)
            if is_parent:
                inherited.append(r['id']+':'+f)
    check('exactly_12_inherited_fields', len(inherited) == 12)

    for r in muscles['entries']:
        key = r['muscle']+(':'+r['part'] if r.get('part') else '')
        check('muscle_disposition_preserved', indexed['muscle:'+key]['status'] == 'explanation', key)
        check('muscle_refs_preserved', indexed['muscle:'+key]['refs'] == r['refs'], key)
        source_card = main_muscles[r['muscle']]
        if r.get('part'):
            source_card = source_card['parts'][r['part']]
        check('original_missing_mesh_not_promoted', source_card.get('noModel') is True, key)
    check('muscle_16_diagrams_3_explanations', Counter(r['status'] for r in muscles['entries']) == {'educational_reconstruction':16, 'explanation':3})
    for r in ossicles:
        check('ossicle_limit_preserved', indexed['ossicle:'+r['c']]['unknown'] == [r['modelNote']], r['c'])

    glb_nodes = {}
    for filename in {m['file'] for m in all_models.values()}:
        b = (SITE/filename).read_bytes()
        magic, version, length, json_len, json_type = struct.unpack('<5I', b[:20])
        check('glb_valid_header', magic == 0x46546c67 and version == 2 and length == len(b) and json_type == 0x4e4f534a, filename)
        gltf = json.loads(b[20:20+json_len])
        glb_nodes[filename] = {node.get('name') for node in gltf.get('nodes', [])}
    for m in all_models.values():
        check('all_diagram_nodes_exist', set(m['nodes']+m['contextNodes']) <= glb_nodes[m['file']], m['id'])
    check('no_displayed_diagrams', len(all_models) == 0)
    check('720_atlas_views', sum(bool(r.get('atlasView')) for r in rows) == 720)
    check('all_variants_link_to_atlas', all(r.get('atlasView') for r in rows if r['category']=='variants'))
    check('incisive_fossa_limit_describes_fossa', 'ямки' in indexed['whole:A02.1.00.060']['unknown'][0])
    check('palatine_torus_limit_describes_variant', 'варианта' in indexed['whole:A02.1.00.063']['unknown'][0])

    browser_result = browser_scope_review() if with_browser else None
    if browser_result:
        check('all_attachment_fields_render_correct_scope', not browser_result['failures'], browser_result['failures'])
    report = {'createdUtc':datetime.now(timezone.utc).isoformat(),
              'reviewType':'internal_inventory_and_evidence_preservation_review',
              'notExternalAnatomistReview':True, 'notNewAnatomicalSourceValidation':True,
              'scope':'All 728 published records and their upstream registries, 156 attachment fields, 720 atlas links, removed standalone diagrams and source freshness.',
              'status':'passed' if not failures else 'failed', 'counts':data['counts'],
              'checks':dict(checks), 'totalAssertions':sum(checks.values()), 'inheritedFields':inherited,
              'internalLinkCounts':dict(link_counts), 'failures':failures, 'browserScopeReview':browser_result,
              'inspectedFilesSha256':{f:sha(SITE/f) for f in ['skull-education.json','skull-educational-bones.json','skull-attachment-education.json','skull-muscle-attachments.json','skull-muscle-reconstructions.json','skull-whole.json','skull-geometry-review.json','skull-education.js','skull-education-model.js']},
              'limitations':['Source locators and preserved source-group identifiers checked structurally; this does not revalidate every anatomical assertion against publications.',
                             'User-authorized diagrams/explanations are accepted outcomes; no inference that all original anatomical geometry is now complete.',
                             'Browser rendering, source-reading review and publication checks are separate reports.']}
    (ROOT/'research/skull-educational-cross-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'assertions':report['totalAssertions'],'failures':failures},ensure_ascii=False))
    return not failures


if __name__ == '__main__':
    raise SystemExit(0 if audit('--browser' in sys.argv) else 1)

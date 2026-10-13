"""Publish only reviewed channel-wall meshes and source CT slice atlases."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build_head/temporal_channels'
SITE = ROOT / 'site'


def copy_checked(name, expected=None):
    source = BUILD / name
    assert source.parent == BUILD and source.is_file()
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if expected:
        assert digest == expected, name
    shutil.copyfile(source, SITE / name)
    return {'file': name, 'sha256': digest, 'bytes': source.stat().st_size}


def main():
    data = json.loads((BUILD / 'skull-temporal-channels.json').read_text(encoding='utf8'))
    assert data['license'] == 'CC BY 4.0'
    for structure in data['structures']:
        assert len(structure['refs']) >= 2
        assert all(ref['locator'] for ref in structure['refs'])
        assert not structure['completeFeatureGeometry']
    assets = [copy_checked(data['file'], data['sha256']), copy_checked(data['contextFile'], data['contextSha256'])]
    slices = json.loads((BUILD / data['slicesFile']).read_text(encoding='utf8'))
    for series in slices['series']:
        assert series['id'] in {row['id'] for row in data['structures']}
        for page in series['pages']:
            assets.append(copy_checked(page['file'], page['sha256']))
    assets += [copy_checked(data['slicesFile']), copy_checked('skull-temporal-channels.json')]
    report = {'source': data['source'], 'license': data['license'], 'assets': assets,
              'structures': len(data['structures']), 'ct_reslices': sum(len(row['frames']) for row in slices['series']),
              'full_channel_geometry_claim': False, 'main_bodyparts3d_status_changed': False}
    (ROOT / 'verify/skull-channel-assets.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    license_file = SITE / 'LICENSE-MODELS.txt'
    text = license_file.read_text(encoding='utf8')
    heading = '\n=== OpenEar: selected channel walls and CT reslices ===\n'
    if heading in text:
        before, previous = text.split(heading, 1)
        following = previous.find('\n=== ')
        text = before + (previous[following:] if following >= 0 else '')
    text += heading + '''Daniel Manuel Sieber, Peter Erfurt, Samuel John, Gabriel Ribeiro dos Santos,
Daniel Schurzig, Mads Sølvsten Sørensen, Thomas Lenarz: OpenEar (2019), ZETA.
Source: https://zenodo.org/records/1473724
License: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
Files: skull-temporal-channels*.glb/json, skull-temporal-channel-slices.json,
skull-channel-facial-slices-*.png, skull-channel-carotid-slices-*.png.
Changes: selected existing triangles of the published Bone.nrrd surface;
coordinate conversion; mesh compression; cropped surrounding bone without
added caps; oblique resampling and windowing of registered source CBCT;
optional source-mask outline and lumen-region overlays. No invented walls.
These are reviewed wall segments, not complete channels or a normative skull.
The acquisition step belongs to each frame: CBCT_Unembedded 0.25 mm or
CBCT_Embedded 0.125 mm. Registered grid 0.125 mm is not an accuracy guarantee.
'''
    license_file.write_text(text, encoding='utf8')
    print(json.dumps({k: v for k, v in report.items() if k != 'assets'}))


if __name__ == '__main__':
    main()

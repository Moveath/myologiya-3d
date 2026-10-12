"""Render native-coordinate source CBCT and segmentation checks, without remodeling."""
from pathlib import Path
import argparse
import gzip
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates, binary_erosion

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/temporal_features'


def indices(points):
    x, y, z = (np.asarray(points) * 1000).T
    return np.array([(y+1.7357300519943237)/.125,
                     (z+7.7452301979064941)/.125,
                     (19.806900024414063-x)/.125])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--full',action='store_true')
    args=parser.parse_args()
    raw = (OUT / ('CBCT_Unembedded.nrrd' if args.full else 'CBCT_Embedded.nrrd')).read_bytes()
    stop = raw.index(b'\n\n') + 2
    header = raw[:stop].decode('ascii')
    assert 'sizes: 668 587 625' in header
    assert '(-0.125,0,0) (0,-0.125,0) (0,0,0.125)' in header
    volume = np.frombuffer(gzip.decompress(raw[stop:]), dtype='<i2').reshape((625,587,668))
    del raw
    mask = np.load(ROOT / 'research/cache/complete-temporal/zeta/bone-mask.npy', mmap_mode='r')
    picks = json.loads((OUT / 'picks.json').read_text())
    checks = []
    for pick in picks:
        p = np.array(pick['p']); normal = np.array(pick['n'])
        values = [int(map_coordinates(mask, indices([p+s*normal]), order=0)[0]) for s in [-.00025,.00025]]
        checks.append({'id':pick['id'], 'faceIndexBeforeWindingFix':pick['faceIndex'],
                       'p':pick['p'], 'normalBeforeWindingFix':pick['n'],
                       'mask_minus_0_25mm':values[0], 'mask_plus_0_25mm':values[1],
                       'inward_before_fix': values == [0,1]})
        # Exact source-axis slices at source grid spacing. Screen scale: 3 px/voxel.
        radius = 64
        center = np.rint(indices([p])[:,0]).astype(int)
        sheet = Image.new('RGB',(3*384,430),'#1d2524')
        for panel, (fixed, a, b) in enumerate([(0,2,1),(1,2,0),(2,1,0)]):
            u,v=np.meshgrid(np.arange(-radius,radius),np.arange(-radius,radius))
            ix=np.tile(center[:,None,None],(1,radius*2,radius*2));ix[a]+=u;ix[b]+=v
            ct=map_coordinates(volume,ix,order=0,mode='constant',cval=-3024)
            seg=map_coordinates(mask,ix,order=0,mode='constant',cval=0)>0
            # Fixed display window, raw CBCT stored values; no claim of calibrated HU.
            gray=(np.clip((ct+500)/3000,0,1)*255).astype('uint8')
            rgb=np.repeat(gray[:,:,None],3,axis=2)
            edge=seg & ~binary_erosion(seg)
            rgb[edge]=[230,70,70]
            im=Image.fromarray(rgb).resize((384,384),Image.Resampling.NEAREST)
            sheet.paste(im,(panel*384,30));d=ImageDraw.Draw(sheet)
            d.text((panel*384+8,8),f'Native slice axis {fixed}; voxel {center[fixed]}',fill='white')
            cx=panel*384+192;cy=222
            d.line((cx-10,cy,cx+10,cy),fill='#00ffff',width=1)
            d.line((cx,cy-10,cx,cy+10),fill='#00ffff',width=1)
        kind='Full CBCT acquired 0.25 mm, registered grid 0.125 mm' if args.full else 'Embedded CBCT acquired 0.125 mm'
        ImageDraw.Draw(sheet).text((8,415),pick['id']+' | '+kind+'; red: Bone mask; cyan: candidate',fill='white')
        sheet.save(OUT / (pick['id']+('-cbct-full.png' if args.full else '-cbct.png')))
    report = {'method':'Compare triangle face normals against original binary volume at +/- 0.25 mm.',
              'source':'OpenEar ZETA, Bone.nrrd', 'checks':checks,
              'inward_count':sum(q['inward_before_fix'] for q in checks)}
    (OUT / 'bone-winding-source-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()

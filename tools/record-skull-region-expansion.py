"""Record explicit review decisions. Candidate detection never grants admission."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN='research/evidence-runs/stage6-skull-regions-expansion-2026-10-21T08-15-07-836Z-IGp5Ll'
source=json.loads((ROOT/RUN/'head-glb-source.json').read_text(encoding='utf8'))
cycles={r['id']:r for r in json.loads((ROOT/RUN/'candidate-cycles.json').read_text(encoding='utf8'))}
regions=[]
specs=[
 ('sphenoid','A02.1.05.036','Овальное отверстие','inferior-493','inferior-500',[0,-1,0],
  'Показан проекционный контур просвета снизу. Он не обозначает всю поверхность края или стенки отверстия.'),
 ('sphenoid','A02.1.05.035','Круглое отверстие','anterior-507','anterior-530',[0,0,1],
  'Показана линия контура в передней проекции на этой модели. Она не подтверждает весь ободок, короткий канал или его внутренние стенки.'),
 ('sphenoid','A02.1.05.023','Клиновидная часть верхней глазничной щели','anterior-505','anterior-525',[0,0,1],
  'Показан проекционный контур в пределах клиновидной модели. Латеральное замыкание лобной костью и полный общий контур щели не размечены. Это не сегментация всей общей структуры.'),
]
for bone,code,name,right,left,view,notice in specs:
 for side,candidate in [('right',right),('left',left)]:
  c=cycles[bone+'-'+candidate]
  regions.append(dict(id=f'{bone}:{code}:{side}',bone=bone,side=side,
   pinIds=['head_'+bone+'_'+code.replace('.','_')],status='reviewed_projection_contour',
   label=name+(' · справа' if side=='right' else ' · слева'),notice=notice,
   view=view,faces=[],edges=c['edges'],candidateId=c['id'],
   evidence=['aperture-sphenoid-anterior.png','aperture-sphenoid-superior.png','aperture-sphenoid-posterior.png'] if code!='A02.1.05.035' else ['rotundum-sphenoid-front.png','rotundum-sphenoid-back.png','rotundum-sphenoid-oblique.png'],
   refs=['https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-sphenoidale.html',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC8907938/' if code!='A02.1.05.023' else 'research/stage5-skull-batch3-report-2026-10-16.md']))
for bone,candidate,view in [('temporal_right','lateral-662',[1,0,0]),('temporal_left','lateral-729',[-1,0,0])]:
 code='A02.1.06.032';c=cycles[bone+'-'+candidate]
 regions.append(dict(id=f'{bone}:{code}',bone=bone,pinIds=['head_'+bone+'_'+code.replace('.','_')],
  status='draft_projection_contour',label='Черновой контур внутреннего слухового отверстия',
  notice='Контур перегиба поверхности у входа не отделён достоверно от стенок и дна прохода. Полная граница апертуры не принята; черновик не показывается.',
  view=view,faces=[],edges=c['edges'],candidateId=c['id'],
  evidence=['acoustic-'+bone+'-back.png','acoustic-exact-'+bone+('-left.png' if bone.endswith('right') else '-right.png')],
  refs=['https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-temporale.html','research/temporal-feature-extent-review.json']))
data=dict(schema='source-edge-review-v1',sourceRun=RUN,sourceHash=source['sha256'],reviewDate='2026-10-21',
 report='research/stage6-skull-region-expansion-2026-10-21.md',completeAnatomicalAcceptance=False,
 method='Explicit source-edge cycles reviewed in Blender; source vertex indices only; no pin-derived regions. Projection admission is not full rim/wall acceptance.',regions=regions)
(ROOT/'scripts/skull_region_expansion_annotations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print([(r['id'],r['status'],len(r['edges'])) for r in regions])

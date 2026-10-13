"""Record the targeted visual review; do not infer absence from a coarse mesh."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def build():
    manifest=read('build_head/cranial_extent/other-orbits/views.json')
    assert sha(manifest['source'])==manifest['sourceSha256']
    source_audit=read('research/new-skull-source-audit.json')
    observations={
      '01_male-cranial_maxilla':'В переднем и трёх нижнепередних видах обе глазницы доступны. Верхнемедиальная область сглажена; отдельная блоковая ость, прослеживаемая от основания до верхушки, не выделяется. Неровные края в глубине глазниц не приняты за этот передний ориентир.',
      '02_female-cranial_maxilla':'На собственных видах обеих глазниц видны гладкие верхние и медиальные стенки, местами с прерывистыми краями. Самостоятельный переднемедиальный выступ с различимыми основанием и верхушкой не подтверждён.',
      'nih-002448':'В переднем и косых нижнепередних видах область доступна с обеих сторон. Верхнемедиальная поверхность сглажена, а глубокие стенки имеют дефекты; ни один выступ не подтверждён как целая блоковая ость.'
    }
    rows=[]
    for node,observation in observations.items():
        src=next(s for s in source_audit['sources'] if any(a.get('review_node')==node for a in s.get('local_assets',[])))
        asset=next(a for a in src['local_assets'] if a.get('review_node')==node)
        assert sha(asset['file'])==asset['sha256']
        views=[v for v in manifest['records'] if v['node']==node]
        assert len(views)==4
        for v in views:
            if (ROOT/v['screenshot']).exists():assert sha(v['screenshot'])==v['screenshotSha256']
        rows.append({'source':src['id'],'title':src['title'],'sourceUrl':src['url'],'license':src['license'],'nativeFile':asset['file'],'nativeSha256':asset['sha256'],'reviewMesh':manifest['source'],'reviewMeshSha256':manifest['sourceSha256'],'node':node,'status':'not_demonstrated','observation':observation,'views':views,'geometryEdits':False,'markersAdded':0,'completeFeatureGeometry':False})
    refs=read('research/head-evidence.json')['bone_features']['A02.1.03.024']['refs']
    assert len(refs)>=2 and all(r.get('locator') for r in refs)
    out={'schemaVersion':1,'date':'2026-10-13','generatedBy':'scripts/cranial_features_variant_check.py','renderScript':manifest['script'],'code':'A02.1.03.024','bone':'frontal','ru':'Блоковая ость','lat':'spina trochlearis','scope':'Целевой региональный осмотр обеих глазниц на трёх уже разрешённо полученных моделях.','criterion':'Реально присутствующий выступ верхнемедиальной области глазницы с основанием, свободной верхушкой и различимой целой формой.','refs':refs,'records':rows,'limitations':['Отсутствие различимого рельефа в сглаженной/неполной модели не доказывает отсутствия варианта в исходном препарате.','Камеры и рамки кадрирования не являются анатомическими точками; новые маркеры не ставились.','Эти три исследовательские сетки не добавлены на сайт и не зарегистрированы на BodyParts3D.','Полный перечень TA98 на этих дополнительных моделях не проверялся.'],'completeGeometryClaim':False,'independentExpertValidation':False}
    (ROOT/'research/cranial-orbital-variant-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('3 source models / 12 views / no confirmed trochlear spine; report saved')
if __name__=='__main__':build()

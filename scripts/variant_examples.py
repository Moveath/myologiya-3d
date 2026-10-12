"""Package reviewed, openly licensed photographs/CT figures of skull variants.

These are examples from OTHER specimens, never proof of the BP3D specimen and
never counted as interactive mesh geometry. Full articles stay in local cache.
"""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/variant-figures'

# Each caption was checked against the original figure and its published caption.
EXAMPLES = [
    ('A02.1.03.007', 'metopic', 'PMC4392959', 'ISRN.ANATOMY2013-158341.001.jpg', 'Figure 1',
     'Ivan do Nascimento da Silva и соавт., 2013', '3.0',
     'Сохраняющийся лобный шов у взрослого: стрелки отмечают его ход на фотографии сухого черепа.'),
    ('A02.1.04.013', 'interparietal', 'PMC12752719', 'cureus-0017-00000098151-i01.jpg', 'Figure 1b',
     'Shojiro Takasu, 2025', '4.0',
     'На панели b показана межтеменная кость из трёх частей. Панель a показывает тот же препарат с посмертными дефектами; дефекты не являются нормальными анатомическими отверстиями.'),
    ('A02.1.05.008', 'middle-clinoid', 'PMC11719673', 'diagnostics-15-00076-g002.jpg', 'Figure 2',
     'Ioannis Paschopoulos и соавт., 2024', '4.0',
     'MCP — средние наклонённые отростки. На панели A видны отдельные отростки, на других панелях — варианты костных перемычек. Перемычка и сам отросток — разные образования.'),
    ('A02.1.05.037', 'venosum', 'PMC10670589', 'cancers-15-05341-g002.jpg', 'Figure 2',
     'Andrea Palamenghi и соавт., 2023', '4.0',
     'Белая стрелка отмечает венозное отверстие справа (foramen venosum; отверстие Везалия) на поперечном срезе КТ.'),
    ('A02.1.05.039', 'petrosum', 'PMC10670589', 'cancers-15-05341-g003.jpg', 'Figure 3',
     'Andrea Palamenghi и соавт., 2023', '4.0',
     'Белые стрелки отмечают двусторонний canaliculus innominatus на КТ. В статье этот вариант также назван foramen petrosum. Один срез показывает просвет на данном уровне, а не весь ход канала.'),
    ('A02.1.07.012', 'supreme-concha', 'PMC13219204', '276_2026_3902_Fig1_HTML.jpg', 'Figure 1',
     'Mauro Bezerra Montello и соавт., 2026', '4.0',
     'Жёлтая стрелка — наивысшая носовая раковина (SupNC), красная — верхняя, голубая — средняя, зелёная — нижняя. Это фотография правой половины препарата с мягкими тканями, не отдельная сетка костной пластинки.'),
    ('A02.1.15.013', 'mandibular-torus', 'PMC11286380', 'cureus-0016-00000063484-i02.jpg', 'Figure 2',
     'Rehman Basharat, Alexander Bjorling, George Samara, 2024', '4.0',
     'Стрелками отмечены увеличенные двусторонние нижнечелюстные валики на КТ. Это клинический пример выраженного варианта, а не образец обязательной формы каждой нижней челюсти.'),
    ('A02.1.12.032', 'incisive-suture', 'PMC6340201', '2176-9451-dpjo-23-06-00016-gf15.jpg', 'Figure 15',
     'Mariana Trevizan и соавт., 2018', '4.0',
     'Три фотографии нёбной поверхности взрослых верхних челюстей показывают различную сохранность резцового шва. Это примеры других препаратов; обе стороны BodyParts3D по ним не подтверждаются.'),
]

PDF_EXAMPLES = [
    ('A02.1.06.008', 'mastoid-foramen', 'mastoid-djeric.pdf', 0,
     'https://publisher.medfak.ni.ac.rs/AMM_1/amm-stari/2014-html/4-broj/Dragoslava%20Djeric%20-%20ENLARGED%20MASTOID%20.pdf',
     'Enlarged mastoid foramen',
     'Dragoslava Đerić, Bojana Bukurov, Srbislav Blažić, Ljiljana Čvorović, 2014, Acta Medica Medianae 53(4)',
     'Figure 1, печатная с. 27; сообщение показано отдельно на Figure 2, с. 28',
     'Фотография увеличенного сосцевидного отверстия отдельного препарата. Его размер не следует считать обычным. Авторы отдельно проверили сообщение с бороздой сигмовидного синуса на распиле; эта фотография не является 3D-моделью канала.'),
    ('A02.1.03.024', 'trochlear-spine', 'trochlear.pdf', 4,
     'https://oajournals.fupress.net/index.php/ijae/article/view/1674',
     'Osteologic topography of the trochlear spine and fovea as landmarks to locate the superior oblique trochlea',
     'Margherita Aglianò и соавт., 2019, Italian Journal of Anatomy and Embryology 123(3)',
     'Figure 2, печатная с. 308',
     'Три фотографии показывают блоковую ость на разном расстоянии от края глазницы. Сохранены исходные стрелки на панелях A–C; это реальные костные препараты.'),
    ('A02.1.04.035', 'paramastoid', 'paramastoid.pdf', 1,
     'https://doi.org/10.5334/jbsr.1844',
     'Unilateral Paracondylar-Epitransverse Neo-Articulation with Secondary Atlas-Axis Rotation Anomaly',
     'Nick Janssen, Wouter Mebis, Jan Gielen, 2019, Journal of the Belgian Society of Radiology',
     'Figure 2A',
     'Жёлтая стрелка на панели A отмечает околососцевидный отросток (processus paramastoideus), названный в статье paracondylar process: эти названия используются как синонимы. Здесь он сочленяется с добавочным выступом поперечного отростка атланта. Это объёмное изображение по КТ отдельного сочетанного варианта; интерактивная сетка автора не предоставлена.'),
    ('A02.1.05.054', 'pterygospinous', 'pterygospinous.pdf', 3,
     'https://journals.pan.pl/Content/130897/2023-04-FMC-02-Artykuly-02.pdf',
     'Suture-like pattern formation in the pterygospinous bridge of the human sphenoid bone',
     'Janusz Skrzat, Grzegorz Goncerz, 2023, Folia Medica Cracoviensia',
     'Figure 3, печатная с. 30',
     'Стрелки показывают соединение костного выступа латеральной крыловидной пластинки с остью клиновидной кости. Здесь отросток участвует в костной перемычке; не следует запоминать замкнутую перемычку как обязательный вид отростка.'),
]

# Independent review of the actual source notices, not an inference from free
# download availability. The selected figures have no separate third-party credit
# excluding them from the article licence. The full source PDFs remain in cache.
PDF_LICENSE_LOCATORS = {
    'mastoid-foramen': 'PDF с.3, печатная с.29: уведомление CC BY 4.0 внизу страницы.',
    'trochlear-spine': 'Страница статьи издателя: Copyright Notice и ссылка Creative Commons Attribution 4.0 International License.',
    'paramastoid': 'PDF с.2: Copyright и CC-BY 4.0 непосредственно перед Figure 2.',
    'pterygospinous': 'PDF с.1, печатная с.27: Copyright и ссылка https://creativecommons.org/licenses/by/4.0/.',
}


def build():
    rows = []
    for code, key, pmc, filename, locator, author, version, caption in EXAMPLES:
        metadata = json.loads((CACHE / (pmc+'-s3.json')).read_text(encoding='utf-8'))
        assert metadata['license_code'] == 'CC BY' and not metadata['is_retracted']
        article = ET.fromstring((CACHE / (pmc+'.xml')).read_bytes())
        permissions = ''.join(article.find('.//permissions').itertext())
        assert 'creativecommons.org/licenses/by/'+version in permissions
        src = CACHE / filename
        original = next(u for u in metadata['media_urls'] if '/'+filename+'?' in u)
        from urllib.parse import parse_qs, urlparse
        assert hashlib.md5(src.read_bytes()).hexdigest() == parse_qs(urlparse(original).query)['md5'][0]
        dest = ROOT / 'site' / ('skull-example-'+key+'.jpg')
        shutil.copyfile(src, dest)
        rows.append(dict(c=code, id=key, image=dest.name, kind='published_image',
                         caption=caption, author=author, title=metadata['title'],
                         url='https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/', locator=locator,
                         license={'name':'CC BY '+version,'url':'https://creativecommons.org/licenses/by/'+version+'/'},
                         licenseEvidence={'reviewed':'2026-10-13',
                                          'url':'https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/',
                                          'locator':'Article permissions / Copyright and License information; подпись выбранного рисунка без отдельного ограничения прав.',
                                          'method':'Лицензия сверена с XML статьи и метаданными PMC; выбранный рисунок и его подпись просмотрены отдельно.'},
                         changes='Оригинальный файл рисунка без изменений. Русская подпись добавлена отдельно.',
                         original=original.replace('s3://pmc-oa-opendata/','https://pmc-oa-opendata.s3.amazonaws.com/'),
                         sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                         repository='NIH NLM NCBI PMC Article Datasets, доступ 2026-10-13. Статическая копия, не синхронизируется автоматически.'))
    import pymupdf
    for code,key,filename,page_index,url,title,author,locator,caption in PDF_EXAMPLES:
        doc=pymupdf.open(CACHE / filename)
        images=doc[page_index].get_images(full=True)
        assert len(images)==1, (filename, len(images))
        raw=doc.extract_image(images[0][0])
        # Some PDFs label JPEG2000 as jpg. Decode the whole embedded figure to
        # lossless PNG so all browsers can display it; no cropping or retouching.
        from PIL import Image
        from io import BytesIO
        dest=ROOT/'site'/('skull-example-'+key+'.png')
        Image.open(BytesIO(raw['image'])).save(dest,format='PNG')
        rows.append(dict(c=code,id=key,image=dest.name,kind='published_image',caption=caption,
                         author=author,title=title,url=url,locator=locator,
                         license={'name':'CC BY 4.0','url':'https://creativecommons.org/licenses/by/4.0/'},
                         licenseEvidence={'reviewed':'2026-10-13','url':url,
                                          'locator':PDF_LICENSE_LOCATORS[key],
                                          'method':'Проверены уведомление о правах в первоисточнике, выбранный рисунок и его подпись; отдельного ограничения прав на рисунок не указано.',
                                          'sourcePdfSha256':hashlib.sha256((CACHE/filename).read_bytes()).hexdigest()},
                         changes='Извлечён целый исходный рисунок из PDF и перекодирован в PNG без потерь; анатомическое изображение и авторские обозначения не изменены. Русская подпись добавлена отдельно.',
                         original=url,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
    assert len({r['c'] for r in rows})==len(rows)
    variants=json.loads((ROOT/'site/skull-study-variants.json').read_text(encoding='utf8'))
    for row in rows:
        term=next(p for p in variants if p['c']==row['c'])
        row['anatomyRefs']=term['refs']
        # The image paper may also be one of the two anatomical sources; its
        # repository copy is not a second independent anatomical reference.
        assert len({r['url'] for r in row['anatomyRefs']})>=2
        assert all(r.get('locator') for r in row['anatomyRefs']), row['id']
    report={'date':'2026-10-13','geometry_claim':False,
            'policy':'Изображения отдельных опубликованных препаратов. Ни одно из них не превращает проекцию BodyParts3D в подтверждённую геометрию.',
            'examples':rows}
    (ROOT/'research/variant-example-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'site/skull-variant-examples.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['ИЗОБРАЖЕНИЯ ВАРИАНТОВ ЧЕРЕПА — АВТОРСТВО И ЛИЦЕНЗИИ',
           'Иллюстрации независимы от 3D-моделей. Каждая сохраняет собственную лицензию.',
           'По одному изображению нельзя восстановить полный ход канала или перенести вариант на BodyParts3D.', '']
    for row in rows:
        lines.extend([row['image']+' — TA98 '+row['c'],row['author'],row['title'],
                      row['url']+' · '+row['locator'],row['license']['name']+' '+row['license']['url'],
                      row['changes'],row.get('repository',''),
                      'Основание проверки лицензии: '+row['licenseEvidence']['locator'],
                      'SHA256 '+row['sha256'],''])
    (ROOT/'site/LICENSE-SKULL-EXAMPLES.txt').write_text('\n'.join(lines),encoding='utf8')
    print('Reviewed variant images:',len(rows),'distinct TA98 codes; zero inferred 3D meshes')


if __name__=='__main__':
    build()

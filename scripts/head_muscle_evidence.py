"""Reviewed locators for head muscle fields, 2026-10-13.

IndependentSource identifies an editorial/observational source family, not a
second URL or a second language edition. DEGUM and its cited Zilles table are
one family. These are literature checks, not a human expert sign-off of meshes.
Inherited part fields retain precisely the parent's evidence and status.
"""
from copy import deepcopy

FIELDS = ('o', 'i', 'a', 'n', 's')
KH = 'https://www.kenhub.com/en/library/anatomy/'
LUMEN = 'https://www.meddean.luc.edu/lumen/meded/grossanatomy/dissector/mml/'
TMA = 'https://teachmeanatomy.info/encyclopaedia/'
DEGUM = 'https://www.degum.de/fileadmin/dokumente/sektionen/kopf-hals/Informationen_zum_Fach/Instruction_for_the_sonography_of_facial_muscles_v06a.pdf'
FACE = KH + 'the-facial-muscles'
OCULI = KH + 'orbicularis-oculi'
UZH = 'https://e-learn.anatomy.uzh.ch/anatomie/Bewegungsapparat/bewapp_HTML/wirbel/wirMlehr49.html'
UZH_MOUTH = 'https://e-learn.anatomy.uzh.ch/anatomie/Topographie/topo_HTML/kopf/KopfMuskeln06.html'
UZH_SCALP = 'https://e-learn.anatomy.uzh.ch/anatomie/Topographie/topo_HTML/kopf/KopfMuskeln02.html'
UZH_EYE = 'https://e-learn.anatomy.uzh.ch/anatomie/Topographie/topo_HTML/kopf/KopfMuskeln03.html'
UNSW = 'https://medicalsciences.med.unsw.edu.au/sites/default/files/soms/page/Undergrad/ANAT2521%20Evolution%20of%20Human%20Structure%20-%20Student%20Manual%202017.pdf'
COOK = 'https://journals.sagepub.com/doi/10.1177/074880680001700402'
HUR = 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264148'
TM = 'https://www.scielo.cl/pdf/ijmorphol/v31n4/art40.pdf'
IMAIOS = 'https://www.imaios.cn/en/e-anatomy/anatomical-structures/transversus-menti-muscle-14215192'
EL = 'https://www.elsevier.com/resources/anatomy/muscular-system/muscles-of-head/'
EL_DS = EL + 'depressor-supercilii/21131'
EL_AUR = EL + 'auricularis-anterior-muscle/23524'
EL_OCC = EL + 'occipitalis-muscle/18733'

PAGES = {
    **dict.fromkeys(('occipitofrontalis','temporoparietalis','orbicularis_oculi','corrugator_supercilii','depressor_supercilii'),4),
    **dict.fromkeys(('procerus','nasalis','depressor_septi_nasi','levator_nasolabialis','orbicularis_oris','buccinator','zygomaticus_major','zygomaticus_minor'),5),
    **dict.fromkeys(('risorius','levator_labii_superioris','levator_anguli_oris','depressor_anguli_oris','depressor_labii_inferioris','mentalis','auricularis_anterior','auricularis_superior','auricularis_posterior'),6),
    **dict.fromkeys(('masseter','temporalis','medial_pterygoid','lateral_pterygoid'),7),
}
LABELS = dict(o='начало',i='прикрепление',a='функция',n='иннервация',s='кровоснабжение')
LATIN_ROWS = {'levator_nasolabialis':'levator labii superioris alaeque nasi',
              'lateral_pterygoid':'pterygoideus lateralis','medial_pterygoid':'pterygoideus medialis'}

def kh(key): return KH + key.replace('_','-') + '-muscle'
def tma(key):
    slug = key.replace('_','-')
    return TMA + slug[0] + '/' + slug + '/'

def reference(url, key, field, *, part=None, locator=None):
    """Specific source headings, never bare URLs as field-level support."""
    row = key.replace('_',' ')
    if url.startswith(LUMEN):
        family='loyola-lumen'; title='Loyola University, LUMEN'
        default=row + ': ' + dict(o='ORIGIN',i='INSERTION',a='ACTION',n='NERVE')[field]
    elif url == DEGUM:
        family='degum-zilles-table'; title='DEGUM, Volk / Sauer: таблица мышц'
        default=f'с. {PAGES[key]}, раздел '+('6 (жевательные мышцы)' if PAGES[key]==7 else '5 (мимические мышцы)')+', строка m. '+LATIN_ROWS.get(key,row)+', '+dict(o='Origin',i='Approach',a='Function',n='Innervation',s='Blood supply')[field]
    elif 'kenhub.com' in url:
        family='kenhub-editorial'; title='Kenhub: открытая анатомическая статья'
        if url == FACE:
            default='Auricular muscles' if key.startswith('auricularis') else 'Levator labii superioris alaeque nasi muscle'
            default += ': абзац «'+LABELS[field]+'»'
        elif '/de/' in url:
            default='Funktion' if field=='a' else 'Verlauf und Versorgung'
        else:
            default=dict(o='Origin and insertion: origin',i='Origin and insertion: insertion',a='Function',n='Innervation',s='Blood supply')[field]
        if key=='transversus_menti':
            default='Depressor anguli oris / Origin and insertion: абзац о пересечении средней линии и transversus menti'
    elif url.startswith(TMA):
        family='teachmeanatomy-editorial'; title='TeachMeAnatomy: '+row
        default=dict(o='Attachments: origin',i='Attachments: insertion',a='Actions',n='Innervation',s='Blood Supply')[field]
    elif url in (UZH, UZH_MOUTH, UZH_SCALP, UZH_EYE):
        family='university-zurich'; title='Цюрихский университет: анатомия'
        default='M. '+row+': '+dict(o='U (Ursprung)',i='A (Ansatz)',a='F (Funktion)',n='N (Nerven)')[field]
    elif url == UNSW:
        family='university-new-south-wales'; title='UNSW, ANAT2521: учебное руководство, 2017'
        default='PDF с. 67: Facial muscles, абзац о frontalis и occipitalis'
    elif url == COOK:
        family='cook-lucarelli-lemke'; title='Cook, Lucarelli, Lemke, 2000: depressor supercilii'
        default='Открытый Abstract, '+('Discussion' if field=='a' else 'Results')
    elif url == HUR:
        family='hur-lee-jung-schneider-2022'; title='Hur и соавт., PLOS ONE, 2022'
        default={'o':'Introduction, абзац о DS: origin from the frontal process of the maxilla; Fig. 1',
                 'i':'Introduction, абзац о DS: skin in the medial third of the eyebrow',
                 'a':'Abstract и Discussion, Fig. 4: downward pull of medial eyebrow',
                 'n':'Introduction, первый абзац: mimetic muscles — facial nerve'}[field]
        if key=='levator_nasolabialis':
            default='Introduction, абзац о LLSAN; Fig. 4: подъём верхней губы и крыла носа'
    elif url == TM:
        family='sripanidkulchai-2013'; title='Sripanidkulchai и соавт., 2013: transversus menti'
        default='с. 1399, '+('Discussion: предполагаемое действие, с отсылкой к Weaver (1978)' if field=='a' else 'Case report; Fig. 1 на с. 1400')
    elif url == IMAIOS:
        family='imaios-javaid-definition'; title='IMAIOS, M. A. Javaid: открытое определение'
        default='Definition / '+dict(o='Origin',i='Insertion',a='Action',n='Innervation',s='Blood supply')[field]
    elif url.startswith(EL):
        family='elsevier-open-summary'; title='Elsevier: открытая справочная страница'
        default='Quick Facts / '+dict(o='Origin',i='Insertion',a='Action',n='Innervation',s='Arterial Supply')[field]
    else:
        raise ValueError(('Unreviewed source',url,key,field))
    if part:
        default += '; '+part
    return dict(sourceId=family+':'+url.rsplit('/',2)[-2 if url.endswith('/') else -1].split('?')[0],
                title=title,url=url,locator=locator or default,independentSource=family)

def enrich_evidence(muscles, evidence):
    # Correct incomplete source pairs instead of treating all anatomy links as
    # support for every field. Additional citations may cover distinct subclaims.
    changes = {
      ('occipitofrontalis','a'):[kh('occipitofrontalis'),UNSW,EL_OCC],
      ('occipitofrontalis','o'):[kh('occipitofrontalis'),DEGUM,UZH_SCALP],
      ('orbicularis_oculi','o'):[tma('orbicularis_oculi'),OCULI],
      ('orbicularis_oculi','i'):[tma('orbicularis_oculi'),OCULI],
      ('corrugator_supercilii','i'):[tma('corrugator_supercilii'),kh('corrugator_supercilii')],
      ('corrugator_supercilii','a'):[tma('corrugator_supercilii'),kh('corrugator_supercilii')],
      ('procerus','o'):[LUMEN+'pro.htm',kh('procerus')],
      ('procerus','a'):[tma('procerus'),kh('procerus')],
      ('orbicularis_oris','o'):[LUMEN+'oor.htm',kh('orbicularis_oris'),tma('orbicularis_oris')],
      ('orbicularis_oris','i'):[kh('orbicularis_oris'),tma('orbicularis_oris')],
      ('orbicularis_oris','a'):[LUMEN+'oor.htm',kh('orbicularis_oris'),UZH_MOUTH],
      ('orbicularis_oris','n'):[kh('orbicularis_oris'),tma('orbicularis_oris')],
      ('depressor_labii_inferioris','i'):[kh('depressor_labii_inferioris'),DEGUM],
      ('depressor_labii_inferioris','n'):[LUMEN+'dli.htm',DEGUM],
      ('levator_anguli_oris','o'):[kh('levator_anguli_oris'),UZH_MOUTH],
      ('levator_nasolabialis','a'):[DEGUM,HUR],
      ('buccinator','i'):[LUMEN+'buc.htm',kh('buccinator'),tma('buccinator')],
      ('buccinator','a'):[kh('buccinator'),tma('buccinator')],
      ('masseter','n'):[kh('masseter'),UZH],
      ('temporalis','o'):[kh('temporalis'),UZH],
      ('temporalis','s'):[kh('temporalis'),DEGUM],
      ('lateral_pterygoid','i'):[LUMEN+'lpte.htm',kh('lateral_pterygoid')],
      ('lateral_pterygoid','a'):[tma('lateral_pterygoid'),kh('lateral_pterygoid')],
      ('lateral_pterygoid','n'):[LUMEN+'lpte.htm',kh('lateral_pterygoid')],
      ('medial_pterygoid','a'):[LUMEN+'mpte.htm',kh('medial_pterygoid')],
      ('medial_pterygoid','n'):[LUMEN+'mpte.htm',kh('medial_pterygoid')],
      ('auricularis_anterior','o'):[DEGUM,FACE,EL_AUR],
      ('auricularis_superior','s'):[DEGUM,FACE],
      ('auricularis_posterior','s'):[DEGUM,FACE],
      ('depressor_supercilii','o'):[COOK,HUR],
      ('depressor_supercilii','i'):[COOK,DEGUM],
      ('depressor_supercilii','a'):[COOK,HUR],
      ('depressor_supercilii','n'):[DEGUM,HUR],
      ('transversus_menti','a'):[TM,IMAIOS],
      ('transversus_menti','s'):[TM,IMAIOS],
    }
    for (key,field), urls in changes.items():
        evidence[key]['fields'][field]=urls

    # More specific part text is added only where two independently edited
    # descriptions explicitly refer to that part. No mesh boundaries are inferred.
    part_changes = {
      ('occipitofrontalis','frontal','s'):('Ветви глазной и поверхностной височной артерий.',[kh('occipitofrontalis'),DEGUM]),
      ('occipitofrontalis','occipital','s'):('Затылочная артерия (a. occipitalis).',[kh('occipitofrontalis'),DEGUM]),
      ('orbicularis_oculi','palpebral','o'):('Медиальная связка века (lig. palpebrale mediale).',[OCULI,DEGUM]),
      ('orbicularis_oculi','palpebral','i'):('Латеральный шов век (raphe palpebralis lateralis); в источниках также назван латеральной связкой века.',[OCULI,DEGUM]),
      ('orbicularis_oculi','orbital','o'):('Медиальный край глазницы в области слёзного гребня и лобного отростка верхней челюсти.',[DEGUM,UZH_EYE,OCULI]),
      ('orbicularis_oculi','orbital','i'):('Кожа и мягкие ткани вокруг края глазницы.',[OCULI,UZH_EYE]),
      ('orbicularis_oculi','deep','o'):('Слёзная кость в области слёзного гребня.',[OCULI,DEGUM]),
      ('orbicularis_oculi','deep','i'):('Волокна вековой части в медиальной области век.',[DEGUM,UZH_EYE]),
      ('nasalis','transverse','o'):('Верхняя челюсть сбоку от основания носа.',[tma('nasalis'),kh('nasalis')]),
      ('nasalis','alar','o'):('Верхняя челюсть над латеральным резцом.',[tma('nasalis'),kh('nasalis')]),
      ('masseter','superficial','i'):('Наружная поверхность угла и нижней части ветви нижней челюсти, жевательная бугристость.',[kh('masseter'),DEGUM]),
      ('masseter','deep','i'):('Наружная поверхность ветви нижней челюсти, выше прикрепления поверхностной части.',[kh('masseter'),DEGUM]),
    }
    part_refs = {}
    for (key,part,field),(text,urls) in part_changes.items():
        muscles[key]['parts'][part][field]=text
        part_refs[key,part,field]=urls
    # Original part-specific statements also need actual part-level sources.
    for part in ('frontal','occipital'):
        for f in ('o','i','n'):
            part_refs['occipitofrontalis',part,f]=[kh('occipitofrontalis'),DEGUM]
        if part=='frontal':
            part_refs['occipitofrontalis',part,'o'].append(UZH_SCALP)
        part_refs['occipitofrontalis',part,'a']=([kh('occipitofrontalis'),DEGUM,UNSW] if part=='frontal' else [kh('occipitofrontalis'),UNSW,EL_OCC])
    for part in ('orbital','palpebral','deep'):
        part_refs['orbicularis_oculi',part,'a']=[tma('orbicularis_oculi'),DEGUM]
    for part in ('transverse','alar'):
        for f in ('i','a'): part_refs['nasalis',part,f]=[tma('nasalis'),kh('nasalis')]
    part_refs['masseter','superficial','o']=[kh('masseter'),tma('masseter'),UZH]
    part_refs['masseter','deep','o']=[kh('masseter'),UZH]
    for part in ('upper','lower'):
        part_refs['lateral_pterygoid',part,'o']=[LUMEN+'lpte.htm',kh('lateral_pterygoid')]

    # Existing disagreements are not erased by the field-level presentation.
    muscles['masseter']['note']='Границы начала глубокой части в источниках описываются неодинаково: Цюрихский университет и таблица Kenhub указывают заднюю треть скуловой дуги, основной текст той же статьи Kenhub — всю длину её нижнего края. Здесь дана область начала, без точной границы на модели.'
    muscles['orbicularis_oculi']['parts']['deep']['x']='В учебниках также называется слёзной частью; в TA98 — pars profunda. DEGUM и Цюрихский университет описывают переход в вековую часть у медиального угла; Kenhub отдельно перечисляет хрящи век и латеральную связку. Краткое поле прикрепления не является исчерпывающей картой всех волокон.'
    muscles['auricularis_superior']['note']='Височные ветви лицевого нерва указаны в обоих источниках; таблица DEGUM дополнительно называет задний ушной нерв. Поле иннервации содержит общий подтверждённый уровень ветвей, а не исключительный перечень.'
    muscles['auricularis_anterior']['note']='DEGUM и Kenhub указывают височные ветви лицевого нерва; открытая страница Elsevier дополнительно перечисляет задний ушной нерв. Для кровоснабжения приведена ветвь, указанная в DEGUM и Elsevier; это не исчерпывающий список сосудов.'
    muscles['transversus_menti']['note']='Непостоянный поперечный пучок. В исследовании 2013 года в одном препарате описаны ветви подподбородочной артерии; открытое определение IMAIOS указывает нижнюю губную и подбородочную артерии. Единую питающую ветвь эти источники не подтверждают. Предположения о функции восходят, в частности, к Weaver (1978) и не приняты здесь за две независимые функциональные проверки.'
    muscles['transversus_menti']['s']='Конкретная питающая ветвь не подтверждена: источники описывают разные сосуды; см. примечание.'

    for key,m in muscles.items():
        ev=evidence[key]
        ev['reviewMethod']='Сопоставление текста каждого поля с указанными разделами; разные страницы одного издателя не считаются независимыми источниками. Это проверка литературы, не экспертная аттестация 3D-формы.'
        ev['note']=m.get('note','')
        m['fieldRefs']={f:[reference(url,key,f) for url in ev['fields'][f]] for f in FIELDS}
        m['fieldStatus']={f:('unconfirmed' if f in ev.get('unconfirmed',[]) else 'supported') for f in FIELDS}
        m['fieldScope']={f:('unconfirmed' if m['fieldStatus'][f]=='unconfirmed' else 'whole_muscle') for f in FIELDS}
        ev['fieldRefs']=deepcopy(m['fieldRefs'])
        ev['fieldStatus']=deepcopy(m['fieldStatus'])
        ev['fieldScope']=deepcopy(m['fieldScope'])
        ev['parts']={}
        for part,p in m.get('parts',{}).items():
            p['fieldRefs']={};p['fieldStatus']={};p['fieldScope']={}
            for f in FIELDS:
                if f in p:
                    urls=part_refs[key,part,f] # No silent fallback for a specific claim.
                    p['fieldRefs'][f]=[reference(url,key,f,part=p['lat']) for url in urls]
                    p['fieldStatus'][f]='supported'
                    p['fieldScope'][f]='specific'
                else:
                    p['fieldRefs'][f]=deepcopy(m['fieldRefs'][f])
                    p['fieldStatus'][f]=m['fieldStatus'][f]
                    p['fieldScope'][f]=m['fieldScope'][f]
            ev['parts'][part]={'code':p['code'],'fields':{f:[r['url'] for r in p['fieldRefs'][f]] for f in FIELDS},
                               'fieldRefs':deepcopy(p['fieldRefs']), 'fieldStatus':deepcopy(p['fieldStatus']),
                               'fieldScope':deepcopy(p['fieldScope'])}
        # Preserve global card references, including nomenclature, and include
        # newly selected field sources. Facts remain anchored by fieldRefs.
        seen={r['url'] for r in m['refs']}
        for rec in [m,*m.get('parts',{}).values()]:
            for f in FIELDS:
                refs=rec['fieldRefs'][f]
                if rec['fieldStatus'][f]=='supported':
                    assert len({r['independentSource'] for r in refs})>=2,(key,f)
                assert all(r['locator'] for r in refs),(key,f)
                for r in refs:
                    if r['url'] not in seen:
                        m['refs'].append({'url':r['url'],'title':r['title']});seen.add(r['url'])

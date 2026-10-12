"""Export the evidence inventory, without copying source articles or images."""
from pathlib import Path
import json
from head_terms import T, DESCRIPTIONS, BONES, BOOK_URL, IFAA_URL, TERM_NOTES
from head_muscles import EVIDENCE, MUSCLE_TEMPLATES
from head_localization import descriptions, positions, SUPPLEMENTS

feature_descriptions = {**DESCRIPTIONS, **descriptions()}
landmarks = positions()

root=Path(__file__).resolve().parents[1]
out=root/'research'
out.mkdir(exist_ok=True)
record={
    'scope':'Череп, мимические и жевательные мышцы. Полнота терминов и локализация 3D проверяются отдельно.',
    'terminology':{'latin':'TA98, с явно указанными различиями электронной таблицы IFAA и печатного издания',
                   'russian':'Международная анатомическая терминология, под ред. Л. Л. Колесникова, 2003',
                   'sources':[IFAA_URL,BOOK_URL],
                   'independence_note':'Два издания одной номенклатуры подтверждают названия, но не считаются двумя независимыми источниками анатомических фактов.'},
    'bone_cards':BONES,
    'bone_features':{code:{'latin':T[code][0],'russian':T[code][1],**data,
                          **({'terminology_note':TERM_NOTES[code]} if code in TERM_NOTES else {})}
                     for code,data in feature_descriptions.items()},
    'muscles':{key:{**entry,'published_fields':{f:MUSCLE_TEMPLATES[key][f] for f in ('o','i','a','n','s')}} for key,entry in EVIDENCE.items()},
    'localization':{'baseline':'pins_head/ta.json',
                    'supplements':SUPPLEMENTS,
                    'method':'Индивидуальный осмотр модели, сопоставление с указанными анатомическими источниками. Поверхность и топографическая проекция учитываются раздельно.',
                    'kinds':{'surface':'Участок видимой поверхности или край образования',
                             'projection':'Проекция анатомического расположения; собственная форма не подтверждается геометрией',
                             'internal':'Схематический внутренний ориентир',
                             'variant':'Проекция варианта строения, который не представлен как отдельное образование на данной модели'},
                    'records':[{'bone':bone,'code':code,**row} for (bone,code),row in landmarks.items()]},
    'limitations':[
        'У поверхностей и краёв маркер указывает один выбранный участок, а не весь объект. Для каналов один маркер не изображает их ход.',
        'Функция и конкретное кровоснабжение поперечной мышцы подбородка не подтверждены двумя независимыми источниками и не заполнены как установленные факты.',
        'Проекции и внутренние схемы не являются измеренными границами образования и не доказывают его наличие в геометрии BodyParts3D.',
        'Автоматические проверки проверяют структуру данных и комплектность. Они не заменяют анатомическую экспертизу.'
    ]
}
(out/'head-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Evidence inventory:',len(feature_descriptions),'bone features;',len(EVIDENCE),'muscle templates')

"""Export the evidence inventory, without copying source articles or images."""
from pathlib import Path
import json
from head_terms import T, DESCRIPTIONS, BONES, BOOK_URL, IFAA_URL, TERM_NOTES
from head_muscles import EVIDENCE, MUSCLE_TEMPLATES

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
    'bone_features':{code:{'latin':T[code][0],'russian':T[code][1],**data} for code,data in DESCRIPTIONS.items()},
    'muscles':{key:{**entry,'published_fields':{f:MUSCLE_TEMPLATES[key][f] for f in ('o','i','a','n','s')}} for key,entry in EVIDENCE.items()},
    'localization':'pins_head/ta.json: только отмеченные на поверхности ориентиры; остальные термины остаются без координат.',
    'limitations':[
        'Для большинства костных образований подготовлена номенклатурная карточка, а не развёрнутое топографическое описание.',
        'Функция и конкретное кровоснабжение поперечной мышцы подбородка не подтверждены двумя независимыми источниками и не заполнены как установленные факты.',
        'Ряд терминов TA98 обозначает внутренние каналы или элементы, которые не удалось уверенно локализовать на этой сетке.',
        'Автоматические проверки проверяют структуру данных и комплектность. Они не заменяют анатомическую экспертизу.'
    ]
}
(out/'head-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Evidence inventory:',len(DESCRIPTIONS),'bone features;',len(EVIDENCE),'muscle templates')

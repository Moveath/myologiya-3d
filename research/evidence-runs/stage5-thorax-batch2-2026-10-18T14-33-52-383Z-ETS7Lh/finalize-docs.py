from pathlib import Path
import json
root=Path.cwd()
base=root/'research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh'
bundle=root/'research/stage5-thorax-batch2-2026-10-18'
data_run='research/evidence-runs/stage5-ribs-data-2026-10-18T14-57-48-409Z-WIBJx1/data-regression.json'
search_run='research/evidence-runs/stage5-ribs-search-final-2026-10-18T15-06-49-553Z-rVaP9Q/result.json'
assert json.loads((root/data_run).read_text(encoding='utf-8'))['status']=='passed'
assert json.loads((root/search_run).read_text(encoding='utf-8'))['status']=='passed'
def write(path,text): path.write_text(text,encoding='utf-8',newline='\n')
issues=root/'ANATOMY_ISSUES.md'
s=issues.read_text(encoding='utf-8')
assert '### SYS-ADDITIONAL-SEARCH' not in s
s=s.replace('PIN-THORAX-KIND проверена; геометрия и прежние задачи сохраняются.', 'PIN-THORAX-KIND и SYS-ADDITIONAL-SEARCH проверены; геометрия и прежние задачи сохраняются.')
s=s.replace('Всего **215 записей**; подтверждённо закрыто **46**','Всего **216 записей**; подтверждённо закрыто **47**')
s=s.replace('Этап 5 — **24/93**. LOG-20261018-02: закрыта только PIN-THORAX-KIND; остальные 214 статусов сохранены.', 'Этап 5 — **25/94**. LOG-20261018-02: закрыта PIN-THORAX-KIND, добавлена и проверена SYS-ADDITIONAL-SEARCH; остальные 214 прежних статусов сохранены.')
s=s.replace('| проверена | 46 |','| проверена | 47 |')
marker='\n\n## Карточки задач'
assert s.count(marker)==1
s=s.replace(marker,'\n| [SYS-ADDITIONAL-SEARCH](#sys-additional-search) | Дополнительные костные карточки ошибочно подписаны как мышцы в поиске | 5 | P1 | проверена |\n'+marker)
s+='''\n### SYS-ADDITIONAL-SEARCH

**Дополнительные костные карточки ошибочно подписаны как мышцы в поиске**

- Категория: интерфейс и поиск. Этап: **5**. Приоритет: **P1**. Статус: **проверена**. Научная проверка: нет. Обновлено: **2026-10-18**.
- Структуры и ID: все костные записи t=additional; адресно проверены 24 extra_sternum_* и прежняя extra_thoracic_12_superior_tubercle_right. Анатомические ID не менялись.
- Источник обнаружения: LOG-20261018-02, проверка нового дополнительного каталога; renderList использовал TA98 для t=ta и «мышца» для всех остальных записей.
- Затронутые файлы: site/index.html, генерируемый site/local.html; tools/verify-stage5-ribs.mjs.
- Решение и критерий закрытия: дополнительные костные карточки подписываются «ориентир»; подписи TA98 и мышечных записей сохраняются. Поиск возвращает единственный ID, реальный клик открывает его карточку; 1280/390 px, без новых ошибок.
- Доказательства исправления и тесты: точечно изменена одна ветка подписи, local.html пересоздан штатным генератором. Node проверил тождество всего index.html прежнему снимку кроме этой замены. Финальный Playwright MCP: на каждой ширине 26 проверок ввода/DOM (24 новые, прежняя T12, запись TA98), реальный клик поиска; список грудины содержит 8 TA98 и отдельно 24 дополнительные записи. Ошибок страницы нет, переполнения нет. Полная предшествующая регрессия 1280/390 сохранена; после подписи геометрический код не менялся. [Отчёт](research/stage5-thorax-batch2-report-2026-10-18.md); [проверка поиска](research/evidence-runs/stage5-ribs-search-final-2026-10-18T15-06-49-553Z-rVaP9Q/result.json); [проверка неизменности](research/evidence-runs/stage5-ribs-data-2026-10-18T14-57-48-409Z-WIBJx1/data-regression.json).
'''
write(issues,s)
progress=root/'ANATOMY_PROGRESS.md'
s=progress.read_text(encoding='utf-8')
s=s.replace('24 проверено / 93 всего; не процент готовности анатомии.', '25 проверено / 94 всего; не процент готовности анатомии.')
s=s.replace('**215 записей: 46 проверено, 169 не закрыто;', '**216 записей: 47 проверено, 169 не закрыто;')
start=s.index('### LOG-20261018-02')
before,log=s[:start],s[start:]
log=log.replace('и 55 защищённых файлов неизменны.', 'и 53 защищённых файла неизменны. index.html отличается только исправлением подписи поиска, local.html пересоздан.')
log=log.replace('- Закрыта только PIN-THORAX-KIND. 215 задач: 46 проверены,', '- Закрыта PIN-THORAX-KIND; зарегистрирована и проверена SYS-ADDITIONAL-SEARCH. 216 задач: 47 проверены,').replace('Этап 5: 24/93.', 'Этап 5: 25/94.')
log=log.replace('- Текущая грудь:', '- Устранена подпись «мышца» у дополнительных костных карточек в поиске. После правки MCP 1280/light,390/dark: по 26 проверок DOM поиска, реальный клик, TA98=8 и additional=24 в грудине; без ошибок страницы. Неверное сравнение innerText с нижним регистром в первом тесте исправлено в сценарии (CSS upper-case). Длинное повторение всех кликов прервано на стороне ожидания, его снимки сохранены; успешным протоколом служит отдельный завершённый адресный запуск.\n- Текущая грудь:')
write(progress,before+log)
report=root/'research/stage5-thorax-batch2-report-2026-10-18.md'
s=report.read_text(encoding='utf-8')
s=s.replace('\nОбщие ID:', '\n7. Исправлена реальная ошибка поиска: дополнительные костные карточки t=additional показывали подпись «мышца». Теперь подпись «ориентир»; TA98 и мышечная ветка сохранены. local.html пересоздан штатно.\n\nОбщие ID:')
s=s.replace('**55 защищённых файлов неизменны**. Код интерфейса, BVH, срезов и оригинальные GLB не правились.', '**53 защищённых файла неизменны**. В index.html допускается только точная замена подписи дополнительных записей в поиске; всё остальное содержимое, включая BVH/срезы, тождественно прежнему. local.html пересоздан; GLB не правились.')
s=s.replace('\nНеуспешные прогоны', '\n- После последней правки подписи: Playwright MCP **1280/light,390/dark**, по 26 проверок ввода/DOM поиска (24 новые + прежняя дополнительная T12 + TA98), реальный поисковый клик; в карточке грудины 8 TA98 и 24 дополнительных записи. Переполнения и ошибок страницы нет. В первом сценарии сравнение innerText не учитывало CSS-регистр; исправлен сценарий. Ожидание длинного повторения всех кликов прекращено на клиенте: его снимки сохранены, но нет принятого итогового JSON. Адресный финальный запуск завершён и сохранён отдельно.\n\nНеуспешные прогоны')
s=s.replace('**В этой партии закрыта одна запись учёта: PIN-THORAX-KIND.** Реестр: **215 задач, 46 проверены,', '**В этой партии проверены две записи учёта: PIN-THORAX-KIND и новая SYS-ADDITIONAL-SEARCH.** Реестр: **216 задач, 47 проверены,')
s=s.replace('Этап 5: 24/93. Новые отдельные задачи не дублировались:', 'Этап 5: 25/94. Новая техническая задача не дублирует анатомические:')
bt=chr(96)
s=s.replace(bt+'site/index.html/local.html'+bt+', анатомические координаты, исходная разметка и GLB не изменены.', bt+'site/index.html'+bt+' содержит одну замену подписи поиска; '+bt+'site/local.html'+bt+' пересоздан штатным генератором. Анатомические координаты, исходная разметка и GLB не изменены.')
write(report,s)
p=bundle/'catalogue-decisions.json'
write(p,p.read_text(encoding='utf-8').replace('Несyставная','Несуставная'))
payload=json.loads((root/data_run).read_text(encoding='utf-8'))
write(bundle/'reviewed-records.json',json.dumps(payload['records'],ensure_ascii=False,indent=2)+'\n')
evidence={
 'date':'2026-10-18','scope':'24 ribs and sternum; stage 5 batch 2',
 'data':data_run,
 'geometry_data':'research/evidence-runs/thorax-data-2026-10-18T14-41-32-613Z-8SMw7W/thorax-data-geometry.json',
 'full_ui_1280':'research/evidence-runs/stage5-ribs-mcp-2026-10-18T14-50-24-656Z-PwmL0A/result.json',
 'full_ui_390':'research/evidence-runs/stage5-ribs-mcp-2026-10-18T14-50-24-737Z-Y0xLlh/result.json',
 'sources_parent_links':'research/evidence-runs/stage5-ribs-final-links-2026-10-18T14-47-48-331Z-3M1DhT/result.json',
 'final_search_ui':search_run,
 'blender':str((base/'blender-ribs.json').relative_to(root)).replace('\\','/'),
 'trimesh':str((base/'trimesh-positions.json').relative_to(root)).replace('\\','/'),
 'source_components':str((base/'source-parts.json').relative_to(root)).replace('\\','/'),
 'pubmed_efetch':str((base/'pubmed-verified.json').relative_to(root)).replace('\\','/'),
 'registry_final':str((base/'registry-final.json').relative_to(root)).replace('\\','/'),
 'limitations':[
  'No new accepted anatomical coordinates or extents; surface proximity alone is not anatomy acceptance.',
  'Full UI precedes the final search-label-only change; final DOM/search regression follows it, and Node verifies all other HTML unchanged.',
  'TA98 console run: 762 terms, three pre-existing differences. No standalone JSON for this run.',
  'Direct NCBI Bookshelf blocked by reCAPTCHA; indexed extracts only; PubMed EFetch and relevant PMC full text verified.',
  '1280/light and 390/dark parent-link screenshots predate classification of new cards as additional; use final full UI and search UI for category counts.',
  'Failed and client-interrupted runs retained; final-search JSON is authoritative for the last label change.'
 ]
}
with (bundle/'evidence.json').open('x',encoding='utf-8') as f: json.dump(evidence,f,ensure_ascii=False,indent=2); f.write('\n')
print('Updated registry, progress, report, per-ID rows and evidence index.')


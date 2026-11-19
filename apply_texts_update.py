"""Обновляет тексты бота под текущую схему (кнопки подключения, список серверов по странам).
Запуск из каталога бота."""
import shutil

REPL = [
    # 1. приветствие
    (r'''"3️⃣ Вставьте её в приложение (шаги в «Инструкциях»)\n\n"''',
     r'''"3️⃣ Нажмите кнопку своего приложения: Karing, Happ или Incy (шаги в «Инструкциях»)\n\n"'''),
    # 2. сообщение после оплаты
    (r'''"Вставьте её в приложение: подробнее в «Инструкциях».",''',
     r'''"Нажмите кнопку своего приложения ниже или скопируйте ссылку. Подробнее в «Инструкциях».",'''),
    # 3. пробный период
    (r'''f"Ссылка подписки (нажмите, чтобы скопировать):\n<code>{u['subscription_url']}</code>",''',
     r'''f"Ссылка подписки (нажмите, чтобы скопировать):\n<code>{u['subscription_url']}</code>\n\n"
        "Нажмите кнопку своего приложения ниже, чтобы подключиться.",'''),
    # 4. список серверов: по странам
    (r'''    names = []
    for h in await mz.hosts():
        if h.get("is_disabled"):
            continue
        name = re.sub(r"\{[^}]*\}", "", h.get("remark", "")).strip()
        if name and name not in names:
            names.append(name)
    text = "<b>Список серверов</b>\n\n" + ("\n".join(f"• {html.escape(n)}" for n in names) or "Пока пусто.")''',
     r'''    groups = {}
    for h in await mz.hosts():
        if h.get("is_disabled"):
            continue
        name = re.sub(r"\{[^}]*\}", "", h.get("remark", "")).strip()
        if not name:
            continue
        country, _, kind = name.rpartition(" · ")
        if not country:
            country, kind = name, ""
        kinds = groups.setdefault(country, [])
        if kind and kind not in kinds:
            kinds.append(kind)
    lines = []
    for country, kinds in groups.items():
        extra = f" ({html.escape(', '.join(kinds))})" if kinds else ""
        lines.append(f"• {html.escape(country)}{extra}")
    text = ("<b>Список серверов</b>\n\n" + ("\n".join(lines) or "Пока пусто.")
            + "\n\nВ приложении выберите любой сервер из списка. Если один не работает, попробуйте другой.")'''),
]

s = open("main.py", encoding="utf-8").read()
if "groups = {}" in s:
    print("main.py уже обновлён")
else:
    for old, _ in REPL:
        assert old in s, "не найден фрагмент: " + old[:60] + " (main.py не изменён)"
    shutil.copy("main.py", "main.py.bak-texts")
    for old, new in REPL:
        s = s.replace(old, new)
    open("main.py", "w", encoding="utf-8").write(s)
    print("main.py обновлён")

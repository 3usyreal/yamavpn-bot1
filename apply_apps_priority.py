"""Приоритет приложений Happ -> Karing -> Incy, новые «Инструкции», список серверов с Hysteria2.
Запуск из каталога бота. Меняет main.py, config.py и строку SERVERS_STATIC в .env."""
import re
import shutil

SERVERS = (
    "🇵🇱 Польша|TCP, gRPC, XHTTP, Hysteria2;"
    "🇩🇪 Германия|TCP, gRPC, XHTTP, Hysteria2;"
    "🇳🇱 Нидерланды|TCP, gRPC, XHTTP;"
    "🇫🇮 Финляндия|TCP, gRPC, XHTTP, Hysteria2;"
    "🇪🇪 Эстония|TCP, gRPC, XHTTP, Hysteria2;"
    "🇸🇪 Швеция|TCP, gRPC, XHTTP, Hysteria2"
)

NEW_HELP = r'''HELP_TEXT = (
    "<b>💡 Как подключиться</b>\n\n"
    "<b>1️⃣ Установите приложение</b>\n"
    "⭐ <b>Happ</b>: рекомендуем\n"
    "🔹 <b>Karing</b>: запасной вариант\n"
    "🔹 <b>Incy</b>: запасной вариант\n"
    "Все бесплатные, есть для iPhone, Android, Windows и macOS. Найдите по названию в App Store или Google Play.\n"
    "<i>Incy есть в российском App Store. Happ там может не находиться: тогда выберите Incy "
    "или установите Happ с Apple ID другой страны.</i>\n\n"
    "<b>2️⃣ Нажмите кнопку подключения</b>\n"
    "Кнопки «📲 Подключить в …» находятся под этим сообщением и в «Мои подписки» → «Подписка 1». "
    "Откроется страница, затем приложение само предложит добавить подписку. Подтвердите.\n"
    "Если подписки у вас ещё нет, кнопки появятся после её оформления.\n"
    "<i>Кнопка не сработала? Нажмите «📋 Скопировать ссылку», в приложении выберите «+» "
    "и импорт подписки из буфера обмена.</i>\n\n"
    "<b>3️⃣ Разрешите VPN-конфигурацию</b> при первом запуске на iPhone.\n\n"
    "<b>4️⃣ Включите соединение</b> и выберите сервер.\n\n"
    "<b>🌍 Серверы</b>\n"
    "В подписке серверы в шести странах. Если один не работает, выберите другой или другой тип подключения "
    "(TCP, gRPC, XHTTP, Hysteria2).\n"
    "<i>Hysteria2 отображается в Happ и Karing, в Incy такие серверы не показываются.</i>\n\n"
    "<b>🛠 Не подключается?</b>\n"
    "• Обновите подписку в приложении (значок обновления)\n"
    "• Выберите другой сервер или другой тип подключения\n"
    "• Если страница открылась, а приложение нет: меню страницы → «Открыть в браузере»\n"
    "• Напишите в поддержку, мы поможем"
)'''

NEW_STATIC = '''    if config.SERVERS_STATIC:
        lines = []
        for item in config.SERVERS_STATIC.split(";"):
            if not item.strip():
                continue
            name, _, kinds = item.partition("|")
            line = f"▫️ <b>{html.escape(name.strip())}</b>"
            if kinds.strip():
                line += f"\\n└ <i>{html.escape(kinds.strip())}</i>"
            lines.append(line)
        text = ("<b>🌐 Серверы YamaVPN</b>\\n\\n" + "\\n".join(lines)
                + "\\n\\n🚀 <b>Hysteria2</b> работает в Happ и Karing, в Incy такие серверы не отображаются."
                "\\nВыберите любой сервер в приложении: если один не работает, попробуйте другой.")
        return await show(c, text, kb([HOME]))
'''

s = open("main.py", encoding="utf-8").read()
orig = s
log = []

# 1. порядок кнопок: Happ, Karing, Incy
m = re.search(r'for title, app in \(\(.*?\)\):', s)
if m:
    s = s.replace(m.group(0), 'for title, app in (("Happ ⭐", "happ"), ("Karing", "karing"), ("Incy", "incy")):')
    log.append("кнопки: Happ, Karing, Incy")
else:
    log.append("ВНИМАНИЕ: кнопки подключения не найдены (сначала примените apply_connect_buttons.py)")

# 2. приветствие
s = re.sub(r"Нажмите кнопку своего приложения: Karing, Happ или Incy", "Нажмите кнопку своего приложения: Happ, Karing или Incy", s)

# 3. «Инструкции»
m = re.search(r"HELP_TEXT = \(\n.*?\n\)", s, re.S)
if m:
    s = s[:m.start()] + NEW_HELP + s[m.end():]
    log.append("инструкции обновлены")

# 4. список серверов
head = "async def cb_servers(c: CallbackQuery):\n"
if head in s:
    s = re.sub(r"    if config\.SERVERS_STATIC:\n.*?return await show\(c, text, kb\(\[HOME\]\)\)\n", "", s, count=1, flags=re.S)
    s = s.replace(head, head + NEW_STATIC, 1)
    log.append("список серверов обновлён")

if s != orig:
    shutil.copy("main.py", "main.py.bak-apps")
    open("main.py", "w", encoding="utf-8").write(s)

c = open("config.py", encoding="utf-8").read()
if "SERVERS_STATIC" not in c:
    open("config.py", "a", encoding="utf-8").write('\nSERVERS_STATIC = env("SERVERS_STATIC")\n')
    log.append("config.py: SERVERS_STATIC добавлен")

# 5. .env
line = 'SERVERS_STATIC="%s"' % SERVERS
try:
    shutil.copy(".env", ".env.bak-apps")
except FileNotFoundError:
    pass
try:
    lines = open(".env", encoding="utf-8").read().split("\n")
except FileNotFoundError:
    lines = []
for i, l in enumerate(lines):
    if l.startswith("SERVERS_STATIC="):
        lines[i] = line
        break
else:
    if lines and lines[-1] == "":
        lines.insert(len(lines) - 1, line)
    else:
        lines.append(line)
open(".env", "w", encoding="utf-8").write("\n".join(lines))
log.append(".env: SERVERS_STATIC обновлён")

print("\n".join(log))

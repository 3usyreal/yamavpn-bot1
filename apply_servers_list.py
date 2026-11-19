"""Список серверов в боте можно задать вручную: переменная SERVERS_STATIC в .env.
Пример: SERVERS_STATIC="🇵🇱 Польша;🇩🇪 Германия;🇳🇱 Нидерланды". Если переменная пустая, список берётся из панели.
Запуск из каталога бота."""
import shutil

HEAD = "async def cb_servers(c: CallbackQuery):\n"
INSERT = '''    if config.SERVERS_STATIC:
        lines = [f"• {html.escape(x.strip())}" for x in config.SERVERS_STATIC.split(";") if x.strip()]
        text = ("<b>Список серверов</b>\\n\\n" + "\\n".join(lines)
                + "\\n\\nВ каждой стране доступны профили TCP, gRPC и XHTTP. "
                "В приложении выберите любой сервер из списка. Если один не работает, попробуйте другой.")
        return await show(c, text, kb([HOME]))
'''

s = open("main.py", encoding="utf-8").read()
if "SERVERS_STATIC" in s:
    print("main.py уже обновлён")
else:
    assert HEAD in s, "cb_servers не найден: main.py не изменён"
    shutil.copy("main.py", "main.py.bak-servers")
    open("main.py", "w", encoding="utf-8").write(s.replace(HEAD, HEAD + INSERT, 1))
    print("main.py обновлён")

c = open("config.py", encoding="utf-8").read()
if "SERVERS_STATIC" not in c:
    open("config.py", "a", encoding="utf-8").write('\n# Список стран для экрана «Список серверов» (через ;). Пусто: брать из панели.\nSERVERS_STATIC = env("SERVERS_STATIC")\n')
    print("config.py обновлён")

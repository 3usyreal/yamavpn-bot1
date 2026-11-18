"""Обновляет «Инструкции»: текст под новый сценарий и кнопки Karing/Happ/Incy. Запуск из каталога бота."""
import re
import shutil

NEW_HELP = r'''HELP_TEXT = (
    "<b>💡 Как подключиться</b>\n\n"
    "<b>1️⃣ Установите приложение</b>\n"
    "⭐ Основное: <b>Karing</b>\n"
    "🔹 Запасные: <b>Happ</b> и <b>Incy</b>\n"
    "Все бесплатные, есть для iPhone, Android, Windows и macOS. Найдите по названию в App Store "
    "или Google Play. Если в вашем магазине приложения нет, скачайте его с сайта разработчика "
    "или выберите другое: Incy есть в российском App Store, для Happ нужен Apple ID другой страны.\n\n"
    "<b>2️⃣ Нажмите кнопку подключения</b>\n"
    "Кнопки «📲 Подключить в …» находятся под этим сообщением и в «Мои подписки» → «Подписка 1». "
    "Откроется страница, затем приложение само предложит добавить подписку, подтвердите. "
    "Если подписки у вас ещё нет, кнопки появятся после её оформления.\n\n"
    "<b>Кнопка не сработала?</b> Нажмите «📋 Скопировать ссылку», в приложении выберите «+» "
    "и импорт подписки из буфера обмена.\n\n"
    "<b>3️⃣ Разрешите VPN-конфигурацию</b> при первом запуске на iPhone.\n\n"
    "<b>4️⃣ Включите соединение</b> и проверьте, что интернет работает.\n\n"
    "<b>Не подключается?</b>\n"
    "• Обновите подписку в приложении (кнопка обновления рядом с ней)\n"
    "• Выберите другой сервер из списка в приложении или попробуйте другое приложение\n"
    "• Если страница открылась, а приложение нет: меню страницы → «Открыть в браузере»\n"
    "• Напишите в поддержку, мы поможем"
)'''

NEW_CB = '''@router.callback_query(F.data == "help")
async def cb_help(c: CallbackQuery):
    rows = []
    try:
        u = await mz.get_user(uname(c.from_user.id))
        if u and u.get("subscription_url"):
            rows = copy_row(u["subscription_url"])
    except Exception:
        log.exception("help: не удалось получить подписку")
    await show(c, HELP_TEXT, kb(rows + [("🛟 Поддержка", config.SUPPORT_URL), HOME]))
'''

s = open("main.py", encoding="utf-8").read()
if "Запасные: <b>Happ</b>" in s:
    print("«Инструкции» уже обновлены")
else:
    m1 = re.search(r"HELP_TEXT = \(\n.*?\n\)\n", s, re.S)
    m2 = re.search(r'@router\.callback_query\(F\.data == "help"\)\nasync def cb_help\(c: CallbackQuery\):\n.*?\n(?=\n\n)', s, re.S)
    assert m1 and m2, "HELP_TEXT или cb_help не найдены: main.py не изменён"
    shutil.copy("main.py", "main.py.bak-help")
    s = s[:m1.start()] + NEW_HELP + "\n" + s[m1.end():]
    m2 = re.search(r'@router\.callback_query\(F\.data == "help"\)\nasync def cb_help\(c: CallbackQuery\):\n.*?\n(?=\n\n)', s, re.S)
    s = s[:m2.start()] + NEW_CB.rstrip("\n") + "\n" + s[m2.end():]
    open("main.py", "w", encoding="utf-8").write(s)
    print("main.py обновлён")

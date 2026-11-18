"""Оплата картой/СБП через встроенные платежи Telegram (ЮKassa в BotFather).
Запрос к ЮKassa делает сам Telegram, поэтому серверу не нужен доступ к api.yookassa.ru.
Запуск из каталога бота. Добавьте TG_PAY_TOKEN в .env (токен из BotFather → Payments)."""
import shutil

IMPORT_OLD = "from aiogram.types import CallbackQuery, CopyTextButton, ErrorEvent, Message"
IMPORT_NEW = "from aiogram.types import CallbackQuery, CopyTextButton, ErrorEvent, LabeledPrice, Message, PreCheckoutQuery"

PLAN_OLD = '''    if config.YOOKASSA_SHOP_ID and config.YOOKASSA_SECRET_KEY:
        rows.append(("💳 Карта / СБП", f"payyoo:{key}"))'''
PLAN_NEW = '''    if config.TG_PAY_TOKEN:
        rows.append(("💳 Карта / СБП", f"payinv:{key}"))
    elif config.YOOKASSA_SHOP_ID and config.YOOKASSA_SECRET_KEY:
        rows.append(("💳 Карта / СБП", f"payyoo:{key}"))'''

ANCHOR = "@router.error()\nasync def on_error(e: ErrorEvent):"
HANDLERS = '''@router.callback_query(F.data.startswith("payinv:"))
async def cb_invoice(c: CallbackQuery):
    key = c.data.split(":")[1]
    p = config.PLANS[key]
    await c.message.answer_invoice(
        title=f"YamaVPN — {p['title']}",
        description="Подписка YamaVPN, безлимитный трафик",
        payload=f"{c.from_user.id}:{key}",
        provider_token=config.TG_PAY_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=p["title"], amount=int(p["price"]) * 100)],
    )
    await c.answer()


@router.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery):
    try:
        uid, key = q.invoice_payload.split(":")
        ok = int(uid) == q.from_user.id and key in config.PLANS
    except ValueError:
        ok = False
    await q.answer(ok=ok, error_message=None if ok else "Платёж недействителен, начните оплату заново")


@router.message(F.successful_payment)
async def on_paid(m: Message):
    sp = m.successful_payment
    uid, key = sp.invoice_payload.split(":")
    ext_id = f"tg:{sp.telegram_payment_charge_id}"
    await db.add_payment(int(uid), key, "tgpay", ext_id, "pending")
    await settle(m.bot, ext_id)
    log.info("tgpay paid: %s %s", uid, key)


'''

s = open("main.py", encoding="utf-8").read()
if "payinv:" in s:
    print("main.py уже обновлён")
else:
    for old in (IMPORT_OLD, PLAN_OLD, ANCHOR):
        assert old in s, "не найден фрагмент: " + old[:50] + " (main.py не изменён)"
    shutil.copy("main.py", "main.py.bak-tgpay")
    s = s.replace(IMPORT_OLD, IMPORT_NEW).replace(PLAN_OLD, PLAN_NEW).replace(ANCHOR, HANDLERS + ANCHOR)
    open("main.py", "w", encoding="utf-8").write(s)
    print("main.py обновлён")

c = open("config.py", encoding="utf-8").read()
if "TG_PAY_TOKEN" not in c:
    open("config.py", "a", encoding="utf-8").write('\n# Токен платежей Telegram (BotFather -> Payments -> ЮKassa)\nTG_PAY_TOKEN = env("TG_PAY_TOKEN")\n')
    print("config.py обновлён")

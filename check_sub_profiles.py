"""Проверка реальной подписки НОВОГО клиента: сколько профилей и какие названия внутри.
Создаёт tgtest9, скачивает его подписку, печатает только названия, удаляет клиента.
Ссылки, UUID и токены не печатаются. Запуск: python3 check_sub_profiles.py"""
import asyncio
import base64
import time
from urllib.parse import unquote, urlparse

import aiohttp

import config
from h1 import H1Panel

NAME = "tgtest9"
UA = {"User-Agent": "v2rayNG/1.8.5", "Accept": "*/*"}


async def fetch(url):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12)) as s:
        async with s.get(url, headers=UA) as r:
            return r.status, r.headers.get("content-type", ""), await r.text()


def names_from(body):
    text = body
    try:
        text = base64.b64decode(body.strip() + "=" * (-len(body.strip()) % 4)).decode("utf-8", "ignore")
    except Exception:
        pass
    lines = [l.strip() for l in text.splitlines() if "://" in l]
    return [unquote(l.split("#", 1)[1]) if "#" in l else "(без названия)" for l in lines]


async def main():
    p = H1Panel()
    if await p.get_user(NAME):
        await p._request("DELETE", f"/clients/{NAME}")
    try:
        u = await p.create_user(NAME, int(time.time()) + 86400)
        await asyncio.sleep(70)  # связка синхронизируется раз в минуту
        sub = u["subscription_url"]
        pr = urlparse(sub)
        base = config.H1_API_URL.rsplit("/api", 1)[0]
        alt = base + pr.path + (("?" + pr.query) if pr.query else "")
        for label, url in (("адрес панели", sub), ("прямой адрес", alt)):
            try:
                status, ctype, body = await fetch(url)
            except Exception as e:
                print(f"{label}: ошибка {type(e).__name__}")
                continue
            names = names_from(body)
            print(f"{label}: HTTP {status}, {ctype.split(';')[0]}, профилей: {len(names)}")
            for n in names:
                print("  -", n)
            if names:
                break
    finally:
        await p._request("DELETE", f"/clients/{NAME}")
        print("тестовый клиент удалён")


asyncio.run(main())

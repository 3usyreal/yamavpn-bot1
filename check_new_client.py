"""Проверка: какие профили получает НОВЫЙ клиент. Создаёт tgtest9, печатает только названия профилей, удаляет его.
Ссылки, UUID и токены не печатаются. Запуск: python3 check_new_client.py"""
import asyncio
import time
from urllib.parse import unquote

from h1 import H1Panel

NAME = "tgtest9"


def label(x):
    if isinstance(x, str):
        return unquote(x.split("#", 1)[1]) if "#" in x else "(без названия)"
    if isinstance(x, dict):
        for k in ("name", "remark", "label", "title", "tag"):
            if x.get(k):
                return str(x[k])
        return "dict: " + ", ".join(sorted(x.keys()))
    return type(x).__name__


async def main():
    p = H1Panel()
    if await p.get_user(NAME):
        await p._request("DELETE", f"/clients/{NAME}")
    try:
        await p.create_user(NAME, int(time.time()) + 86400)
        await asyncio.sleep(3)
        c = await p.get_user(NAME)
        links = c.get("inbound_links") or []
        print("профилей у нового клиента:", len(links))
        for x in links:
            print(" -", label(x))
        print("links (ключи):", sorted((c.get("links") or {}).keys()))
        print("fed_nodes:", c.get("fed_nodes"))
    finally:
        await p._request("DELETE", f"/clients/{NAME}")
        print("тестовый клиент удалён")


asyncio.run(main())

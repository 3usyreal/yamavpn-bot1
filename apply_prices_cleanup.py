"""Новые цены (149 / 410 / 1490 ₽) и удаление устаревшей команды /fixflow. Запуск из каталога бота."""
import re
import shutil

NEW_PRICES = {"m1": 149, "m3": 410, "m12": 1490}

c = open("config.py", encoding="utf-8").read()
changed = False
for key, price in NEW_PRICES.items():
    pat = re.compile(r'("%s":\s*\{[^}]*"price":\s*)\d+' % key)
    assert pat.search(c), "тариф %s не найден в config.py" % key
    new_c = pat.sub(r"\g<1>%d" % price, c)
    changed = changed or new_c != c
    c = new_c
if changed:
    shutil.copy("config.py", "config.py.bak-prices")
    open("config.py", "w", encoding="utf-8").write(c)
    print("config.py: цены обновлены (149 / 410 / 1490)")
else:
    print("config.py: цены уже такие")

s = open("main.py", encoding="utf-8").read()
pat = re.compile(r'@router\.message\(Command\("fixflow"\)\)\nasync def cmd_fixflow\(m: Message\):\n.*?\n\n\n(?=@router)', re.S)
if pat.search(s):
    shutil.copy("main.py", "main.py.bak-cleanup")
    open("main.py", "w", encoding="utf-8").write(pat.sub("", s, count=1))
    print("main.py: команда /fixflow удалена")
else:
    print("main.py: /fixflow уже удалена")

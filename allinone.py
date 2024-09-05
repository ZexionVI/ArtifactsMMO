from Artifacts_classes import MMOAPI
from SuperCraft import s_craft
from SuperSkill import s_skill

print("Что ты хочешь сделать?")
print()
print("1)Крафт предмета;")
print("2)Поднятие скилла;")
v = int(input("Твой выбор: "))

if v == 1:
    token = input("Введи токен с сайта: ")
    name = input("Имя персонажа: ")
    optimize_weapone = input("Нужно ли менять оружие во время битвы с мобами? (y/n): ")
    while True:
        s_craft(name, token, optimize_weapone)

elif v == 2:
    token = input("Введи токен с сайта: ")
    name = input("Имя персонажа: ")
    optimize_weapone = input("Нужно ли менять оружие во время битвы с мобами? (y/n): ")
    while True:
        s_skill(name, token, optimize_weapone)
else:
    print("Хуита")

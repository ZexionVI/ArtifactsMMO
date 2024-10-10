from Artifacts_classes import MMOAPI
from SuperCraft import s_craft
from SuperSkill import s_skill

print("Что ты хочешь сделать?")
print()
print("1)Крафт предмета;")
print("2)Поднятие скилла;")
v = int(input("Твой выбор: "))
token = input("Введи токен с сайта: ")
character = input("Имя персонажа: ")
o_w = input("Нужно ли менять оружие во время битвы с мобами? (y/n): ")

if v == 1:
    while True:
        s_craft(character, token, o_w)

elif v == 2:    
    while True:
        s_skill(character, token, o_w)
else:
    print("Хуита")

from Artifacts_classes import MMOAPI
from SuperCraft import s_craft
from SuperSkill import s_skill

print("Что ты хочешь сделать?")
print()
print("1)Крафт предмета;")
print("2)Поднятие скилла;")
v = int(input("Твой выбор: "))

if v == 1:
    while True:
        name = input("Имя персонажа: ")
        s_craft(name)

elif v == 2:
    name = input("Имя персонажа: ")
    while True:
        s_skill(name)
else:
    print("Хуита")

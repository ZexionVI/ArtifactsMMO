import requests
import time


#Необходимые доработки:
#+0.2v (1 на оружие и 1 на броню)
#Во время боя нужно менять оружие и одежду подстраиваясь по моба:
##В теории надо считать уязвимости противника и тип урона.
##Исходя из этого надо выбрат оружие из тех что лежат в инвенторе и одежду из той что есть в инвентаре  

#+0.1v
#Сделать проверку свободных мест в инвентаре. Если же места в инвентаре не хватит, то отдавать соответствующую ошибку и заканчивать работу

#+0.1v
#Нужно сделат продажу добытых предметов и выбор кол-ва предметов

#up до v2.0
#Переработать вывод и дизайн вывода. Возможно переработать ввод данных.

#up до v3.0
#Проверка предметов в банке. Если есть необходимые предметы, то перейти к банку и взять их.
#Если в инвентаре есть ненужные предметы, то сложить их в банк.


#Разделим на действия.
#Во-первых нужен вывод возможных предметов для крафта. Конец первого этапа - ввод нужного предмета. Функции для этого: skills и items_from_level

#Во-вторых надо разбить предмет для крафта на составные. А эти составные на подсоставные и так до конца. Потом вывести весь путь с местами добычи и крафтами (в разработке)

#В-третьих получив 2 списка со всей нужной инфой, делаем поочередный move к нужному ресурсу и начинаем добычу или убийство моба. Добывать нужно пока в инвентаре не будет нужного кол-ва предметов
#Также в третьем пункте итоговый крафт по всем путям


#######################
#####Блок с константами

#Адрес сервера для обращения к апишкам
server = "https://api.artifactsmmo.com"

#Токен пользователя и имя персонажа
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlpleGlvbiIsInBhc3N3b3JkX2NoYW5nZWQiOiIifQ.28oPeGddQ5u5gUlYaHTjkHlzcaTmHFM6Rn7DrDKroN0"

character = input("Выбери перса (Jan3 or Lil_Z or Aryan):")

#Апишки для взаимодействий
gathering_url = f"{server}/my/{character}/action/gathering"
move_url = f"{server}/my/{character}/action/move"
craft_url = f"{server}/my/{character}/action/crafting"
character_url = f"{server}/characters/{character}"
fight_url = f"{server}/my/{character}/action/fight"
maps_url = f"{server}/maps/"
monsters_url = f"{server}/monsters/"
items_url = f"{server}/items/"
resources_url = f"{server}/resources/"
unequip_url = f"{server}/my/{character}/action/unequip"
equip_url = f"{server}/my/{character}/action/equip"

#заголовки необходимые для апишек
headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
#######################
#######################


#######################
#####Блок с переменными
components = []
craft_road = []
#######################
#######################


##########################################################
###############---  Блок первого этапа  ---###############

#Функция скилов. Ничего не принимает. Возвращает словарь с названием скила и его уровнем.
def skills():

    character_response = requests.get(character_url, headers=headers)

    if character_response.status_code == 404:
        print("Map not found.")
        exit()
    elif character_response.status_code != 200:
        print("Какая-то херня в функции skils")
        exit()
    else:
        character_response_data = character_response.json()["data"]

    levels = {}


    for skill in character_response_data:
        if skill == "mining_level":
            levels["mining"] = character_response_data[skill]
        if skill == "woodcutting_level":
            levels["woodcutting"] = character_response_data[skill]
        if skill == "weaponcrafting_level":
            levels["weaponcrafting"] = character_response_data[skill]
        if skill == "gearcrafting_level":
            levels["gearcrafting"] = character_response_data[skill]
        if skill == "cooking_level":
            levels["cooking"] = character_response_data[skill]
        if skill == "jewelrycrafting_level":
            levels["jewelrycrafting"] = character_response_data[skill]



    return(levels)

#Функиця предметов для скила. Принимает название скила и его уровень. Ничего не возвращает. Выводит название скила и возможные предметы крафта
def items_from_level(skill, level):

    payload = {
        "max_level": level,
        "craft_skill": skill
    }

    items_response = requests.get(items_url, headers=headers, params=payload)

    if items_response.status_code == 404:
        print("Items not found.")
        exit()
    elif items_response.status_code != 200:
        print("Какая-то херня в функции items_from_level")
        print(items_response.json())
        exit()
    else:
        items_data = items_response.json()["data"]
    
    i=0
    print(f"{skill}-{level}:")
    for i in range(len(items_data)):
        name = items_data[i]["code"]
        print_name = "     " + str(i+1) + "." + str(name)
        print(print_name)

#Первое действие - узнать уровень скилов и вывести их
levels = skills()

#В зависимости от уровней предложить что можно крафтить
for level in levels.keys():
    items_from_level(level, levels[level])

item = input("Выбери что-то:\n")
quantity = int(input("Сколько?\n"))

print("Конец 1 этапа")
##########################################################
##########################################################

stop = input("Stop!! Просто нажми Enter чтобы продолжить")

##########################################################
##############---   Блок второго этапа   ---##############

#Функция определения имя ресурса по предмету. Принимает название предмета. Возвращает имя ресурса.
def resource_from_item(name):

    payload_resources = {
        "drop": name
    }

    resources_response = requests.get(resources_url, params=payload_resources, headers=headers)

    if resources_response.status_code == 404:
        print("Map not found.")
        exit()
    elif resources_response.status_code != 200:
        print("Какая-то херня в item_map")
        exit()
    else:
        resources_data = resources_response.json()["data"][0]
        resource = resources_data["code"]
        return resource

#Функция определения монстра по дропа. Принимает название предмета. Возвращает имя монстра.
def monster_from_item(drop):

    payload = {
        "drop": drop
    }

    monsters_drop_response = requests.get(monsters_url, params=payload, headers=headers)

    if monsters_drop_response.status_code == 404:
        print("Monster not found.")
        exit()
    elif monsters_drop_response.status_code != 200:
        print("Какая-то херня в monsters")
        exit()
    else:
        monsters_drop_data = monsters_drop_response.json()["data"][0]

    return monsters_drop_data["code"]

#Функция разбора предмета на компоненты. Принимает название предмета и кол-во. Ничего не возвращает, но записывает в спискни необходимые данные
def craft_from_item(item, quantity):

    #объявление списка для всех функций
    global components
    global craft_road

    #Создание юрл и обращение к ней
    item_url = items_url + item
    item_response = requests.get(item_url, headers=headers)

    #Ошибки
    if item_response.status_code == 404:
        print("Item not found.")
        exit()
    elif item_response.status_code != 200:
        print("Какая-то херня в функции craft_from_item")
        print(item_response.json())
        exit()
    else:

        #Запись вывода в переменную
        item_data = item_response.json()["data"]["item"]

        #Проверка на то надо ли компонент крафтить
        if item_data["subtype"] == "task":
            print("Нужен предмет из заданий:")
            print(item_data["code"], quantity)

        elif item_data["craft"] == None:
            if item_data["subtype"] == "mob" or item_data["subtype"] == "food":
                mob = monster_from_item(item)
                #Добавление в список название компонента, кол-во и имя моба
                components.append({"code": item, "quantity": quantity, "mob":mob, "subtype":item_data["subtype"]})
            else:
                resource = resource_from_item(item)
                #Добавление в список название компонентаего, кол-во и название ресурса
                components.append({"code": item, "quantity": quantity, "resource":resource, "subtype":item_data["subtype"]})

        else:

            craft_road.append({"code": item, "skill":item_data["craft"]["skill"], "quantity":quantity})

            #Цикл для проверки по всем предметам для крафта
            for i in range(len(item_data["craft"]["items"])):
            
                #Кол-во и название компонентов
                quantity_component = item_data["craft"]["items"][i]["quantity"] * quantity
                component = item_data["craft"]["items"][i]["code"]

                craft_from_item(component, quantity_component)

#Вызов функции
craft_from_item(item, quantity)

#Вывод спискса компонентов и их кол-ва
print(components)

#Разворот списка и вывод списка из скила крафта и предмета
craft_road.reverse()
print(craft_road)

print("Конец 2 этапа")
##########################################################
##########################################################

stop = input("Stop!! Просто нажми Enter чтобы продолжить")

##########################################################
##############---   Блок третьего этапа   ---#############

#Функция перемещения. Принимает координаты чего-либо. Возвращает кулдаун int в секундах. 
def move(x, y) -> int:

    payload = {
        "x": x,
        "y": y
    }

    move_response = requests.post(move_url, json=payload, headers=headers)
    

    if move_response.status_code == 404:
        print("Map not found.")
        exit()
    elif move_response.status_code == 486:
        print("Character is locked. Action is already in progress.")
        exit()
    elif move_response.status_code == 490:
        print("Character already at destination")
        return 0
    elif move_response.status_code == 498:
        print("Character not found.")
        exit()
    elif move_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif move_response.status_code != 200:
        print("Какая-то херня в move")
        print(move_response.json())
        exit()
    else:
        move_data = move_response.json()["data"]
        return move_data["cooldown"]["total_seconds"]

#Функция определения местоположения монстра или ресурса. Принимает название. Возвращает список с координатами (x, y)
def map(name):
    
    payload = {
        "content_code": name
    }

    monster_map_response = requests.get(maps_url, params=payload, headers=headers)

    if monster_map_response.status_code == 404:
        print("Map not found.")
        exit()
    elif monster_map_response.status_code != 200:
        print("What the fuck?")
        exit()
    else:
        monster_map_data = monster_map_response.json()["data"][0]

    return monster_map_data["x"], monster_map_data["y"]

#Функция определения местоположения воркшопа. Принимает название. Возвращает список с координатами (x, y)
def workshop_map(name):
    
    payload = {
        "content_type":"workshop",
        "content_code": name
    }

    workshop_map_response = requests.get(maps_url, params=payload, headers=headers)

    if workshop_map_response.status_code == 404:
        print("Map not found.")
        exit()
    elif workshop_map_response.status_code != 200:
        print("What the fuck map?")
        exit()
    else:
        workshop_map_data = workshop_map_response.json()["data"][0]

    return workshop_map_data["x"], workshop_map_data["y"]

#Функция добычи. Ничего не принимает. Возвращает кулдаун int в секундах.
def gathering() -> int:

    gathering_response = requests.post(gathering_url, headers=headers)

    if gathering_response.status_code == 486:
        print("Character is locked. Action is already in progress.")
        exit()
    elif gathering_response.status_code == 493:
        print("Not skill level required.")
        exit()
    elif gathering_response.status_code == 497:
        print("Your character's inventory is full.")
        exit()
    elif gathering_response.status_code == 498:
        print("Character not found.")
        exit()
    elif gathering_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif gathering_response.status_code == 598:
        print("Resource not found on this map.")
        exit()
    elif gathering_response.status_code != 200:
        print("Какая-то херня в gathering")
        exit()
    else:
        gathering_data = gathering_response.json()["data"]
#        receive_quantity = gathering_data["details"]["items"][0]["quantity"]
        cooldown = gathering_data["cooldown"]["total_seconds"]

        return cooldown

#Функция крафта. Принимает имя и кол-во предмета. Возвращает кулдаун int в секундах.
def craft(item, q) -> int:

    payload = {
        "code": item,
        "quantity": q
    }

    craft_response = requests.post(craft_url, json=payload, headers=headers)

    if craft_response.status_code == 404:
        print("Craft not found.")
        exit()
    elif craft_response.status_code == 478:
        print("Missing item or insufficient quantity in your inventory.")
        exit()
    elif craft_response.status_code == 486:
        print("Character is locked. Action is already in progress.")
        exit()
    elif craft_response.status_code == 493:
        print("Not skill level required.")
        return 0
    elif craft_response.status_code == 497:
        print("Character inventory is full.")
        exit()
    elif craft_response.status_code == 498:
        print("Character not found.")
        exit()
    elif craft_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif craft_response.status_code == 598:
        print("Workshop not found on this map.")
        exit()
    elif craft_response.status_code != 200:
        print("What the fuck craft?")
        exit()
    else:
        craft_response_data = craft_response.json()["data"]
        return craft_response_data["cooldown"]["total_seconds"]

#Функция для подсчёта кол-ва предметов. Возвращает кол-во предмета int.
def count(name) -> int:
    
    character_response = requests.get(character_url, headers=headers)
    character_response_data = character_response.json()["data"]["inventory"]

    quantity = 0
    for i in range(len(character_response_data)):
        if character_response_data[i]["code"] == name:
            quantity = character_response_data[i]["quantity"]

    return quantity

#Апи для боя. Возвращает кулдаун в секундах.
def fight() -> int:

    fight_response = requests.post(fight_url, headers=headers)

    if fight_response.status_code == 486:
        print("Character is locked. Action is already in progress.")
        exit()
    elif fight_response.status_code == 497:
        print("Your character's inventory is full.")
        exit()
    elif fight_response.status_code == 498:
        print("Character not found.")
        exit()
    elif fight_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif fight_response.status_code == 598:
        print("Monster not found on this map.")
        exit()
    elif fight_response.status_code != 200:
        print("What the fuck attack?")
        exit()
    else:
        fight_data = fight_response.json()["data"]
        if fight_data["fight"]["result"] == "lose":
            print("Соснул у моба!")
            exit()
        xp = fight_data["fight"]["xp"]
        gold = fight_data["fight"]["gold"]
        drops =  fight_data["fight"]["drops"]

        print("Won!")
        print("XP:", xp)
        print("Gold:", gold)
        for i in range(len(drops)):
            item = drops[i]["code"]
            quantity = drops[i]["quantity"]
            print("Drop:", quantity, item)

        #Return the cooldown in seconds
        return fight_data["cooldown"]["total_seconds"]

#Функция для снятия предмета. Принимает название слота из которого надо снять предмет.
def unequip(slot) -> int:

    payload = { "slot": slot }
    
    unequip_response = requests.post(unequip_url, headers=headers, json=payload)

    #Ошибки
    if unequip_response.status_code == 404:
        print("Item not found.")
        exit()
    elif unequip_response.status_code == 486:
        print("An action is already in progress by your character.")
        exit()
    elif unequip_response.status_code == 491:
        print("Slot is empty.")
        exit()
    elif unequip_response.status_code == 497:
        print("Character inventory is full.")
        exit()
    elif unequip_response.status_code == 498:
        print("Character not found.")
        exit()
    elif unequip_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif unequip_response.status_code != 200:
        print("Какая-то херня в unequip")
        print(unequip_response.json())
        exit()
    else:
        unequip_data = unequip_response.json()["data"]

        return unequip_data["cooldown"]["total_seconds"]

#Функция для экипировки предмета. Принимает название предмета в инвенторе и слот в который его надо экипировать.
def equip(item, slot) -> int:

    payload = {
        "code": item,
        "slot": slot 
    }
    
    equip_response = requests.post(equip_url, headers=headers, json=payload)

    #Ошибки
    if equip_response.status_code == 404:
        print("Item not found.")
        exit()
    elif equip_response.status_code == 478:
        print("Missing item or insufficient quantity in your inventory.")
        exit()
    elif equip_response.status_code == 485:
        print("This item is already equipped.")
        exit()
    elif equip_response.status_code == 486:
        print("An action is already in progress by your character.")
        exit()
    elif equip_response.status_code == 491:
        print("Slot is not empty.")
        exit()
    elif equip_response.status_code == 496:
        print("Character level is insufficient.")
        exit()
    elif equip_response.status_code == 498:
        print("Character not found.")
        exit()
    elif equip_response.status_code == 499:
        print("Character in cooldown.")
        exit()
    elif equip_response.status_code != 200:
        print("Какая-то херня в unequip")
        exit()
    else:
        equip_data = equip_response.json()["data"]

        return equip_data["cooldown"]["total_seconds"]

#Функция для получения информации о предмете. Принимает название предмета. Возвращает словарь с инфой о предмете.
def item_info(item):

    #Создание юрл и обращение к ней
    item_url = items_url + item
    item_response = requests.get(item_url, headers=headers)

    #Ошибки
    if item_response.status_code == 404:
        print("Item not found.")
        exit()
    elif item_response.status_code != 200:
        print("Какая-то херня в функции craft_from_item")
        print(item_response.json())
        exit()
    else:

        #Запись вывода в переменную
        item_data = item_response.json()["data"]["item"]

        return item_data

#Функция находящая минимум в словаре
def max(type):
    buffer = 0
    for key in type.keys():
        if type[key] > buffer:
            buffer = type[key]
            max = key
    return max
#Функция находящая максимум в словаре
def min(type):
    buffer = 100
    for key in type.keys():
        if type[key] < buffer:
            buffer = type[key]
            min = key
    return min

#####ДОРАБОТАТЬ!!!
#####ДОРАБОТАТЬ!!!
#####ДОРАБОТАТЬ!!!

#Функция которая принимает имя монстра. Просматривает его характеристики защиты и характеристики атаки персонажа, а также оружие. Меняет оружие на то которое будет подходить под наименьшую защиту монстра.
def adaptability(monster_name):

    #Два словаря, в которые будут записываться защита монстра и атака персонажа
    M_res_type = {}
    P_attacks_type = {}

    #Обращение к апишке с инфой о персонаже
    character_response = requests.get(character_url, headers=headers)
    character_response_data = character_response.json()["data"]

    #Запись в словарь всех типов атаки что есть
    for key in character_response_data.keys():
        if "attack_" in key:
            P_attacks_type[key] = character_response_data[key]
    print(f"Типы атаки персонажа: {P_attacks_type}")

    #Обращение к апишке с инфой о монстре
    monster_url = monsters_url + monster_name
    monster_response = requests.get(monster_url, headers=headers)
    monster_response_data = monster_response.json()["data"]

    #Запись в словарь всех типов защиты что есть
    for key in monster_response_data.keys():
        if "res_" in key:
            M_res_type[key] = monster_response_data[key]
    print(f"Типы защиты монстра: {M_res_type}")

    #Макс атака перса и мин защита монстра
    P_max_attack = max(P_attacks_type)
    M_min_res = min(M_res_type)

    #Ёбнутая хуйня. Надо как-нибудь улучшить или вывести в отдельную функцию
    #По сути оно подстраивает оружие под мин защиту противника
    if M_min_res.split("_")[1] != P_max_attack.split("_")[1]:
        #Снять оружие
        print("Unequip weapon")
        unequip_cooldown = unequip("weapon")
        time.sleep(unequip_cooldown)
        #Надеть нужное оружие
        for item in character_response_data["inventory"]:
            if len(item["code"])<1:
                continue
            if "axe" in item["code"]:
                continue
            if item_info(item["code"])["type"] == "weapon":
                for effect in item_info(item["code"])["effects"]:
                    if effect["name"].split("_")[1] == M_min_res.split("_")[1]:
                        print("Equip", item["code"])
                        equip_cooldown = equip(item["code"], "weapon")
                        time.sleep(equip_cooldown)



#Цикл для каждого компонета в списке
for component in components:

    #Временный вывод компонента
    print(component)

    #Условие проверяющее моб или ресурс
    if "mob" in component:

        #Координаты
        x_c = map(component["mob"])[0]
        y_c = map(component["mob"])[1]

        #Передвижение к мобу
        mob = component["mob"]
        print(f"Передвижение к {mob}")
        move_cooldown = move(x_c, y_c)
        time.sleep(move_cooldown)

        #
        #Функция проверки защиты противника и смена оружия
        adaptability(mob)
        #

        #Подсчёт кол-ва предметов в инвенторе и цикл пока не будет в инвентаре нужного кол-ва
        q_inventory = count(component["code"])
        while q_inventory < component["quantity"]:

            c = component["code"]
            print(f"В инвентаре {q_inventory} - {c}")
            #Бой и кулдаун
            print(f"Бой с {mob}")
            kill_cooldown = fight()
            time.sleep(kill_cooldown)

            #Подсчёт кол-ва предметов
            q_inventory = count(component["code"])

    #Условие проверяющее моб или ресурс
    elif "resource" in component:
            
        #Координаты
        x_c = map(component["resource"])[0]
        y_c = map(component["resource"])[1]

        #Передвижение к ресурсу
        r = component["resource"]
        print(f"Передвижение к ресурсу {r}")
        move_cooldown = move(x_c, y_c)
        time.sleep(move_cooldown)

        #Подсчёт кол-ва предметов в инвенторе и цикл пока не будет в инвентаре нужного кол-ва
        q_inventory = count(component["code"])
        
        #Условие для изменения оружия на кирку/топор !!! УЖАСНЫЙ КОСТЫЛЬ! ПОФИКСИТЬ!!!
        if component["subtype"] == "mining" and character == "Jan3":
            print("Unequip weapon")
            unequip_cooldown = unequip("weapon")
            time.sleep(unequip_cooldown)

            print("Equip iron pickaxe")
            equip_cooldown = equip("iron_pickaxe", "weapon")
            time.sleep(equip_cooldown)
        elif component["subtype"] == "woodcutting" and character == "Jan3":
            print("Unequip weapon")
            unequip_cooldown = unequip("weapon")
            time.sleep(unequip_cooldown)

            print("Equip iron pickaxe")
            equip_cooldown = equip("iron_axe", "weapon")
            time.sleep(equip_cooldown)
            
        while q_inventory < component["quantity"]:

            c = component["code"]
            print(f"В инвентаре {q_inventory} - {c}")
            #Добыча и кулдаун
            print(f"Добыча {r}")
            gathering_cooldown = gathering()
            time.sleep(gathering_cooldown)

            #Подсчёт кол-ва предметов
            q_inventory = count(component["code"])
        
        #Тоже часть костыля!!!
        if (component["subtype"] == "mining" or component["subtype"] == "woodcutting") and character == "Jan3":
            print("Unequip weapon")
            unequip_cooldown = unequip("weapon")
            time.sleep(unequip_cooldown)
            
            print("Equip fire bow")
            equip_cooldown = equip("fire_bow", "weapon")
            time.sleep(equip_cooldown)

#Цикл для каждого шага крафта в списке
for step in craft_road:

    #Временный вывод шага
    print(step)

    #Координаты воркшопа
    x_s = workshop_map(step["skill"])[0]
    y_s = workshop_map(step["skill"])[1]

    #Передвижение
    s = step["skill"]
    print(f"Передвижение к {s}")
    move_cooldown = move(x_s, y_s)
    time.sleep(move_cooldown)

    #Крафт
    cr = step["code"]
    print(f"Крафт {cr}")
    craft_cooldown = craft(step["code"], step["quantity"])
    time.sleep(craft_cooldown)

print("Конец 3 этапа!! Просто нажми Enter чтобы продолжить")


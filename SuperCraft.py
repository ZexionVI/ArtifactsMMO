import time
from Artifacts_classes import MMOAPI

#Основные неизменные переменные (сервер, токен и выбор имени персонажа)
server = "https://api.artifactsmmo.com"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlpleGlvbiIsInBhc3N3b3JkX2NoYW5nZWQiOiIifQ.28oPeGddQ5u5gUlYaHTjkHlzcaTmHFM6Rn7DrDKroN0"

def item_list(api):
    skills = []
    # Первый этап: получение и отображение уровней скилов
    levels = api.get_character_skills() #запись в словарь навыки и их уровень. Вызов функции из класса (1)
    #print(levels)
    for skill, level in levels.items(): #Цикл по каждому навыку
        items = api.get_items_by_skill_level(skill, level) #Запись в список всех возможных предметов для крафта (2)
        skills.append({'skill': skill, 'level': level, 'items': items})
    for s in skills:
        print(f"{s['skill']} (уровень {s['level']})")
    i_skill = input("Выбери навык: ")
    for s in skills:
        if s['skill'] == i_skill:
            for item in s['items']:
                print(f"- {item}")

def craftnroad(api, item, quantity):
    # Второй этап: разбор и отображение необходимых компонентов
    api.craft_item(item, quantity) # Вызов апишки которая производит поиск крафта для предмета (3)
    print(f"Необходимые компоненты для создания {item}:")
    for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
        print(f"{component['code']} x {component['quantity']} ({component.get('mob') or component.get('resource')})") #Вывод компонета, его кол-во и моб/ресурс

    print("Маршрут крафта:")
    for road_item in reversed(api.craft_road): #Цикл для каждого элемента в списке с маршрутом крафта
        print(f"Создать {road_item['code']} в количестве {road_item['quantity']}") #Вывод что надо создать и в каком кол-ве

def mobfarm(api, component):

    x, y = api.find_location(component["mob"]) #Поиск местоположения моба (4)
    print(f"Move {x},{y}")
    move_cooldown = api.move_to(x, y) #Передвижение (5)
    time.sleep(move_cooldown) #Перерыв по кулдауну
    
    if optimize_weapone == "y":
        api.optimize_weapon_for_monster(component["mob"]) #Смена оружия (11)

    quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)
        
    while quantity_in_inventory <  component['quantity']: #Сражаться пока в инвентаре не будет нужного кол-ва пердмета
        print(f"{quantity_in_inventory} {component['code']} в инвенторе")
        print("Fight")
        fight_cooldown = api.fight_monster() #Бой с монстром (7)
        time.sleep(fight_cooldown)
        quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

def resourcefarm(api, component):
    x, y = api.find_location(component["resource"]) #Поиск местоположения ресурса (4)
    print(f"Move {x}, {y}")
    move_cooldown = api.move_to(x, y) #Передвижение (5)
    time.sleep(move_cooldown) #Перерыв по кулдауну

    quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

    pickaxe_quantity = api.get_quantity_item_inventory("pickaxe")
    axe_quantity = api.get_quantity_item_inventory("axe")
    
    #Условие для изменения оружия на кирку/топор !!! УЖАСНЫЙ КОСТЫЛЬ! ПОФИКСИТЬ!!!
    if component["subtype"] == "mining" and pickaxe_quantity != 0:
        print("Unequip weapon")
        unequip_cooldown = api.unequip_item("weapon")
        time.sleep(unequip_cooldown)

        print("Equip iron pickaxe")
        equip_cooldown = api.equip_item("iron_pickaxe", "weapon")
        time.sleep(equip_cooldown)

    elif component["subtype"] == "woodcutting" and axe_quantity != 0:
        print("Unequip weapon")
        unequip_cooldown = api.unequip_item("weapon")
        time.sleep(unequip_cooldown)

        print("Equip iron axe")
        equip_cooldown = api.equip_item("iron_axe", "weapon")
        time.sleep(equip_cooldown)

    while quantity_in_inventory <  component['quantity']: #Добывать пока в инвентаре не будет нужного кол-ва пердмета
        print(f"{quantity_in_inventory} {component['code']} в инвенторе")
        print("Gather")
        gather_cooldown = api.gather_resource() #Добыча предмета (8)
        time.sleep(gather_cooldown)
        quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

def finish_craft(api, craft_item):
    x, y = api.find_workshop_location(craft_item["skill"]) #Поиск местоположения нужного воркшопа (9)
    print(f"Move {x},{y}")
    move_cooldown = api.move_to(x, y) #Передвижение (5)
    time.sleep(move_cooldown)

    print(f"Craft {craft_item['code']}")
    craft_cooldown = api.craft(craft_item["code"], craft_item["quantity"]) #Крафт нужного предмета в нужном кол-ве (10)
    time.sleep(craft_cooldown)

def s_craft (character):

    global optimize_weapone

    optimize_weapone = input("Нужно ли менять оружие во время битвы с мобами? (y/n): ")


    api = MMOAPI(server, token, character) #Вызов класса, передача в него переменных

    item_list(api)

    item = input("Выберите предмет для крафта: ") #Выбор предмета крафта
    quantity = int(input("Сколько единиц создать? ")) #Ввод необходимого кол-ва предметов

    craftnroad(api, item, quantity)

    # Третий этап: выполнение действий
    for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
        if component["subtype"] in ["mob", "food"]: #Если предмет выбивается из моба
            mobfarm(api, component)

        elif "resource" in component: #Если предмет добывается из ресурса
            resourcefarm(api, component)

    for craft_item in reversed(api.craft_road): #Проход по всем этапам рецепта крафта
        finish_craft(api, craft_item)



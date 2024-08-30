import time
from Artifacts_classes import MMOAPI

#Основная функция в которой поэтапно выполняются все действия и т.д.
def main(character):
    
    #Основные неизменные переменные (сервер, токен и выбор имени персонажа)
    server = "https://api.artifactsmmo.com"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlpleGlvbiIsInBhc3N3b3JkX2NoYW5nZWQiOiIifQ.28oPeGddQ5u5gUlYaHTjkHlzcaTmHFM6Rn7DrDKroN0"
    global skill_for_up

    api = MMOAPI(server, token, character) #Вызов класса, передача в него переменных

    # Первый этап: получение и отображение уровней скилов
    levels = api.get_character_skills() #запись в словарь навыки и их уровень. Вызов функции из класса (1)
    for skill, level in levels.items(): #Цикл по каждому навыку
        
        print(f"{skill.capitalize()} (уровень {level}):") #Вывод названия и уровня навыка
        print(" ")
    if skill_for_up == "":
        skill_for_up = input("Выбери навык, который необходимо апнуть: ")
    items = api.get_items_by_skill_level(skill_for_up, level) #Запись в список всех возможных предметов для крафта (2)

    for item in items: #Цикл для вывода предметов для крафта для навыка
        if item in ("wooden_staff"):
            continue
        print(f"Начинается процесс для {item}")
        if skill_for_up == "Cooking":
            quantity = 10
        else:
            quantity = 1

        # Второй этап: разбор и отображение необходимых компонентов
        api.craft_item(item, quantity) # Вызов апишки которая производит поиск крафта для предмета (3)
        print(f"Необходимые компоненты для создания {item}:")
        for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
            print(f"{component['code']} x {component['quantity']} ({component.get('mob') or component.get('resource')})") #Вывод компонета, его кол-во и моб/ресурс

        print("Маршрут крафта:")
        for road_item in reversed(api.craft_road): #Цикл для каждого элемента в списке с маршрутом крафта
            print(f"Создать {road_item['code']} в количестве {road_item['quantity']}") #Вывод что надо создать и в каком кол-ве

        # Третий этап: выполнение действий
        for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
            if component["subtype"] in ["mob", "food"]: #Если предмет выбивается из моба
                x, y = api.find_location(component["mob"]) #Поиск местоположения моба (4)
                print(f"Move {x},{y}")
                move_cooldown = api.move_to(x, y) #Передвижение (5)
                time.sleep(move_cooldown) #Перерыв по кулдауну

                api.optimize_weapon_for_monster(component["mob"]) #Смена оружия (11)

                quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

                while quantity_in_inventory <  component['quantity']: #Сражаться пока в инвентаре не будет нужного кол-ва пердмета
                    print(f"{quantity_in_inventory} {component['code']} в инвенторе")
                    print("Fight")
                    fight_cooldown = api.fight_monster() #Бой с монстром (7)
                    time.sleep(fight_cooldown)
                    quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

            elif "resource" in component: #Если предмет добывается из ресурса
                x, y = api.find_location(component["resource"]) #Поиск местоположения ресурса (4)
                print(f"Move {x}, {y}")
                move_cooldown = api.move_to(x, y) #Передвижение (5)
                time.sleep(move_cooldown) #Перерыв по кулдауну

                quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

                #Условие для изменения оружия на кирку/топор !!! УЖАСНЫЙ КОСТЫЛЬ! ПОФИКСИТЬ!!!
                if component["subtype"] == "mining" and character == "Jan2":
                    print("Unequip weapon")
                    unequip_cooldown = api.unequip_item("weapon")
                    time.sleep(unequip_cooldown)

                    print("Equip iron pickaxe")
                    equip_cooldown = api.equip_item("iron_pickaxe", "weapon")
                    time.sleep(equip_cooldown)

                elif component["subtype"] == "woodcutting" and character == "Jan2":
                    print("Unequip weapon")
                    unequip_cooldown = api.unequip_item("weapon")
                    time.sleep(unequip_cooldown)

                    print("Equip iron pickaxe")
                    equip_cooldown = api.equip_item("iron_axe", "weapon")
                    time.sleep(equip_cooldown)

                while quantity_in_inventory <  component['quantity']: #Добывать пока в инвентаре не будет нужного кол-ва пердмета
                    print(f"{quantity_in_inventory} {component['code']} в инвенторе")
                    print("Gather")
                    gather_cooldown = api.gather_resource() #Добыча предмета (8)
                    time.sleep(gather_cooldown)
                    quantity_in_inventory = api.get_quantity_item_inventory(component['code']) #Подсчёт кол-ва нужных предметов в инвентаре (6)

        for craft_item in reversed(api.craft_road): #Проход по всем этапам рецепта крафта
            x, y = api.find_location(craft_item["skill"]) #Поиск местоположения нужного воркшопа (9)
            print(f"Move {x},{y}")
            move_cooldown = api.move_to(x, y) #Передвижение (5)
            time.sleep(move_cooldown)

            print(f"Craft {craft_item['code']}")
            craft_cooldown = api.craft(craft_item["code"], craft_item["quantity"]) #Крафт нужного предмета в нужном кол-ве (10)
            time.sleep(craft_cooldown)

        #Четвёртый этап: продажа предметов
        x, y = api.find_location("grand_exchange") #Поиск местоположения магазина (4)
        print(f"Move to Grand Exchange")
        move_cooldown = api.move_to(x, y) #Передвижение (5)
        time.sleep(move_cooldown)

        sell_info = api.get_item_info(item)["ge"] # Инфа о предмете для продажи (11.3)
        sell_cooldown = api.sell_item(sell_info["code"], quantity, sell_info["sell_price"]) # Продажа предмета (12)
        print("Был продан", sell_info["code"], "за", sell_info["sell_price"])
        time.sleep(sell_cooldown)

        api.components = []
        api.craft_road = []

character = input("Выбери персонажа (Blue_Rose): ")
skill_for_up = ""
#Запуск
while True:
    main(character)
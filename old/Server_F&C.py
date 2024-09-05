import requests
import time
from typing import List, Dict, Tuple

#Основной класс со всеми функциями
class MMOAPI:
    def __init__(self, server: str, token: str, character: str):
        self.server = server
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        self.character = character
        self.urls = {
            "gathering": f"{self.server}/my/{self.character}/action/gathering",
            "move": f"{self.server}/my/{self.character}/action/move",
            "craft": f"{self.server}/my/{self.character}/action/crafting",
            "character": f"{self.server}/characters/{self.character}",
            "fight": f"{self.server}/my/{self.character}/action/fight",
            "maps": f"{self.server}/maps/",
            "monsters": f"{self.server}/monsters/",
            "items": f"{self.server}/items/",
            "resources": f"{self.server}/resources/",
            "unequip": f"{self.server}/my/{self.character}/action/unequip",
            "equip": f"{self.server}/my/{self.character}/action/equip",
            "sell":f"{self.server}/my/{self.character}/action/ge/sell"
        }
        self.components = []
        self.craft_road = []

    def request(self, url: str, method: str = 'GET', params: Dict = None, json: Dict = None): #-(0)
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=json)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 490:
                print("Character already at destination.")
                return 0
            print(f"HTTP error occurred: {http_err}")
            print(response.json())  # Detailed server response
            exit()

        except Exception as err:
            print(f"An error occurred: {err}")
            exit()

    def get_character_skills(self) -> Dict[str, int]: #-(1)
        data = self.request(self.urls['character'])["data"] #(0)
        skill_mapping = {
            "weaponcrafting": "weaponcrafting_level",
            "gearcrafting": "gearcrafting_level",
            "jewelrycrafting": "jewelrycrafting_level",
            "cooking": "cooking_level",
            "woodcutting": "woodcutting_level",
            "mining": "mining_level"
        }
        skills = {skill: data.get(level_key, 0) for skill, level_key in skill_mapping.items()}
        return skills

    def get_items_by_skill_level(self, skill: str, level: int) -> List[str]: #-(2)
        params = {
            "max_level": level,
            "craft_skill": skill
        }
        items = self.request(self.urls['items'], params=params)["data"] #(0)
        return [item["code"] for item in items]

    def get_resource_by_item(self, item_name: str) -> str: #-(3.1)
        params = {"drop": item_name}
        resources = self.request(self.urls['resources'], params=params)["data"] #(0)
        return resources[0]["code"] if resources else None

    def get_monster_by_item(self, item_name: str) -> str: #-(3.2)
        params = {"drop": item_name}
        monsters = self.request(self.urls['monsters'], params=params)["data"] #(0)
        return monsters[0]["code"] if monsters else None

    def craft_item(self, item: str, quantity: int): #-(3)
        item_data = self.request(f"{self.urls['items']}{item}")["data"]["item"] #(0)

        if item_data["subtype"] == "task": #Если предмет достаётся из таски, то просто вывод сколько нужно и каких предметов и сразу же возврат
            print(f"Нужен предмет из заданий: {item} x {quantity}")
            return

        if item_data["craft"] is None: #Если у предмета не крафтящийся
            if item_data["subtype"] in ["mob", "food"]: #Если предмет достаётся из моба
                mob = self.get_monster_by_item(item) #Запись в переменную имя монстра из которого дропается предмет (3.2)
                self.components.append({"code": item, "quantity": quantity, "mob": mob, "subtype": item_data["subtype"]}) #Запись в список элемента содержащего всю нужную инфу по предмету
            else: #Если предмет надо добывать где-то
                resource = self.get_resource_by_item(item) #Запись в переменную название ресурса из которого добывается нужный предмет (3.1)
                self.components.append({"code": item, "quantity": quantity, "resource": resource, "subtype": item_data["subtype"]}) #Запись в список элемента содержащего всю нужную инфу по предмету
        else: #Если у предмета не крафтящийся
            self.craft_road.append({"code": item, "skill": item_data["craft"]["skill"], "quantity": quantity}) #Запись пути крафта (какой предмет, какой скилл крафта для него и кол-во)
            for component in item_data["craft"]["items"]: #Цикл для каждого предмета из крафта
                self.craft_item(component["code"], component["quantity"] * quantity) #Повтор функции для каждого предмета из крафта с указанием кол-ва (3)

    def find_location(self, name: str) -> Tuple[int, int]: #-(4)
        params = {"content_code": name}
        location = self.request(self.urls['maps'], params=params)["data"] #(0)
        return location[0]["x"], location[0]["y"]

    def move_to(self, x: int, y: int) -> int: #-(5)
        payload = {"x": x, "y": y}
        response = self.request(self.urls['move'], method='POST', json=payload) #(0)
        if response == 0: #Условие при котором возвращается 0 секунд если код ответа 490-уже на нужном месте
            return 0
        return response["data"]["cooldown"]["total_seconds"]

    def get_quantity_item_inventory(self, item: str) -> int: #-(6)
        inventory = self.request(self.urls['character'])["data"]["inventory"] #(0)

        quantity = 0
        for slot in inventory:
            if slot["code"] == item:
                quantity = slot["quantity"]
        return quantity

    def fight_monster(self) -> int: #-(7)
        response = self.request(self.urls['fight'], method='POST') #(0)
        fight_data = response["data"]["fight"]
        if fight_data["result"] == "lose": #Условие для проигрыша
            print("Вы проиграли бой!")
            exit()
        print(f"Победа! Опыт: {fight_data['xp']}, Золото: {fight_data['gold']}") #Вывод победного сообщения и кол-ва xp и золота
        for drop in fight_data["drops"]: #Проход по всем предметам дропа
            print(f"Добыча: {drop['quantity']} x {drop['code']}")  #Вывод дропа
        return response["data"]["cooldown"]["total_seconds"]

    def gather_resource(self) -> int: #-(8)
        response = self.request(self.urls['gathering'], method='POST')
        return response["data"]["cooldown"]["total_seconds"]

    def find_workshop_location(self, workshop_name: str) -> Tuple[int, int]: #-(9)
        params = {"content_type": "workshop", "content_code": workshop_name} 
        location = self.request(self.urls['maps'], params=params)["data"] #(0)
        return location[0]["x"], location[0]["y"]

    def craft(self, name: str, quantity: int) -> int: #-(10)
        payload = {"code": name, "quantity": quantity}
        craft = self.request(self.urls['craft'], method='POST', json=payload)["data"]["cooldown"]["total_seconds"] #(0)
        return craft

    def unequip_item(self, slot: str) -> int: #-(11.1)
        payload = {"slot": slot}
        return self.request(self.urls['unequip'], method='POST', json=payload)["data"]["cooldown"]["total_seconds"] #(0)

    def equip_item(self, item: str, slot: str) -> int: #-(11.2)
        payload = {"code": item, "slot": slot}
        return self.request(self.urls['equip'], method='POST', json=payload)["data"]["cooldown"]["total_seconds"] #(0)

    def get_item_info(self, item: str) -> Dict: #-(11.3)
        return self.request(f"{self.urls['items']}{item}")["data"] #(0)

    def optimize_weapon_for_monster(self, monster_name: str): #-(11)
        character_data = self.request(self.urls['character'])["data"] #(0)
        monster_data = self.request(f"{self.urls['monsters']}{monster_name}")["data"] #(0)

        P_attacks_type = {k: v for k, v in character_data.items() if "attack_" in k}
        M_res_type = {k: v for k, v in monster_data.items() if "res_" in k}

        P_max_attack = max(P_attacks_type, key=P_attacks_type.get)
        M_min_res = min(M_res_type, key=M_res_type.get)

        if (P_max_attack.split("_")[1] != M_min_res.split("_")[1]) or (self.request(self.urls['character'])["data"]["weapon_slot"] in ["iron_pickaxe", "iron_axe"]):
            print("Unequip")
            unequip_cooldown = self.unequip_item("weapon")
            time.sleep(unequip_cooldown)

            for item in character_data["inventory"]:
                if (len(item["code"])<1) or ("axe" in item["code"]):
                    continue
                item_info = self.get_item_info(item["code"])["item"] #(11.3)
                if item_info["type"] == "weapon":
                    for effect in item_info["effects"]:
                        if effect["name"].split("_")[1] == M_min_res.split("_")[1]:
                            print("Equip",item["code"])
                            equip_cooldown = self.equip_item(item["code"], "weapon")
                            time.sleep(equip_cooldown)
                            break

    def sell_item(self, item_name: str, quantity: int, price: int) -> int: #-(12)
        payload = {"code": item_name, "quantity": quantity, "price": price}
        sell = self.request(self.urls['sell'], method='POST', json=payload)["data"]["cooldown"]["total_seconds"] #(0)
        return sell


#Основная функция в которой поэтапно выполняются все действия и т.д.
def main(character):
    
    #Основные неизменные переменные (сервер, токен и выбор имени персонажа)
    server = "https://api.artifactsmmo.com"
    token = input("Введи токен с сайта: ")
    

    api = MMOAPI(server, token, character) #Вызов класса, передача в него переменных

    # Первый этап: получение и отображение уровней скилов
    levels = api.get_character_skills() #запись в словарь навыки и их уровень. Вызов функции из класса (1)
    for skill, level in levels.items(): #Цикл по каждому навыку
        items = api.get_items_by_skill_level(skill, level) #Запись в список всех возможных предметов для крафта (2)
        print(f"{skill.capitalize()} (уровень {level}):") #Вывод названия и уровня навыка
        for item in items: #Цикл для вывода предметов для крафта для навыка
            if item in ("wooden_staff"): #Здесь можно убирать предметы которые стоит пропускать
                continue
            print(f"Начинается процесс для {item}") 
            print()  # Пустая строка между разделами для читаемости

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

            #Обнуление списков
            api.components = []
            api.craft_road = []

character = input("Выбери персонажа (Jan3, Lil_Z, Aryan): ")
#Запуск
while True:
    main(character)
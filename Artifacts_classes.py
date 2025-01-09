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
            "sell":f"{self.server}/my/{self.character}/action/ge/sell",
            "bank_items":f"{self.server}/my/bank/items"
            #"bank_withdraw"
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
        levels = {skill: data.get(level_key, 0) for skill, level_key in skill_mapping.items()}
        return levels

    def get_items_by_skill_level(self, skill: str, level: int) -> List[str]: #-(2)
        params = {
            "max_level": level,
            "craft_skill": skill
        }
        items_from_skill = self.request(self.urls['items'], params=params)["data"] #(0)
        items = [item["code"] for item in items_from_skill]
        return items

    def get_resource_by_item(self, item_name: str) -> str: #-(3.1)
        params = {"drop": item_name}
        resources = self.request(self.urls['resources'], params=params)["data"] #(0)
        return resources[0]["code"] if resources else None

    def get_monster_by_item(self, item_name: str) -> str: #-(3.2)
        params = {"drop": item_name}
        monsters = self.request(self.urls['monsters'], params=params)["data"] #(0)
        return monsters[0]["code"] if monsters else None

    def craft_item(self, item: str, quantity: int): #-(3)
        item_data = self.request(f"{self.urls['items']}{item}")["data"] #(0)

        if item_data["subtype"] == "task": #Если предмет достаётся из таски, то просто вывод сколько нужно и каких предметов и сразу же возврат
            print(f"Нужен предмет из заданий: {item} x {quantity}")
            return

        if item_data["craft"] is None: #Если предмет не надо крафтить
            if item_data["subtype"] in ["mob", "food"]: #Если предмет достаётся из моба
                mob = self.get_monster_by_item(item) #Запись в переменную имя монстра из которого дропается предмет (3.2)
                self.components.append({"code": item, "quantity": quantity, "mob": mob, "subtype": item_data["subtype"]}) #Запись в список элемента содержащего всю нужную инфу по предмету
            else: #Если предмет надо добывать где-то
                resource = self.get_resource_by_item(item) #Запись в переменную название ресурса из которого добывается нужный предмет (3.1)
                self.components.append({"code": item, "quantity": quantity, "resource": resource, "subtype": item_data["subtype"]}) #Запись в список элемента содержащего всю нужную инфу по предмету
        else: #Если предмет надо крафтить
            self.craft_road.append({"code": item, "skill": item_data["craft"]["skill"], "quantity": quantity}) #Запись пути крафта (какой предмет, какой скилл крафта для него и кол-во)
            for component in item_data["craft"]["items"]: #Цикл для каждого предмета из крафта
                self.craft_item(component["code"], component["quantity"] * quantity) #Повтор функции для каждого предмета из крафта с указанием кол-ва (3)

    def check_bank(self, item: str):
        params = {"item_code": item}
        bank_item_data = self.request(self.urls['bank_items'], params=params)["data"] #(0)
        if len(bank_item_data) != 0:
            print(f"В банке есть {item}")
            return bank_item_data
        

    #def withdraw_bank():

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

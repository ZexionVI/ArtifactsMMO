import time
from Artifacts_classes import MMOAPI
from Artifacts_standart import item_list_skill, craftnroad, mobfarm, resourcefarm, finish_craft

#Основные неизменные переменные (сервер, токен и выбор имени персонажа)
server = "https://api.artifactsmmo.com"

def s_skill (character, token, optimize_weapone):

    api = MMOAPI(server, token, character) #Вызов класса, передача в него переменных

    need_info = item_list_skill(api)

    quantity = 5 if need_info['skill'] == "cooking" else 1

    for item in need_info['items']:
        craftnroad(api, item, quantity)
        for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
            if component["subtype"] in ["mob", "food"]: #Если предмет выбивается из моба
                mobfarm(api, component, optimize_weapone)
            elif "resource" in component: #Если предмет добывается из ресурса
                resourcefarm(api, component)
        for craft_item in reversed(api.craft_road): #Проход по всем этапам рецепта крафта
            finish_craft(api, craft_item)



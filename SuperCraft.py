import time
from Artifacts_classes import MMOAPI
from Artifacts_standart import item_list_craft, craftnroad, mobfarm, resourcefarm, finish_craft

#Основные неизменные переменные (сервер, токен и выбор имени персонажа)
server = "https://api.artifactsmmo.com"

def s_craft (character, token, optimize_weapone):

    api = MMOAPI(server, token, character) #Вызов класса, передача в него переменных

    item_list_craft(api)

    item = input("Выберите предмет для крафта: ") #Выбор предмета крафта
    quantity = int(input("Сколько единиц создать? ")) #Ввод необходимого кол-ва предметов

    craftnroad(api, item, quantity)

    # Третий этап: выполнение действий
    for component in api.components: #Цикл для каждого элемента в списке с компонентами которые нужны для крафта
        if component["subtype"] in ["mob", "food"]: #Если предмет выбивается из моба
            mobfarm(api, component, optimize_weapone)

        elif "resource" in component: #Если предмет добывается из ресурса
            resourcefarm(api, component)

    for craft_item in reversed(api.craft_road): #Проход по всем этапам рецепта крафта
        finish_craft(api, craft_item)



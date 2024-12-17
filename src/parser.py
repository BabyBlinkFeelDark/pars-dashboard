from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import re
from src.db import save_courier_data

def extract_order_data(order):
    """
    Извлекает данные о заказе (статус, имя курьера, время) из элемента веб-страницы и сохраняет эти данные в базу.

    Функция находит элемент с заказом, извлекает статус, имя курьера и время, если оно указано.
    Если время требует выхода ("Пора выходить"), то извлекается значение времени.
    Все данные сохраняются в базу данных через функцию `save_courier_data`.

    Args:
        order (selenium.webdriver.remote.webelement.WebElement): Элемент на веб-странице, представляющий заказ, из которого нужно извлечь данные.

    Returns:
        None: Функция не возвращает значение, но сохраняет информацию о заказе в базе данных.

    Exceptions:
        StaleElementReferenceException: Если элемент устарел (например, страница перезагрузилась), будет возвращено `None`.
        NoSuchElementException: Если не удается найти нужный элемент, возвращается `None`.
        Exception: При любых других ошибках возвращается `None`.

    Prints:
        str: Информация о заказе (имя курьера и время) выводится в консоль.

    """
    try:
        # Проверка наличия элемента с нужным классом (для статуса)
        status_element = order.find_element(By.CLASS_NAME, "sc-bCnriq")
        status = status_element.text

        # Извлекаем имя
        name_element = order.find_element(By.CLASS_NAME, "sc-bCnriq")
        name = name_element.text.split('\n')[1]  # Имя обычно идет после времени

        time_taken = None
        if "Пора выходить" in status:
            # Ищем время в строке после слов "Пора выходить"
            time_match = re.search(r"Пора выходить (\d+) мин", status)
            if time_match:
                time_taken = int(time_match.group(1))  # Извлекаем и конвертируем в целое число


        if name:
            save_courier_data(name, time_taken)

        # Печатаем данные
        print(f"Имя: {name}")
        print(f"Статус: {time_taken}")
        print("_"*40)


    except StaleElementReferenceException:
        return None  # Элемент устарел, необходимо повторно его найти

    except NoSuchElementException:
        return None  # Элемент не найден

    except Exception as e:
        return None  # При любой ошибке возвращаем None

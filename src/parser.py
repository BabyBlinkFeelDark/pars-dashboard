from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import re
from src.db import save_courier_data

def extract_order_data(order):

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

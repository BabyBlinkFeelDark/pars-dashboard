import logging
import time
from dotenv import load_dotenv
import requests
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from src.login import login
from src.utils import wait_for_elements
from src.parser import extract_order_data
from src.cleaner import run_scheduler


logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования: DEBUG (можно изменить на INFO или ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.StreamHandler(),  # Выводить в консоль
        logging.FileHandler("app.log")  # Логирование в файл
    ]
)


load_dotenv()


# Функция получения заголовков и куков
def get_headers_and_cookies(driver):
    """
    Извлекает куки и заголовки для авторизации в API из браузера.

    Args:
        driver (selenium.webdriver.Chrome): Объект WebDriver для работы с браузером.

    Returns:
        tuple: Заголовки (headers) и куки (cookie_dict) для использования в запросах API.

    Raises:
        Exception: Если отсутствует cookie авторизации (auth_token или spid), выбрасывается исключение.
    """
    cookies = driver.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    authorization_cookie = cookie_dict.get("auth_token") or cookie_dict.get("spid")
    if not authorization_cookie:
        raise Exception("Authorization cookie is missing! Please check the login process.")

    headers = {
        "Authorization": f"Bearer {authorization_cookie}",
        "Accept": "application/json",
        "Origin": os.getenv("ORIGIN_URL"),
        "Referer": os.getenv("DASHBOARD_URL"),
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
    }

    return headers, cookie_dict


# Функция запроса к API
def fetch_warehouse_summary(headers, cookies):
    """
    Отправляет GET-запрос к API для получения сводной информации о складе.

    Args:
        headers (dict): Заголовки для авторизации в запросе.
        cookies (dict): Куки для авторизации в запросе.

    Returns:
        int: Код состояния HTTP-ответа (например, 200 для успешного запроса).

    Prints:
        str: Ответ от API в случае успешного запроса.
    """
    url = os.getenv("COOKER")
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        print("Успешный запрос:", response.json())
    return response.status_code


# Основной процесс
def create_driver():
    """
    Создаёт и конфигурирует объект WebDriver для работы с браузером.

    Returns:
        selenium.webdriver.Chrome: Объект WebDriver для браузера Chrome.
    """
    chrome_options = Options()
    # Настройка пользовательского агента и отключение автоматизации
    # chrome_options.add_argument("--headless")  # Безголовый режим
    chrome_options.add_argument("--disable-gpu")  # Отключаем GPU
    chrome_options.add_argument(os.getenv("USER_AGENT"))
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Отключаем индикатор автоматизации

    driver = webdriver.Chrome(options=chrome_options)
    return driver


driver = create_driver()

# Шаг 1: Авторизация
driver.get(os.getenv("DASHBOARD_URL"))
login(driver, os.getenv("DASHBOARD_USER"), os.getenv("DASHBOARD_PASSWORD"))
time.sleep(5)


# Сохранение куков в файл
def save_cookies(driver, filename="cookies.pkl"):
    """
    Сохраняет куки, полученные из браузера, в файл для последующего использования.

    Args:
        driver (selenium.webdriver.Chrome): Объект WebDriver.
        filename (str, optional): Имя файла для сохранения куков. По умолчанию "cookies.pkl".
    """
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


# Загрузка куков из файла
def load_cookies(driver, filename="cookies.pkl"):
    """
    Загружает куки из файла и добавляет их в браузер.

    Args:
        driver (selenium.webdriver.Chrome): Объект WebDriver.
        filename (str, optional): Имя файла для загрузки куков. По умолчанию "cookies.pkl".

    Prints:
        str: Сообщения об ошибках при загрузке куков.
    """
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
        except EOFError:
            print("Файл куков повреждён или пуст.")
        except Exception as e:
            print(f"Ошибка при загрузке куков: {e}")
    else:
        print("Файл куков не найден, потребуется заново войти в систему.")


# Попытка загрузки куков, если они существуют
load_cookies(driver)

# Установка начальных куков и заголовков
headers, cookies = get_headers_and_cookies(driver)
last_cookie_update = time.time()

# Цикл работы
try:
    while True:
        # Проверяем, нужно ли обновить куки
        if time.time() - last_cookie_update >= 60:
            print("Обновляем куки...")
            headers, cookies = get_headers_and_cookies(driver)
            last_cookie_update = time.time()

        # Пытаемся получить данные
        status_code = fetch_warehouse_summary(headers, cookies)

        # Ожидание появления новых заказов на веб-странице
        orders = wait_for_elements(driver, By.CLASS_NAME, "sc-hHvkSs")

        # Для каждого нового заказа извлекаем данные
        for order in orders:
            extract_order_data(order)

        # Ожидание перед следующим запросом
        time.sleep(15)
        run_scheduler()

except KeyboardInterrupt:
    print("Скрипт остановлен.")
finally:
    # Сохраняем куки перед завершением работы
    save_cookies(driver)

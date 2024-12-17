import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver, username, password):
    """
    Осуществляет авторизацию на веб-странице, заполняя поля для ввода логина и пароля,
    и нажимает кнопку логина.

    Args:
        driver (selenium.webdriver.Chrome): Объект WebDriver для взаимодействия с браузером.
        username (str): Имя пользователя для входа.
        password (str): Пароль для входа.

    Waits:
        WebDriverWait: Ожидание появления полей ввода логина и пароля, а также кнопки для отправки формы.
        time.sleep: Пауза после выполнения логина для ожидания появления токена в куках.

    Prints:
        str: Сообщение о успешной авторизации.
    """
    wait = WebDriverWait(driver, 10)

    # Ожидание полей для логина
    login_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    # Заполнение полей
    driver.execute_script("arguments[0].value = arguments[1];", login_field, username)
    driver.execute_script("arguments[0].value = arguments[1];", password_field, password)

    # Ожидание и клик по кнопке логина
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @data-testid='login-button']")))
    login_button.click()

    # Ждем, пока токен не появится в куках
    time.sleep(2)
    print("Авторизация выполнена.")

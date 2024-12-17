from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, by, value, timeout=10):
    """Функция для явного ожидания элемента"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))

def wait_for_elements(driver, by, value, timeout=10):
    """Функция для явного ожидания элементов"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_all_elements_located((by, value)))
# Проект по автоматизации обработки данных и интеграции с API

## Описание

Этот проект представляет собой систему для автоматизации сбора и обработки данных, а также интеграции с внешними API. Основная цель - построить инфраструктуру для работы с базой данных, сбором данных через API, а также обеспечить автоматизацию процессов с использованием Python, Selenium и PostgreSQL. Проект включает разработку скриптов для взаимодействия с веб-сервисами.

## Основные технологии

- **Python**: для написания логики обработки данных, взаимодействия с API и базы данных.
- **Selenium**: для автоматизации браузерных действий и работы с веб-страницами.
- **PostgreSQL**: для хранения данных, управления транзакциями и выполнения сложных SQL-запросов.
- **Requests**: для взаимодействия с REST API.

## Установка и запуск

### 1. Клонирование репозитория

Склонируйте репозиторий:

```bash
git clone https://github.com/BabyBlinkFeelDark/pars-dashboard.git
cd pars-dashboard
```

### 2. Установка зависимостей

Убедитесь, что у вас установлен **Python** и **Poetry**. Затем установите все зависимости:

```bash
poetry install
```

Для запуска проекта без Poetry, можно установить зависимости через `pip`:

```bash
pip install -r requirements.txt
```

### 3. Настройка PostgreSQL

Для работы с базой данных PostgreSQL, убедитесь, что база данных настроена правильно. В файле конфигурации укажите данные для подключения:

```bash
# Пример подключения в коде
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "your_database"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
```

### 5. Запуск приложения

Запустите скрипт для выполнения основной логики обработки данных:

```bash
poetry run python main.py
```

Или если не используете Poetry:

```bash
python3 main.py
```

## Функционал

- **Автоматизация сбора и обработки данных с онлайн-платформ**: разработан модуль для взаимодействия с веб-сервисами и API, включая сбор информации о заказах.
- **Интеграция с базой данных PostgreSQL**: проект включает настройку и оптимизацию базы данных для учета заказов и курьеров.
- **Автоматизация обновления куков для API-запросов с использованием Selenium**: настройка автоматического обновления сессий и куков для работы с API.


## Структура проекта

- `main.py`: Основной скрипт, запускающий логику обработки данных и работы с API.
- `pyproject.toml`: Список зависимостей для установки через `poetry`.
- `scr/`: Дополнительные скрипты для обработки данных или автоматизации задач.

## Примечания

- Обратите внимание, что для корректной работы с Selenium необходимо использовать совместимую версию `chromedriver` и установить его на сервере.
- Если при работе с PostgreSQL возникают проблемы с подключением, проверьте настройки конфигурации базы данных и порты.

## Лицензия

Этот проект лицензирован на условиях [MIT](https://opensource.org/licenses/MIT).

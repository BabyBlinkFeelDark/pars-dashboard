import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Установите временную зону
local_tz = pytz.timezone('Europe/Moscow')  # Укажите ваш часовой пояс
load_dotenv()

# Получение текущего времени в вашем часовом поясе
def get_local_time():
    """
    Возвращает текущее время в часовом поясе 'Europe/Moscow'.

    Returns:
        datetime: Текущее время в указанном часовом поясе.
    """
    return datetime.now(local_tz)


# Подключение к базе данных PostgreSQL
def get_connection():
    """
    Устанавливает соединение с базой данных PostgreSQL с использованием
    параметров, загруженных из .env файла.

    Returns:
        psycopg2.connection: Объект подключения к базе данных.
    Raises:
        Exception: Если не удается подключиться к базе данных, возбуждается исключение.
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DBNAME"),  # Убедитесь, что имя базы данных правильное
            user=os.getenv("USER_NAME"),  # Имя пользователя, которое вы создали
            password=os.getenv("PASSWORD"),  # Замените на ваш реальный пароль
            host=os.getenv("HOST"),  # Локально
            port=os.getenv("PORT")
        )
        print("Подключение к базе данных успешно!")  # Сообщение о успешном подключении
        return conn
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        raise  # Повторно выбрасываем исключение, если подключение не удалось

# Создание таблиц с добавлением столбца deliveries
def init_db():
    """
    Инициализирует базу данных, создавая таблицы для курьеров и заказов,
    если они еще не существуют.

    Creates:
        - couriers: Таблица курьеров с полями courier_id, courier_name и last_update.
        - orders: Таблица заказов с полями order_id, courier_id, time_taken, cur_time.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS couriers (
                courier_id SERIAL PRIMARY KEY,
                courier_name TEXT UNIQUE NOT NULL,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    courier_id INTEGER REFERENCES couriers(courier_id) ON DELETE CASCADE,
                    time_taken FLOAT,
                    cur_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
                );
            """)
            conn.commit()

# Сохранение или обновление данных курьера и заказа
def save_courier_data(courier_name, time_taken):
    """
    Сохраняет или обновляет данные курьера и его последнего заказа в базе данных.
    Если курьер уже существует, обновляется информация о последнем заказе.
    Если курьер не существует, создается новая запись.

    Args:
        courier_name (str): Имя курьера.
        time_taken (float): Время, затраченное на заказ.

    Prints:
        str: Сообщения о выполненных действиях (добавление нового заказа, обновление и т. д.).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Находим ID курьера или создаем новую запись
            cur.execute("SELECT courier_id FROM couriers WHERE courier_name = %s", (courier_name,))
            courier = cur.fetchone()

            if not courier:
                cur.execute("""
                    INSERT INTO couriers (courier_name)
                    VALUES (%s)
                    RETURNING courier_id
                """, (courier_name,))
                courier_id = cur.fetchone()[0]
            else:
                courier_id = courier[0]

            # Получаем последний заказ курьера с его time_taken
            cur.execute("""
                SELECT order_id, time_taken 
                FROM orders 
                WHERE courier_id = %s 
                ORDER BY cur_time DESC LIMIT 1
            """, (courier_id,))
            last_order = cur.fetchone()

            # Логируем, что происходит с последним заказом
            if last_order:
                print(f"У курьера {courier_name} последний заказ с time_taken {last_order[1]}.")

                # Если time_taken нового заказа меньше предыдущего, то это новый заказ
                if time_taken is not None and time_taken < last_order[1]:
                    print(f"Для курьера {courier_name} добавлен новый заказ с time_taken {time_taken}.")
                    # Добавляем новый заказ
                    cur.execute("""
                        INSERT INTO orders (courier_id, time_taken, cur_time)
                        VALUES (%s, %s, %s)
                    """, (courier_id, time_taken, get_local_time()))
                    print("Новый заказ добавлен в базу данных.")
                else:
                    print(f"У курьера {courier_name} нет нового заказа. Текущее время: {time_taken}, последнее время: {last_order[1]}.")
                    # Если time_taken больше или равно предыдущему, обновляем время
                    if time_taken is not None:
                        print(
                            f"У курьера {courier_name} нет нового заказа. Обновляем время с {last_order[1]} на {time_taken}.")
                        cur.execute("""
                                                UPDATE orders
                                                SET time_taken = %s, cur_time = %s
                                                WHERE order_id = %s
                                            """, (time_taken, get_local_time(), last_order[0]))
                        print(f"Время для последнего заказа курьера {courier_name} обновлено.")
            else:
                # Если заказов еще нет, добавляем первый
                print(f"У курьера {courier_name} еще нет заказов. Добавляем первый заказ с time_taken 0.")
                cur.execute("""
                    INSERT INTO orders (courier_id, time_taken, cur_time)
                    VALUES (%s, %s, %s)
                """, (courier_id, 0, get_local_time()))
                print("Первый заказ добавлен в базу данных.")

            # Завершаем транзакцию
            conn.commit()
            print("Транзакция завершена, данные сохранены.")

# Получение данных курьера
def get_courier_data(courier_name):
    """
    Получает данные курьера по имени.

    Args:
        courier_name (str): Имя курьера.

    Returns:
        dict: Данные курьера в виде словаря, если курьер найден, иначе None.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM couriers WHERE courier_name = %s", (courier_name,))
            return cur.fetchone()

# Получение всех курьеров
def get_all_couriers():
    """
    Получает список всех курьеров из базы данных.

    Returns:
        list: Список словарей с данными всех курьеров.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM couriers")
            return cur.fetchall()

# Получение всех заказов
def get_all_orders():
    """
    Получает список всех заказов из базы данных.

    Returns:
        list: Список словарей с данными всех заказов.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orders")
            return cur.fetchall()

def clear_tables():
    """
    Очищает таблицы 'couriers' и 'orders', удаляя все данные и сбрасывая идентификаторы.
    Это действие сбрасывает состояние таблиц на чистое.

    Prints:
        str: Сообщение об очистке таблиц.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE orders, couriers RESTART IDENTITY CASCADE;")  # Очистить таблицу orders
            conn.commit()
            print(f"Таблицы 'couriers' и 'orders' очищены в {get_local_time()}")

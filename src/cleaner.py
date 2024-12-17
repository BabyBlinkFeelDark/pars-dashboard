from src.db import clear_tables, get_local_time, get_all_couriers

def is_within_time_range(start_hour, start_minute, end_hour, end_minute):
    """
    Проверяет, находится ли текущее время в заданном диапазоне.

    Функция сравнивает текущее время с заданным диапазоном времени (начало и конец)
    и возвращает `True`, если текущее время находится внутри диапазона, и `False`, если нет.

    Args:
        start_hour (int): Час начала диапазона времени.
        start_minute (int): Минута начала диапазона времени.
        end_hour (int): Час конца диапазона времени.
        end_minute (int): Минута конца диапазона времени.

    Returns:
        bool: `True`, если текущее время внутри указанного диапазона, `False` — если за пределами.

    """
    now = get_local_time()
    start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    return start_time <= now <= end_time


def scheduled_clear_tables():
    """
    Проверяет, нужно ли очищать таблицы на основе времени и наличия данных.

    Функция проверяет, находится ли текущее время в диапазоне с 3:30 до 6:00 утра и
    если таблица курьеров не пуста, то запускает очистку данных из таблиц с помощью функции `clear_tables`.

    Если текущее время не попадает в заданный диапазон или таблицы пусты, очистка не выполняется.

    Prints:
        str: Информация о начале или пропуске очистки выводится в консоль.

    Returns:
        None
    """
    if is_within_time_range(3, 30, 6, 0) and get_all_couriers() != []:
        print(f"Очистка начата в {get_local_time()}...")
        clear_tables()
    else:
        print(f"Очистка пропущена в {get_local_time()}: вне диапазона или таблицы пусты.")


def run_scheduler():
    """
    Запускает планировщик для выполнения функции очистки таблиц.

    Функция вызывает `scheduled_clear_tables`, чтобы выполнить проверку и очистку таблиц, если это необходимо.

    Returns:
        None
    """
    scheduled_clear_tables()

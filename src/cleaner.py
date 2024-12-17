from src.db import clear_tables,get_local_time, get_all_couriers


def is_within_time_range(start_hour, start_minute, end_hour, end_minute):
    now = get_local_time()
    start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    return start_time <= now <= end_time


def scheduled_clear_tables():
    if is_within_time_range(3,30,6,0) and get_all_couriers() != []:
        print(f"Очистка начата в {get_local_time()}...")
        clear_tables()
    else:
        print(f"Очистка пропущена в {get_local_time()}: вне диапазона или таблицы пусты.")


def run_scheduler():
        scheduled_clear_tables()
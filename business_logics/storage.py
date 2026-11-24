"""
Модуль in-memory хранилища (эмуляция базы данных).

Данные хранятся в оперативной памяти в виде списков словарей.
При перезапуске сервера все изменения сбрасываются, и данные
инициализируются заново с помощью функции `seed()`.
"""

import itertools

# --- Автоинкрементные счётчики для ID ---
_user_id_counter = itertools.count(1)
_place_id_counter = itertools.count(1)
_booking_id_counter = itertools.count(1)

# --- Таблицы (списки словарей) ---
users = []      # Пользователи: [{"id": int, "name": str, "email": str, "password": str, "role": str}]
places = []     # Рабочие места: [{"id": int, "name": str, "description": str, "price": int}]
bookings = []   # Брони: [{"id": int, "user_id": int, "place_id": int, "date": str, "start": str, "end": str, "status": str}]


def seed():
    """
    Инициализирует хранилище тестовыми данными.

    Создаёт двух пользователей (администратора и обычного пользователя)
    и три демонстрационных рабочих места. Вызывается один раз при импорте модуля.
    """
    users.append({
        "id": next(_user_id_counter),
        "name": "Администратор",
        "email": "admin@coworking.ru",
        "password": "admin123",
        "role": "admin",
    })
    users.append({
        "id": next(_user_id_counter),
        "name": "Иван",
        "email": "ivan@mail.ru",
        "password": "12345",
        "role": "user",
    })

    demo_places = [
        ("Место №1", "У окна, тихое", 500),
        ("Место №2", "В центре зала", 400),
        ("Место №3", "Переговорная", 600),
    ]
    for name, desc, price in demo_places:
        places.append({
            "id": next(_place_id_counter),
            "name": name,
            "description": desc,
            "price": price,
        })

# Автоматическая инициализация при импорте
seed()
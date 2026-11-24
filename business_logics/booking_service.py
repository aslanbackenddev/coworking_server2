"""
Модуль бизнес-логики приложения «Коворкинг».

Содержит функции для работы с пользователями, рабочими местами
и бронированиями. Все операции работают поверх in-memory хранилища
(`storage.py`). Каждая функция возвращает кортеж `(успех, результат)`,
где `успех` — булево значение, а `результат` — данные или текст ошибки.
"""

from datetime import datetime
from . import storage


# ---------- Вспомогательные функции ----------

def _find_user_by_email(email: str):
    """Ищет пользователя по email. Возвращает словарь или None."""
    return next((u for u in storage.users if u["email"] == email), None)


def _find_place(place_id: int):
    """Ищет рабочее место по ID. Возвращает словарь или None."""
    return next((p for p in storage.places if p["id"] == place_id), None)


def _parse_time(hhmm: str) -> datetime.time:
    """Преобразует строку формата 'HH:MM' в объект time."""
    return datetime.strptime(hhmm, "%H:%M").time()


def _overlaps(start1, end1, start2, end2) -> bool:
    """
    Проверяет пересечение двух временных интервалов.

    :return: True, если интервалы пересекаются, иначе False.
    """
    return start1 < end2 and start2 < end1


# ---------- Операции с пользователями ----------

def register_user(name: str, email: str, password: str):
    """
    Регистрирует нового пользователя.

    :param name: Имя пользователя.
    :param email: Электронная почта (должна быть уникальной).
    :param password: Пароль в открытом виде (в учебных целях).
    :return: (True, user_dict) или (False, сообщение_об_ошибке).
    """
    if not name or not email or not password:
        return False, "Все поля обязательны"
    if _find_user_by_email(email):
        return False, "Пользователь с таким email уже существует"

    user = {
        "id": next(storage._user_id_counter),
        "name": name,
        "email": email,
        "password": password,
        "role": "user",
    }
    storage.users.append(user)
    return True, user


def authenticate(email: str, password: str):
    """
    Проверяет учётные данные пользователя.

    :return: (True, user_dict) при успехе, иначе (False, сообщение_об_ошибке).
    """
    user = _find_user_by_email(email)
    if not user or user["password"] != password:
        return False, "Неверный email или пароль"
    return True, user


# ---------- Операции с местами ----------

def list_places():
    """
    Возвращает список всех рабочих мест.

    :return: (True, список мест).
    """
    return True, list(storage.places)


def add_place(name: str, description: str, price: int, requester):
    """
    Добавляет новое рабочее место (только для администратора).

    :param name: Название места.
    :param description: Описание (может быть пустым).
    :param price: Цена за час (целое положительное число).
    :param requester: Словарь с данными текущего пользователя.
    :return: (True, place_dict) или (False, сообщение_об_ошибке).
    """
    if not requester or requester.get("role") != "admin":
        return False, "Недостаточно прав"
    if not name or price is None or int(price) <= 0:
        return False, "Некорректные данные места"

    place = {
        "id": next(storage._place_id_counter),
        "name": name,
        "description": description or "",
        "price": int(price),
    }
    storage.places.append(place)
    return True, place


def delete_place(place_id: int, requester):
    """
    Удаляет рабочее место (только для администратора).

    Запрещено удалять место, если на него есть активные брони.

    :return: (True, {"deleted_id": place_id}) или (False, сообщение_об_ошибке).
    """
    if not requester or requester.get("role") != "admin":
        return False, "Недостаточно прав"

    place = _find_place(place_id)
    if not place:
        return False, "Место не найдено"

    active = [b for b in storage.bookings if b["place_id"] == place_id and b["status"] == "active"]
    if active:
        return False, "Есть активные брони на это место"

    storage.places.remove(place)
    return True, {"deleted_id": place_id}


# ---------- Операции с бронированиями ----------

def create_booking(user_id: int, place_id: int, date: str, start: str, end: str):
    """
    Создаёт новое бронирование.

    Проверяет:
    - Существование места.
    - Корректность даты и времени.
    - Что время окончания позже времени начала.
    - Отсутствие пересечений с другими активными бронями на это же место и дату.

    :return: (True, booking_dict) или (False, сообщение_об_ошибке).
    """
    place = _find_place(place_id)
    if not place:
        return False, "Место не найдено"

    try:
        datetime.strptime(date, "%Y-%m-%d")
        t_start = _parse_time(start)
        t_end = _parse_time(end)
    except (ValueError, TypeError):
        return False, "Некорректный формат даты или времени"

    if t_end <= t_start:
        return False, "Время окончания должно быть позже начала"

    for b in storage.bookings:
        if b["place_id"] != place_id or b["status"] != "active":
            continue
        if b["date"] != date:
            continue
        if _overlaps(t_start, t_end, _parse_time(b["start"]), _parse_time(b["end"])):
            return False, "Это время занято"

    booking = {
        "id": next(storage._booking_id_counter),
        "user_id": user_id,
        "place_id": place_id,
        "date": date,
        "start": start,
        "end": end,
        "status": "active",
    }
    storage.bookings.append(booking)
    return True, booking


def list_user_bookings(user_id: int):
    """
    Возвращает список активных броней пользователя.

    :param user_id: ID пользователя.
    :return: (True, список броней).
    """
    result = [b for b in storage.bookings if b["user_id"] == user_id and b["status"] == "active"]
    return True, result


def list_all_bookings(requester):
    """
    Возвращает список всех броней (только для администратора).

    :return: (True, список броней) или (False, сообщение_об_ошибке).
    """
    if not requester or requester.get("role") != "admin":
        return False, "Недостаточно прав"
    return True, list(storage.bookings)


def cancel_booking(booking_id: int, user_id: int, is_admin: bool = False):
    """
    Отменяет бронирование.

    Пользователь может отменить только свою бронь. Администратор — любую.
    Бронь не удаляется физически, а помечается статусом 'cancelled'.

    :param booking_id: ID брони.
    :param user_id: ID текущего пользователя.
    :param is_admin: Флаг, указывающий, является ли пользователь админом.
    :return: (True, booking_dict) или (False, сообщение_об_ошибке).
    """
    booking = next((b for b in storage.bookings if b["id"] == booking_id and b["status"] == "active"), None)
    if not booking:
        return False, "Бронь не найдена"

    if not is_admin and booking["user_id"] != user_id:
        return False, "Нет прав на отмену этой брони"

    booking["status"] = "cancelled"
    return True, booking
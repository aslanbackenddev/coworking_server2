"""
Контроллер для обработки API-запросов (JSON).
"""

import json
from business_logics import booking_service, session


def _get_current_user(environ):
    """Извлекает текущего пользователя из cookie сессии."""
    cookie = environ.get("HTTP_COOKIE", "")
    sid = None
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("sid="):
            sid = part[4:]
            break
    return session.get_user(sid)


def cancel_booking(environ, start_response):
    """
    Обрабатывает DELETE-запрос на отмену брони.

    :return: Кортеж (тело_ответа, статус, MIME-тип).
    """
    user = _get_current_user(environ)
    if not user:
        return json.dumps({"success": False, "error": "Не авторизован"}), "401 Unauthorized", "application/json"

    path = environ.get("PATH_INFO", "/")
    try:
        booking_id = int(path.rstrip("/").split("/")[-1])
    except ValueError:
        return json.dumps({"success": False, "error": "Некорректный ID"}), "400 Bad Request", "application/json"

    ok, result = booking_service.cancel_booking(
        booking_id, user["id"], is_admin=(user["role"] == "admin")
    )

    if not ok:
        return json.dumps({"success": False, "error": result}), "400 Bad Request", "application/json"

    return json.dumps({"success": True, "booking": result}), "200 OK", "application/json"
"""
Модуль управления пользовательскими сессиями.

Сессии хранятся в оперативной памяти в виде словаря `_sessions`.
Каждой сессии присваивается уникальный идентификатор (UUID),
который передаётся клиенту через cookie.
"""

import uuid
from . import storage

# Хранилище сессий: {session_id (str): user_id (int)}
_sessions = {}


def create_session(user_id: int) -> str:
    """
    Создаёт новую сессию для пользователя.

    :param user_id: ID пользователя, для которого создаётся сессия.
    :return: Уникальный идентификатор сессии (UUID в виде строки).
    """
    sid = str(uuid.uuid4())
    _sessions[sid] = user_id
    return sid


def get_user(sid: str):
    """
    Возвращает пользователя по ID сессии.

    :param sid: Идентификатор сессии (строка).
    :return: Словарь с данными пользователя или None, если сессия не найдена.
    """
    if not sid:
        return None
    uid = _sessions.get(sid)
    if uid is None:
        return None
    return next((u for u in storage.users if u["id"] == uid), None)


def destroy(sid: str):
    """
    Удаляет сессию (выход из системы).

    :param sid: Идентификатор сессии для удаления.
    """
    _sessions.pop(sid, None)
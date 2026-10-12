import os


# ============================================================
# Пути
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


# ============================================================
# MIME-типы
# ============================================================
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".json": "application/json",
    ".txt": "text/plain; charset=utf-8",
}


# ============================================================
# Маршруты: URL → HTML-файл
# ============================================================
ROUTES = {
    "/": "index.html",
    "/login": "login.html",
    "/register": "register.html",
    "/workspaces": "workspaces.html",
    "/bookings": "bookings.html",
    "/bookings/new": "booking_new.html",
}


def read_text_file(path):
    """
    Читает текстовый файл (HTML, CSS) в кодировке UTF-8.

    :param path: Полный путь к файлу
    :return: Содержимое файла как строка
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_binary_file(path):
    """
    Читает бинарный файл (картинки, иконки) и возвращает байты.

    :param path: Полный путь к файлу
    :return: Содержимое файла как bytes
    """
    with open(path, "rb") as f:
        return f.read()


def get_content_type(path):
    """
    Определяет Content-Type по расширению файла.

    Ищет расширение в словаре MIME_TYPES.
    Если расширение не найдено — возвращает
    'application/octet-stream' (стандартный тип для
    произвольных бинарных данных).

    :param path: Путь к файлу (или его имя)
    :return: Строка с MIME-типом
    """
    ext = os.path.splitext(path)[1].lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def make_response(start_response, status, body, content_type="text/html; charset=utf-8"):
    """
    Формирует HTTP-ответ и возвращает его тело.

    Преобразует строку в байты (если нужно), формирует
    заголовки Content-Type и Content-Length, вызывает
    start_response и возвращает список байтов.

    :param start_response: WSGI-функция для передачи статуса и заголовков
    :param status: HTTP-статус (например, "200 OK")
    :param body: Тело ответа — строка или байты
    :param content_type: MIME-тип содержимого
    :return: Список байтов — тело ответа для WSGI
    """
    if isinstance(body, str):
        body = body.encode("utf-8")

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


def application(environ, start_response):
    """
    Главная точка входа WSGI. Обрабатывает все запросы.

    Логика:
    1. Если путь начинается с /static/ — отдать статику.
    2. Если запрошен /favicon.ico — отдать иконку.
    3. Если путь есть в ROUTES — отдать HTML-страницу.
    4. Иначе — вернуть 404.

    :param environ: Словарь с данными HTTP-запроса
    :param start_response: WSGI-функция для передачи статуса и заголовков
    :return: Список байтов — тело ответа
    """
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # 1. Статика: /static/*
    if path.startswith("/static/"):
        return serve_static(path, start_response)

    # 2. Иконка сайта
    if path == "/favicon.ico":
        favicon = os.path.join(STATIC_DIR, "favicon.ico")
        if os.path.exists(favicon):
            return serve_file(favicon, start_response)
        return make_response(start_response, "404 Not Found", "<h1>404</h1>")

    # 3. HTML-страницы
    if method == "GET" and path in ROUTES:
        filename = ROUTES[path]
        filepath = os.path.join(TEMPLATES_DIR, filename)
        if os.path.exists(filepath):
            html = read_text_file(filepath)
            return make_response(start_response, "200 OK", html)

    # 4. Всё остальное — 404
    return make_response(
        start_response,
        "404 Not Found",
        "<h1>404 — Страница не найдена</h1>",
    )


def serve_static(path, start_response):
    """
    Отдаёт файлы из папки static (картинки, CSS, JS).

    Принимает путь вида /static/logo.png, определяет
    относительный путь внутри static/ и отдаёт файл.

    :param path: Путь запроса (например, /static/style.css)
    :param start_response: WSGI-функция для передачи статуса и заголовков
    :return: Список байтов — тело ответа
    """
    relative = path[len("/static/"):]
    filepath = os.path.join(STATIC_DIR, relative)

    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return make_response(start_response, "404 Not Found", "<h1>404</h1>")

    return serve_file(filepath, start_response)


def serve_file(filepath, start_response):
    """
    Отдаёт один файл с правильным Content-Type.

    Для текстовых файлов (text/*, application/json) читает
    как текст в UTF-8. Для остальных (картинки) — как байты.

    :param filepath: Полный путь к файлу
    :param start_response: WSGI-функция для передачи статуса и заголовков
    :return: Список байтов — тело ответа
    """
    content_type = get_content_type(filepath)

    if content_type.startswith("text/") or content_type.startswith("application/json"):
        body = read_text_file(filepath).encode("utf-8")
    else:
        body = read_binary_file(filepath)

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
    ]
    start_response("200 OK", headers)
    return [body]
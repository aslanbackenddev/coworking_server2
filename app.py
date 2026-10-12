import os
import json

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

# ============================================================
# Вспомогательные функции
# ============================================================

def read_text_file(path):
    """
    Читает текстовый файл в кодировке UTF-8.
    Используется для HTML и CSS файлов.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_binary_file(path):
    """
    Читает бинарный файл и возвращает байты.
    Используется для картинок и иконок.
    """
    with open(path, "rb") as f:
        return f.read()


def get_content_type(path):
    """
    Определяет MIME-тип по расширению файла.
    Если расширение неизвестно — возвращает application/octet-stream.
    """
    ext = os.path.splitext(path)[1].lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def make_response(start_response, status, body, content_type="text/html; charset=utf-8"):
    """
    Формирует HTTP-ответ с нужными заголовками.
    Преобразует строку в байты, если нужно,
    и вызывает start_response для передачи ответа серверу.
    """
    if isinstance(body, str):
        body = body.encode("utf-8")

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Server", "Coworking-WSGI/1.0"),
        ("Cache-Control", "no-cache"),
    ]
    start_response(status, headers)
    return [body]


def serve_html(filename, start_response):
    """
    Отдаёт HTML-файл из папки templates.
    Если файл не имеет расширения .html или не существует —
    возвращает страницу 404.
    """
    if not filename.endswith(".html"):
        return make_response(start_response, "404 Not Found", "<h1>404 — Только HTML-файлы</h1>")

    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        html = read_text_file(filepath)
        return make_response(start_response, "200 OK", html, "text/html; charset=utf-8")
    else:
        return make_response(start_response, "404 Not Found", f"<h1>404 — Файл {filename} не найден</h1>")


def serve_file(filepath, start_response):
    """
    Отдаёт один файл с правильным Content-Type.
    Текстовые файлы читаются как текст,
    бинарные (картинки) — как байты.
    """
    content_type = get_content_type(filepath)

    if content_type.startswith("text/") or content_type.startswith("application/json"):
        body = read_text_file(filepath).encode("utf-8")
    else:
        body = read_binary_file(filepath)

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Server", "Coworking-WSGI/1.0"),
    ]
    start_response("200 OK", headers)
    return [body]


def serve_static(path, start_response):
    """
    Отдаёт файлы из папки static (картинки, CSS, JS).
    Принимает путь вида /static/logo.png
    и ищет файл внутри папки static.
    """
    relative = path[len("/static/"):]
    filepath = os.path.join(STATIC_DIR, relative)

    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return make_response(start_response, "404 Not Found", "<h1>404 — Статика не найдена</h1>")

    return serve_file(filepath, start_response)


# ============================================================
# Главная точка входа WSGI
# ============================================================

def application(environ, start_response):
    """
    Главная точка входа WSGI. Обрабатывает все запросы.

    Логика:
    1. Логирует запрос (метод, путь, User-Agent).
    2. Если путь начинается с /static/ — отдать статику.
    3. Если запрошен /favicon.ico — отдать иконку.
    4. Если путь есть в ROUTES — отдать HTML-страницу.
    5. Если путь оканчивается на .html — попробовать найти файл.
    6. Если метод DELETE и путь /bookings/<id> — отменить бронь.
    7. Иначе — вернуть 404.
    """
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # --- ОБРАБОТКА DELETE-ЗАПРОСА (отмена брони) ---
    if method == "DELETE" and path.startswith("/bookings/"):
        try:
            booking_id = int(path.split("/")[-1])

            response_data = json.dumps({"success": True, "message": f"Бронь {booking_id} отменена"})

            headers = [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(response_data))),
                ("Server", "Coworking-WSGI/1.0"),
            ]
            start_response("200 OK", headers)
            return [response_data.encode("utf-8")]

        except ValueError:
            start_response("400 Bad Request", [("Content-Type", "text/plain")])
            return [b"Invalid booking ID"]

    # --- Логирование ---
    user_agent = environ.get("HTTP_USER_AGENT", "Unknown")
    print(f"[LOG] {method} {path} | UA: {user_agent[:50]}...")

    # --- Проверка метода ---
    if method not in ("GET", "POST", "DELETE"):
        return make_response(start_response, "405 Method Not Allowed", "<h1>405 — Метод не разрешен</h1>")

    # ---  Статика: /static/* ---
    if path.startswith("/static/"):
        return serve_static(path, start_response)

    # - Иконка сайта ---
    if path == "/favicon.ico":
        favicon = os.path.join(STATIC_DIR, "favicon.ico")
        if os.path.exists(favicon):
            return serve_file(favicon, start_response)
        return make_response(start_response, "404 Not Found", "<h1>404 — Иконка не найдена</h1>")

    # . HTML-страницы из ROUTES ---
    if method == "GET":
        if path in ROUTES:
            return serve_html(ROUTES[path], start_response)

        # --- Автопоиск HTML-файлов ---
        if path.endswith(".html"):
            filename = path.lstrip("/")
            return serve_html(filename, start_response)

    # ---  Всё остальное — 404 ---
    return make_response(start_response, "404 Not Found", "<h1>404 — Страница не найдена</h1>")
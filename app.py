from wsgiref.simple_server import make_server
from controllers import pages, static, api

# ============================================================
# МАРШРУТИЗАЦИЯ: URL -> Контроллер
# ============================================================
ROUTES = {
    "/": pages.index,
    "/login": pages.login,
    "/register": pages.register,
    "/workspaces": pages.workspaces,
    "/bookings": pages.bookings,
    "/bookings/new": pages.booking_new,
}

def make_response(start_response, body, status, content_type):
    """Формирует финальный HTTP-ответ."""
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

def application(environ, start_response):
    """
    Главная точка входа WSGI.
    Только маршрутизация. Обработка — в контроллерах.
    """
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # 1. Статика (/static/*)
    if path.startswith("/static/"):
        body, status, ctype = static.serve_static(environ, start_response)
        return make_response(start_response, body, status, ctype)

    # 2. API (DELETE)
    if method == "DELETE" and path.startswith("/bookings/"):
        body, status, ctype = api.cancel_booking(environ, start_response)
        return make_response(start_response, body, status, ctype)

    # 3. HTML Страницы
    if method == "GET" and path in ROUTES:
        controller = ROUTES[path]
        body, status, ctype = controller(environ, start_response)
        return make_response(start_response, body, status, ctype)

    # 4. 404
    return make_response(start_response, "<h1>404 — Страница не найдена</h1>", "404 Not Found", "text/html")
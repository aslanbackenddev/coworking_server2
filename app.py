"""
Главный модуль WSGI-приложения «Коворкинг».
"""
from controllers import pages, static, api

ROUTES = {
    "/": pages.index,
    "/login": pages.login,
    "/register": pages.register,
    "/workspaces": pages.workspaces,
    "/bookings": pages.bookings,
    "/bookings/new": pages.booking_new,
    "/logout": pages.logout,
    "/admin": pages.admin,
}

def make_response(start_response, body, status, content_type):
    """Формирует HTTP-ответ."""
    if isinstance(body, str):
        body = body.encode("utf-8")

    if content_type.startswith("text/") and "charset" not in content_type:
        content_type += "; charset=utf-8"

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Server", "Coworking-WSGI/1.0"),
        ("Cache-Control", "no-cache"),
    ]

    try:
        start_response(status, headers)
    except AssertionError:
        pass

    return [body]

def application(environ, start_response):
    """Точка входа WSGI-приложения."""
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    try:
        if path.startswith("/static/"):
            body, status, ctype = static.serve_static(environ, start_response)
            return make_response(start_response, body, status, ctype)

        if method == "DELETE" and path.startswith("/bookings/"):
            body, status, ctype = api.cancel_booking(environ, start_response)
            return make_response(start_response, body, status, ctype)

        if path in ROUTES:
            controller = ROUTES[path]
            body, status, ctype = controller(environ, start_response)

            # Если контроллер вернул список байтов (редирект)
            if isinstance(body, list) and all(isinstance(b, bytes) for b in body):
                return body

            return make_response(start_response, body, status, ctype)

        return make_response(start_response, "<h1>404 — Страница не найдена</h1>", "404 Not Found", "text/html; charset=utf-8")

    except Exception as e:
        # Если произошла ошибка, выводим её прямо в браузер
        import traceback
        error_html = f"<h1>Ошибка сервера</h1><pre>{traceback.format_exc()}</pre>"
        return make_response(start_response, error_html, "500 Internal Server Error", "text/html; charset=utf-8")
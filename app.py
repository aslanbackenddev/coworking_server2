import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def read_template(name):
    """Читает HTML-файл из папки templates."""
    path = os.path.join(TEMPLATES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def application(environ, start_response):
    """WSGI-приложение. Вызывается сервером на каждый запрос."""
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path == "/" and method == "GET":
        html = read_template("index.html")
        status = "200 OK"
    else:
        html = "<h1>404 — Страница не найдена</h1>"
        status = "404 Not Found"

    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(html.encode("utf-8")))),
    ]
    start_response(status, headers)

    return [html.encode("utf-8")]
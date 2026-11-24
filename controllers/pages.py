import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def render_page(filename):
    """
    Вспомогательная функция для чтения HTML-файла из папки templates.
    """
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>404 — Файл не найден</h1>"


def response_OK(filename):
    """
    Функция, которая автоматически формирует
    успешный HTTP-ответ (200 OK) для HTML-страницы.
    """

    def controller(environ, start_response):
        """
        Внутренний контроллер, который вызывается роутером
        """
        html = render_page(filename)
        return html, "200 OK", "text/html; charset=utf-8"

    return controller

"""
Создаем готовые контроллеры, передавая им имена файлов
"""
index = response_OK("index.html")
login = response_OK("login.html")
register = response_OK("register.html")
workspaces = response_OK("workspaces.html")
bookings = response_OK("bookings.html")
booking_new = response_OK("booking_new.html")
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

def render_page(filename):
    """Вспомогательная функция. Читает HTML-файл из папки templates."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return None

def index(environ, start_response):
    """Контроллер главной страницы. Возвращает index.html."""
    html = render_page("index.html")
    return html, "200 OK", "text/html; charset=utf-8"

def login(environ, start_response):
    """Контроллер страницы входа. Возвращает login.html."""
    html = render_page("login.html")
    return html, "200 OK", "text/html; charset=utf-8"

def register(environ, start_response):
    """Контроллер страницы регистрации. Возвращает register.html."""
    html = render_page("register.html")
    return html, "200 OK", "text/html; charset=utf-8"

def workspaces(environ, start_response):
    """Контроллер списка мест. Возвращает workspaces.html."""
    html = render_page("workspaces.html")
    return html, "200 OK", "text/html; charset=utf-8"

def bookings(environ, start_response):
    """Контроллер страницы 'Мои брони'. Возвращает bookings.html."""
    html = render_page("bookings.html")
    return html, "200 OK", "text/html; charset=utf-8"

def booking_new(environ, start_response):
    """Контроллер страницы бронирования. Возвращает booking_new.html."""
    html = render_page("booking_new.html")
    return html, "200 OK", "text/html; charset=utf-8"
import os
import urllib.parse
from business_logics import booking_service, session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

def render_page(filename: str, context: dict = None) -> str:
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        if context:
            for k, v in context.items():
                html = html.replace("{{" + k + "}}", str(v))
        return html
    return "<h1>404 — Файл не найден</h1>"

def _get_current_user(environ):
    cookie = environ.get("HTTP_COOKIE", "")
    sid = None
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("sid="):
            sid = part[4:]
            break
    return session.get_user(sid)

def index(environ, start_response):
    return render_page("index.html"), "200 OK", "text/html; charset=utf-8"

def login(environ, start_response):
    if environ.get("REQUEST_METHOD") == "GET":
        return render_page("login.html"), "200 OK", "text/html; charset=utf-8"

    size = int(environ.get("CONTENT_LENGTH", "0") or 0)
    body = environ["wsgi.input"].read(size).decode("utf-8")
    form = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

    ok, result = booking_service.authenticate(form.get("email", ""), form.get("password", ""))
    if not ok:
        html = render_page("login.html").replace("</h1>", f"</h1><p style='color:red'>{result}</p>", 1)
        return html, "200 OK", "text/html; charset=utf-8"

    sid = session.create_session(result["id"])
    start_response("302 Found", [
        ("Location", "/workspaces"),
        ("Set-Cookie", f"sid={sid}; Path=/; HttpOnly"),
        ("Content-Length", "0"),
    ])
    return [b""]

def register(environ, start_response):
    if environ.get("REQUEST_METHOD") == "GET":
        return render_page("register.html"), "200 OK", "text/html; charset=utf-8"

    size = int(environ.get("CONTENT_LENGTH", "0") or 0)
    body = environ["wsgi.input"].read(size).decode("utf-8")
    form = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

    ok, result = booking_service.register_user(
        form.get("name", ""), form.get("email", ""), form.get("password", "")
    )
    if not ok:
        html = render_page("register.html").replace("</h1>", f"</h1><p style='color:red'>{result}</p>", 1)
        return html, "200 OK", "text/html; charset=utf-8"

    sid = session.create_session(result["id"])
    start_response("302 Found", [
        ("Location", "/workspaces"),
        ("Set-Cookie", f"sid={sid}; Path=/; HttpOnly"),
        ("Content-Length", "0"),
    ])
    return [b""]

def workspaces(environ, start_response):
    ok, places = booking_service.list_places()
    items_html = ""
    for p in places:
        items_html += f"""
        <div class="item">
            <div class="info">
                <span class="name">{p['name']}</span>
                <span class="price">{p['price']} ₽/час</span>
            </div>
            <a href="/bookings/new?place_id={p['id']}" class="button">Забронировать</a>
        </div>
        """
    html = render_page("workspaces.html", {"places_list": items_html})
    return html, "200 OK", "text/html; charset=utf-8"

def bookings(environ, start_response):
    user = _get_current_user(environ)
    if not user:
        start_response("302 Found", [("Location", "/login"), ("Content-Length", "0")])
        return [b""]

    ok, user_bookings = booking_service.list_user_bookings(user["id"])
    items_html = ""
    for b in user_bookings:
        place = next((p for p in booking_service.list_places()[1] if p["id"] == b["place_id"]), None)
        place_name = place["name"] if place else f"Место {b['place_id']}"
        items_html += f"""
        <div class="item" data-id="{b['id']}">
            <div class="info">
                <span class="name">{place_name}</span>
                <span class="price">{b['date']} | {b['start']}–{b['end']}</span>
            </div>
            <button class="btn-cancel" onclick="cancelBooking({b['id']})">Отменить</button>
        </div>
        """
    html = render_page("bookings.html", {"bookings_list": items_html})
    return html, "200 OK", "text/html; charset=utf-8"

def booking_new(environ, start_response):
    user = _get_current_user(environ)
    if not user:
        return "Необходимо войти", "401 Unauthorized", "text/plain"

    if environ.get("REQUEST_METHOD") == "GET":
        qs = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        place_id = qs.get("place_id", ["1"])[0]
        return render_page("booking_new.html", {"place_id": place_id}), "200 OK", "text/html; charset=utf-8"

    size = int(environ.get("CONTENT_LENGTH", "0") or 0)
    body = environ["wsgi.input"].read(size).decode("utf-8")
    form = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

    place_id = int(form.get("place_id", 0))
    date = form.get("date", "")
    start = form.get("start", "")
    end = form.get("end", "")

    ok, result = booking_service.create_booking(user["id"], place_id, date, start, end)
    if not ok:
        html = render_page("booking_new.html", {"place_id": place_id}).replace("</h1>", f"</h1><p style='color:red'>{result}</p>", 1)
        return html, "200 OK", "text/html; charset=utf-8"

    start_response("302 Found", [("Location", "/bookings"), ("Content-Length", "0")])
    return [b""]

def logout(environ, start_response):
    cookie = environ.get("HTTP_COOKIE", "")
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("sid="):
            session.destroy(part[4:])
            break
    start_response("302 Found", [
        ("Location", "/"),
        ("Set-Cookie", "sid=; Path=/; Max-Age=0"),
        ("Content-Length", "0"),
    ])
    return [b""]

def admin(environ, start_response):
    user = _get_current_user(environ)
    if not user or user.get("role") != "admin":
        return "Доступ запрещён", "403 Forbidden", "text/plain"

    if environ.get("REQUEST_METHOD") == "POST":
        size = int(environ.get("CONTENT_LENGTH", "0") or 0)
        body = environ["wsgi.input"].read(size).decode("utf-8")
        form = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

        action = form.get("action")
        if action == "add_place":
            name = form.get("name", "")
            desc = form.get("description", "")
            price = int(form.get("price", 0))
            ok, res = booking_service.add_place(name, desc, price, user)
            if not ok:
                return f"<h1>Ошибка</h1><p>{res}</p><a href='/admin'>Назад</a>", "400 Bad Request", "text/html"
        elif action == "delete_place":
            place_id = int(form.get("place_id", 0))
            ok, res = booking_service.delete_place(place_id, user)
            if not ok:
                return f"<h1>Ошибка</h1><p>{res}</p><a href='/admin'>Назад</a>", "400 Bad Request", "text/html"

        start_response("302 Found", [("Location", "/admin"), ("Content-Length", "0")])
        return [b""]

    ok_places, places = booking_service.list_places()
    ok_bookings, bookings = booking_service.list_all_bookings(user)

    places_html = "".join(f"""
        <div class="item">
            <div class="info"><span class="name">{p['name']}</span><span class="price">{p['price']} ₽</span></div>
            <form method="POST" action="/admin" style="display:inline;">
                <input type="hidden" name="action" value="delete_place">
                <input type="hidden" name="place_id" value="{p['id']}">
                <button type="submit" class="btn-cancel">Удалить</button>
            </form>
        </div>
    """ for p in places)

    bookings_html = ""
    if ok_bookings:
        for b in bookings:
            place = next((p for p in places if p["id"] == b["place_id"]), None)
            p_name = place["name"] if place else "?"
            bookings_html += f"""
            <div class="item">
                <div class="info"><span class="name">{p_name}</span><span class="price">Пользователь ID {b['user_id']} | {b['date']} {b['start']}-{b['end']} ({b['status']})</span></div>
            </div>
            """

    html = render_page("admin.html", {
        "places_list": places_html,
        "bookings_list": bookings_html
    })
    return html, "200 OK", "text/html; charset=utf-8"
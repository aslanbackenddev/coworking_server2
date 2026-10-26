import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

MIME_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}

def serve_static(environ, start_response):
    """Отдаёт файлы из папки static (CSS, картинки)."""
    path = environ.get("PATH_INFO", "/")
    relative = path[len("/static/"):]
    filepath = os.path.join(STATIC_DIR, relative)

    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return "<h1>404 — Статика не найдена</h1>", "404 Not Found", "text/html"

    ext = os.path.splitext(filepath)[1].lower()
    content_type = MIME_TYPES.get(ext, "application/octet-stream")

    if content_type.startswith("text/"):
        with open(filepath, "r", encoding="utf-8") as f:
            body = f.read()
    else:
        with open(filepath, "rb") as f:
            body = f.read()

    return body, "200 OK", content_type
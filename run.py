from wsgiref.simple_server import make_server
from app import application

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    with make_server(host, port, application) as server:
        print(f"Сервер запущен: http://localhost:{port}")
        print("Нажмите Ctrl+C для остановки")
        server.serve_forever()
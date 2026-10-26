import json

def cancel_booking(environ, start_response):
    """Контроллер отмены брони. Обрабатывает DELETE-запрос и возвращает JSON."""
    path = environ.get("PATH_INFO", "/")
    try:
        # Извлекаем ID брони из URL (например, /bookings/5 -> 5)
        booking_id = int(path.split("/")[-1])
        response_data = json.dumps({"success": True, "message": f"Бронь {booking_id} отменена"})
        return response_data, "200 OK", "application/json; charset=utf-8"
    except ValueError:
        # Если ID не число, возвращаем ошибку 400
        return "Invalid booking ID", "400 Bad Request", "text/plain"
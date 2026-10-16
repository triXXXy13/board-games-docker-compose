import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Локальный эмулятор специализированного каталога настольных игр.
GAMES = [
    {"id": "catan", "title": "Колонизаторы", "players_min": 3, "players_max": 4, "duration_minutes": 75, "genre": "Стратегия", "description": "Собирайте ресурсы, стройте дороги и поселения."},
    {"id": "carcassonne", "title": "Каркассон", "players_min": 2, "players_max": 5, "duration_minutes": 40, "genre": "Тактика", "description": "Создавайте средневековый ландшафт из тайлов."},
    {"id": "ticket-to-ride", "title": "Билет на поезд", "players_min": 2, "players_max": 5, "duration_minutes": 60, "genre": "Семейная", "description": "Собирайте карты и соединяйте города железными дорогами."},
    {"id": "pandemic", "title": "Пандемия", "players_min": 2, "players_max": 4, "duration_minutes": 45, "genre": "Кооперативная", "description": "Работайте командой, чтобы остановить распространение болезней."},
    {"id": "azul", "title": "Азул", "players_min": 2, "players_max": 4, "duration_minutes": 40, "genre": "Абстрактная", "description": "Составляйте узоры из цветных плиток."},
    {"id": "dixit", "title": "Диксит", "players_min": 3, "players_max": 6, "duration_minutes": 30, "genre": "Творческая", "description": "Угадывайте ассоциации по иллюстрированным картам."},
    {"id": "wingspan", "title": "Крылья", "players_min": 1, "players_max": 5, "duration_minutes": 70, "genre": "Стратегия", "description": "Создавайте заповедник и привлекайте птиц."},
    {"id": "7-wonders", "title": "7 чудес", "players_min": 3, "players_max": 7, "duration_minutes": 30, "genre": "Цивилизация", "description": "Развивайте древнюю цивилизацию за три эпохи."},
]


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "board-game-catalog"})


@app.get("/games")
def search_games():
    try:
        players = int(request.args.get("players", "4"))
        max_minutes = int(request.args.get("max_minutes", "90"))
        if players < 1 or max_minutes < 1:
            return jsonify({"error": "Параметры должны быть положительными."}), 400
    except ValueError:
        return jsonify({"error": "Параметры должны быть целыми числами."}), 400

    results = [
        game for game in GAMES
        if game["players_min"] <= players <= game["players_max"]
        and game["duration_minutes"] <= max_minutes
    ]
    return jsonify({"count": len(results), "games": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))

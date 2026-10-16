import os
import time
from contextlib import contextmanager
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "boardgames"),
    "user": os.getenv("DB_USER", "boarduser"),
    "password": os.getenv("DB_PASSWORD", "boardpass"),
}
WEB_SERVICE_URL = os.getenv("WEB_SERVICE_URL", "http://localhost:5001")


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def db_session():
    """Open a database connection, manage its transaction, and always close it."""
    connection = get_connection()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def wait_for_database():
    for attempt in range(30):
        try:
            connection = get_connection()
            connection.close()
            print("Database connection established.")
            return
        except psycopg2.OperationalError as exc:
            print(f"Waiting for database ({attempt + 1}/30): {exc}")
            time.sleep(2)
    raise RuntimeError("Database did not become available in time")


@app.get("/health")
def health():
    try:
        connection = get_connection()
        connection.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 503


@app.get("/api/games")
def search_games():
    try:
        players = int(request.args.get("players", "4"))
        max_minutes = int(request.args.get("max_minutes", "90"))
        if players < 1 or players > 20 or max_minutes < 1 or max_minutes > 600:
            return jsonify({"error": "Число игроков: 1–20, время партии: 1–600 минут."}), 400
        response = requests.get(
            f"{WEB_SERVICE_URL}/games",
            params={"players": players, "max_minutes": max_minutes},
            timeout=5,
        )
        response.raise_for_status()
        return jsonify(response.json())
    except ValueError:
        return jsonify({"error": "Параметры players и max_minutes должны быть целыми числами."}), 400
    except requests.RequestException as exc:
        app.logger.exception("Web-service request failed")
        return jsonify({"error": "Сервис каталога временно недоступен.", "details": str(exc)}), 502


@app.get("/api/collection")
def get_collection():
    try:
        with db_session() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, title, players_min, players_max, duration_minutes,
                           genre, description, saved_at
                    FROM board_games ORDER BY saved_at DESC, title
                """)
                rows = cursor.fetchall()
        for row in rows:
            row["saved_at"] = row["saved_at"].isoformat()
        return jsonify(rows)
    except Exception:
        app.logger.exception("Could not read collection")
        return jsonify({"error": "Не удалось получить коллекцию."}), 500


@app.post("/api/collection")
def add_to_collection():
    data = request.get_json(silent=True) or {}
    required = ["id", "title", "players_min", "players_max", "duration_minutes", "genre", "description"]
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({"error": "Не хватает полей: " + ", ".join(missing)}), 400

    try:
        players_min = int(data["players_min"])
        players_max = int(data["players_max"])
        duration = int(data["duration_minutes"])
        if players_min < 1 or players_max < players_min or duration < 1:
            return jsonify({"error": "Проверьте количество игроков и длительность партии."}), 400

        with db_session() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO board_games
                    (id, title, players_min, players_max, duration_minutes, genre, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    RETURNING id
                """, (str(data["id"]), str(data["title"]), players_min, players_max,
                      duration, str(data["genre"]), str(data["description"])))
                inserted = cursor.fetchone()
        if not inserted:
            return jsonify({"message": "Эта игра уже есть в коллекции."}), 200
        return jsonify({"message": "Игра добавлена в коллекцию.", "id": inserted["id"]}), 201
    except (TypeError, ValueError):
        return jsonify({"error": "Числовые поля имеют неверный формат."}), 400
    except Exception:
        app.logger.exception("Could not add game")
        return jsonify({"error": "Не удалось сохранить игру."}), 500


@app.delete("/api/collection/<game_id>")
def delete_from_collection(game_id):
    try:
        with db_session() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM board_games WHERE id = %s", (game_id,))
                deleted = cursor.rowcount
        if not deleted:
            return jsonify({"error": "Игра не найдена в коллекции."}), 404
        return jsonify({"message": "Игра удалена из коллекции."})
    except Exception:
        app.logger.exception("Could not delete game")
        return jsonify({"error": "Не удалось удалить игру."}), 500


if __name__ == "__main__":
    wait_for_database()
    app.run(host="0.0.0.0", port=5000)

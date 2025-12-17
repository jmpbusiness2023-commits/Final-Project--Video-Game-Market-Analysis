from flask import Flask, jsonify, request
from sqlalchemy import text
import pymysql

app = Flask(__name__)

# ====================================
# Database connection
# ====================================
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="sqlpassword:=9SfuA7",
        database="video_game_market",
        cursorclass=pymysql.cursors.DictCursor
    )

# ====================================
# Home route
# ====================================
@app.route("/")
def home():
    return jsonify({
        "message": "Video Games API",
        "endpoints": {
            "/games": "List games (pagination)",
            "/games/<rawg_id>": "Game details"
        }
    })

# ====================================
# Endpoint 1: Games (collection)
# ====================================
@app.route("/games", methods=["GET"])
def get_games_collection():
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT rawg_id, game_name, user_rating, ratings_count
            FROM games
            LIMIT %s OFFSET %s
        """, (limit, offset))
        games = cursor.fetchall()
    conn.close()

    return jsonify({
        "count": len(games),
        "results": games
    })

# ====================================
# Endpoint 2: Single game
# ====================================
@app.route("/games/<int:rawg_id>", methods=["GET"])
def get_game(rawg_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM games
            WHERE rawg_id = %s
        """, (rawg_id,))
        game = cursor.fetchone()
    conn.close()

    if game is None:
        return jsonify({"error": "Game not found"}), 404

    return jsonify(game)

# ====================================
# Run app
# ====================================
if __name__ == "__main__":
    app.run(debug=True)

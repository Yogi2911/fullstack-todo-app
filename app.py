"""
Full-Stack Todo App
--------------------
A simple full-stack Python web application using:
  - Flask (backend + REST API)
  - SQLite (database)
  - HTML/CSS/JS (frontend, served by Flask)

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request, render_template, g
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.db")


# ---------- Database helpers ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    db.close()


# ---------- Frontend route ----------

@app.route("/")
def index():
    return render_template("index.html")


# ---------- REST API routes ----------

@app.route("/api/todos", methods=["GET"])
def get_todos():
    db = get_db()
    rows = db.execute(
        "SELECT id, task, done, created_at FROM todos ORDER BY id DESC"
    ).fetchall()
    todos = [dict(row) for row in rows]
    return jsonify(todos)


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json(silent=True) or {}
    task = data.get("task", "").strip()
    if not task:
        return jsonify({"error": "Task text is required"}), 400

    db = get_db()
    cur = db.execute("INSERT INTO todos (task, done) VALUES (?, 0)", (task,))
    db.commit()
    new_id = cur.lastrowid
    row = db.execute(
        "SELECT id, task, done, created_at FROM todos WHERE id = ?", (new_id,)
    ).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    db = get_db()

    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Todo not found"}), 404

    task = data.get("task", row["task"])
    done = data.get("done", row["done"])
    db.execute(
        "UPDATE todos SET task = ?, done = ? WHERE id = ?",
        (task, int(bool(done)), todo_id),
    )
    db.commit()
    updated = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return jsonify(dict(updated))


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    db = get_db()
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Todo not found"}), 404
    db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    return jsonify({"success": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)

"""
Full-Stack Todo App
-------------------
Flask + SQLite Todo application with login authentication.
"""

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    g,
    session,
    redirect,
    url_for
)

import sqlite3
import os


app = Flask(__name__)

# Secret key for session authentication
app.secret_key = "dev-secret-key-change-in-production"


DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "todos.db"
)


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

    # Todo table
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

    # Users table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    # Create demo user if it doesn't exist
    existing_user = db.execute(
        "SELECT id FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if existing_user is None:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    db.commit()
    db.close()


# ---------- Authentication ----------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("index"))

        return render_template(
            "login.html",
            error="Invalid username or password. Please try again."
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


def login_required():
    return "user_id" in session


# ---------- Frontend route ----------

@app.route("/")
def index():

    if not login_required():
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        username=session.get("username")
    )


# ---------- User Profile ----------

@app.route("/profile")
def profile():

    if not login_required():
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        username=session.get("username")
    )


# ---------- REST API routes ----------

@app.route("/api/todos", methods=["GET"])
def get_todos():

    if not login_required():
        return jsonify({
            "error": "Authentication required"
        }), 401

    db = get_db()

    rows = db.execute(
        """
        SELECT id, task, done, created_at
        FROM todos
        ORDER BY id DESC
        """
    ).fetchall()

    todos = [dict(row) for row in rows]

    return jsonify(todos)


@app.route("/api/todos", methods=["POST"])
def create_todo():

    if not login_required():
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(silent=True) or {}

    task = data.get("task", "").strip()

    if not task:
        return jsonify({
            "error": "Task text is required"
        }), 400

    db = get_db()

    cur = db.execute(
        """
        INSERT INTO todos (task, done)
        VALUES (?, 0)
        """,
        (task,)
    )

    db.commit()

    new_id = cur.lastrowid

    row = db.execute(
        """
        SELECT id, task, done, created_at
        FROM todos
        WHERE id = ?
        """,
        (new_id,)
    ).fetchone()

    return jsonify(dict(row)), 201


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):

    if not login_required():
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(silent=True) or {}

    db = get_db()

    row = db.execute(
        """
        SELECT *
        FROM todos
        WHERE id = ?
        """,
        (todo_id,)
    ).fetchone()

    if row is None:
        return jsonify({
            "error": "Todo not found"
        }), 404

    task = data.get("task", row["task"])
    done = data.get("done", row["done"])

    db.execute(
        """
        UPDATE todos
        SET task = ?, done = ?
        WHERE id = ?
        """,
        (
            task,
            int(bool(done)),
            todo_id
        )
    )

    db.commit()

    updated = db.execute(
        """
        SELECT *
        FROM todos
        WHERE id = ?
        """,
        (todo_id,)
    ).fetchone()

    return jsonify(dict(updated))


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):

    if not login_required():
        return jsonify({
            "error": "Authentication required"
        }), 401

    db = get_db()

    row = db.execute(
        """
        SELECT *
        FROM todos
        WHERE id = ?
        """,
        (todo_id,)
    ).fetchone()

    if row is None:
        return jsonify({
            "error": "Todo not found"
        }), 404

    db.execute(
        """
        DELETE FROM todos
        WHERE id = ?
        """,
        (todo_id,)
    )

    db.commit()

    return jsonify({
        "success": True
    })


# ---------- Application entry point ----------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
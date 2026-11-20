import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "students.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            school TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template('index.html')
   
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO students (full_name, email, school) VALUES (?, ?, ?)",
            (request.form["full_name"], request.form["email"], request.form["school"]),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("thanks"))
    return render_template("signup.html")

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")
import os
from flask import Response

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")

def check_admin():
    auth = request.authorization
    return auth is not None and auth.password == ADMIN_PASSWORD

def ask_login():
    return Response("Admin login required", 401,
                    {"WWW-Authenticate": 'Basic realm="Admin"'})

@app.route("/admin")
def admin():
    if not check_admin():
        return ask_login()
    conn = get_db()
    students = conn.execute(
        "SELECT * FROM students ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("admin.html", students=students)

@app.route("/admin/update/<int:student_id>/<action>", methods=["POST"])
def admin_update(student_id, action):
    if not check_admin():
        return ask_login()
    if action not in ("verified", "rejected"):
        return "Invalid action", 400
    conn = get_db()
    conn.execute("UPDATE students SET status = ? WHERE id = ?", (action, student_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))
init_db()

if __name__ == "__main__":
    app.run(debug=True)
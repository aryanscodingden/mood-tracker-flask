from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("moods.db")

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mood TEXT
        )
    """)

@app.route("/")
def home():
    db = get_db()
    return render_template("home.html")

@app.route("/add/<mood>")
def add(mood):
    db = get_db()
    db.execute("INSERT INTO moods (mood) VALUES (?)", (mood,))
    db.commit()
    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)
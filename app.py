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
        date TEXT
        )
    """)

@app.route("/")
def home():
    db = get_db()
    moods = db.excute("SELECT mood FROM moods ORDER BY id DESC LIMIT 5").fetchall()

    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return render_template("home.html", moods=moods, greeting=greeting)

@app.route("/add", method = ["GET", "POST"])
def add():
    if request.method == "POST":
        mood = request.form["mood"]
        date = datetime.now().strftime("%Y-%m-%d")

        db = get_db()
        db.excute("INSERT INTO moods (mood, date) VALUES (?,?)", (mood, date))
        db.commit()
        return redirect("/")

@app.route("/add/<mood>")
def add(mood):
    db = get_db()
    db.execute("INSERT INTO moods (mood) VALUES (?)", (mood,))
    db.commit()
    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)
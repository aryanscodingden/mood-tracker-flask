from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
from calendar import monthrange
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DB_PATH = os.path.join('/tmp', 'moods.db') if os.environ.get('VERCEL') else 'moods.db'

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT,
            date TEXT
            )
        """)

init_db()

@app.route("/")
def home():
    init_db()
    with get_db() as db:
        moods = db.execute("SELECT mood FROM moods ORDER BY id DESC LIMIT 5").fetchall()

        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        now = datetime.now()
        year = now.year
        month = now.month

        month_moods = db.execute(
            "SELECT date, mood FROM moods WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?",
            (str(year), f"{month:02d}")
        ).fetchall()

        mood_dict = {mood[0]: mood[1] for mood in month_moods}
        first_day_weekday, num_days = monthrange(year, month)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        return render_template("home.html", 
                             moods=moods, 
                             greeting=greeting,
                             mood_dict=mood_dict,
                             year=year,
                             month=month,
                             month_name=month_names[month-1],
                             first_day_weekday=first_day_weekday,
                             num_days=num_days)

@app.route("/add", methods = ["GET", "POST"])
def add():
    if request.method == "POST":
        init_db()
        mood = request.form["mood"]
        date = datetime.now().strftime("%Y-%m-%d")

        with get_db() as db:
            db.execute("INSERT INTO moods (mood, date) VALUES (?,?)", (mood, date))
            db.commit()
        return redirect('/')

    return render_template("add.html")

@app.route("/calendar")
def calendar():
    init_db()
    with get_db() as db:
        now = datetime.now()
        year = request.args.get('year', now.year, type=int)
        month = request.args.get('month', now.month, type=int)

        moods = db.execute(
            "SELECT date, mood FROM moods WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?",
            (str(year), f"{month:02d}")
        ).fetchall()

        mood_dict = {mood[0]: mood[1] for mood in moods}

        first_day_weekday, num_days = monthrange(year, month)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        return render_template("calendar.html",
                             mood_dict=mood_dict,
                             year=year,
                             month=month,
                             month_name=month_names[month-1],
                             first_day_weekday=first_day_weekday,
                             num_days=num_days)

@app.route("/delete/<date>", methods=["POST"])
def delete(date):
    init_db()
    with get_db() as db:
        db.execute("DELETE FROM moods WHERE date = ?", (date,))
        db.commit()
    return redirect('/')

@app.route("/stats")
def stats():
    init_db()
    with get_db() as db:
        total_moods = db.execute("SELECT COUNT(*) FROM moods").fetchone()[0]

        mood_counts = db.execute(
            "SELECT mood, COUNT(*) as count from moods GROUP BY mood ORDER BY count DESC"
        ).fetchall()

        all_dates = db.execute("SELECT DISTINCT date FROM moods ORDER BY date DESC").fetchall()
        streak = 0 
        if all_dates:
            current_date = datetime.now().date()
            for date_row in all_dates:
                date_obj = datetime.strptime(date_row[0], "%Y-%m-%d").date()
                if date_obj == current_date or (streak > 0 and date_obj == current_date - timedelta(days=streak)):
                    streak += 1 
                    current_date = date_obj
                else:
                    break

        recent_moods = db.execute(
            "SELECT date, mood FROM moods WHERE date >= date('now', '-7 days') ORDER BY date DESC"
        ).fetchall()
                
        return render_template("stats.html",
                total_moods=total_moods,
                mood_counts=mood_counts,
                streak=streak,
                recent_moods=recent_moods)

            
if __name__ == "__main__":
    app.run(debug=True, port=5001)
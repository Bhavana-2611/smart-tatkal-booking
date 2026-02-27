from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_user", methods=["POST"])
def register_user():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                   (name, email, password))
    conn.commit()
    conn.close()

    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect("/search")
        else:
            return "Invalid Email or Password ❌"

    return render_template("login.html")
@app.route("/search")
def search():
    return render_template("search.html")
@app.route("/train_list", methods=["POST"])
def train_list():
    from_station = request.form["from"]
    to_station = request.form["to"]
    date = request.form["date"]
    travel_class = request.form["class"]

    return render_template("train_list.html",
                       from_station=from_station,
                       to_station=to_station,
                       date=date,
                       travel_class=travel_class)
@app.route("/compartments")
def compartments():
    travel_class = request.args.get("class")

    if travel_class == "3A" or travel_class == "2A":
        coaches = ["A1", "A2"]   # AC coaches
    else:
        coaches = ["S" + str(i) for i in range(1, 11)]  # S1 to S10

    return render_template("compartments.html",
                           coaches=coaches,
                           travel_class=travel_class)
import random

@app.route("/seats")
def seats():
    coach = request.args.get("coach")
    travel_class = request.args.get("class")

    total_seats = 80

    # Randomly book 40 seats (Tatkal situation)
    booked_seats = random.sample(range(1, total_seats+1), 40)

    # Berth pattern (Indian Railways style 8-seat block)
    berth_pattern = ["LB", "MB", "UB", "LB", "MB", "UB", "SL", "SU"]

    seats_data = []

    for i in range(1, total_seats+1):
        berth_type = berth_pattern[(i-1) % 8]
        seats_data.append({
            "number": i,
            "berth": berth_type,
            "booked": i in booked_seats
        })

    return render_template("seats.html",
                           coach=coach,
                           travel_class=travel_class,
                           seats_data=seats_data)
@app.route("/passenger_details", methods=["POST"])
def passenger_details():
    selected_seats = request.form.get("selected_seats")
    coach = request.form.get("coach")
    travel_class = request.form.get("class")

    if not selected_seats:
        return "No seats selected!"

    seat_list = selected_seats.split(",")

    return render_template("passenger_details.html",
                           seat_list=seat_list,
                           coach=coach,
                           travel_class=travel_class)
import random

@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    import random

    coach = request.form.get("coach")
    travel_class = request.form.get("class")

    # Generate PNR
    pnr = random.randint(1000000000, 9999999999)

    passengers = []

    for key in request.form:
        if key.startswith("name_"):
            seat = key.split("_")[1]
            name = request.form.get(f"name_{seat}")
            age = request.form.get(f"age_{seat}")
            gender = request.form.get(f"gender_{seat}")

            passengers.append({
                "seat": seat,
                "name": name,
                "age": age,
                "gender": gender
            })

    return render_template("confirmation.html",
                           pnr=pnr,
                           coach=coach,
                           travel_class=travel_class,
                           passengers=passengers)
if __name__ == "__main__":
    init_db()

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

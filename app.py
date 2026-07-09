from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import uuid
import qrcode
import os


app = Flask(__name__)

app.secret_key = "buspasssecret"



# ---------------- DATABASE ----------------

def create_database():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS passes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        pass_type TEXT,
        price INTEGER,
        pass_id TEXT
    )
    """)


    conn.commit()
    conn.close()



create_database()



# Create QR folder

if not os.path.exists("static/qr"):

    os.makedirs("static/qr")





# ---------------- HOME ----------------

@app.route("/")
def home():

    return render_template("index.html")





# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])

def register():

    if request.method == "POST":


        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]



        conn = sqlite3.connect("database.db")

        cur = conn.cursor()


        cur.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            """,
            (name,email,password)
        )


        conn.commit()

        conn.close()



        return redirect("/login")



    return render_template("register.html")







# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])

def login():


    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]



        conn = sqlite3.connect("database.db")

        cur = conn.cursor()



        cur.execute(
            """
            SELECT name FROM users
            WHERE email=? AND password=?
            """,
            (email,password)
        )


        user = cur.fetchone()


        conn.close()



        if user:


            session["user"] = user[0]

            return redirect("/booking")



    return render_template("login.html")







# ---------------- BOOKING ----------------

@app.route("/booking", methods=["GET","POST"])

def booking():


    if "user" not in session:

        return redirect("/login")



    if request.method == "POST":



        pass_type = request.form["type"]



        prices = {

            "Monthly":1000,

            "Student":500,

            "Daily":100

        }



        price = prices[pass_type]



        # Generate Unique Pass ID

        ticket = "PASS-" + str(uuid.uuid4())[:8]




        # Generate QR Code

        qr_text = f"""

Cloud Bus Pass System

Pass ID:
{ticket}

User:
{session['user']}

Pass Type:
{pass_type}

Price:
₹{price}

"""


        qr = qrcode.make(qr_text)



        qr_filename = ticket + ".png"


        qr_path = os.path.join(
            "static",
            "qr",
            qr_filename
        )


        qr.save(qr_path)




        # Save booking details


        conn = sqlite3.connect("database.db")

        cur = conn.cursor()



        cur.execute(
            """
            INSERT INTO passes
            (user,pass_type,price,pass_id)
            VALUES(?,?,?,?)
            """,
            (
                session["user"],
                pass_type,
                price,
                ticket
            )
        )



        conn.commit()

        conn.close()




        return render_template(
            "pass.html",
            ticket=ticket,
            price=price,
            qr_code=qr_filename
        )



    return render_template("booking.html")







# ---------------- ADMIN ----------------

@app.route("/admin")

def admin():


    conn = sqlite3.connect("database.db")

    cur = conn.cursor()



    cur.execute(
        "SELECT * FROM passes"
    )


    passes = cur.fetchall()



    conn.close()



    return render_template(
        "admin.html",
        passes=passes
    )







# ---------------- LOGOUT ----------------

@app.route("/logout")

def logout():


    session.pop("user",None)


    return redirect("/")







# ---------------- RUN ----------------

if __name__ == "__main__":

    app.run(debug=True)
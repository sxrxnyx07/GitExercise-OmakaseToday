from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey123"

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        username TEXT,
        password TEXT,
        bio TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)

        try:
            with sqlite3.connect("users.db") as conn:
                c = conn.cursor()

                c.execute("""
                    INSERT INTO users (email, username, password, bio)
                    VALUES (?, ?, ?, ?)
                """, (email, username, hashed_pw, ""))

                conn.commit()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="This email is already registered!"
            )

    return render_template("register.html")


@app.route("/check-email")
def check_email():
    email = request.args.get("email")

    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        user = c.fetchone()

    return {"exists": user is not None}

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = c.fetchone()

        if user and check_password_hash(user[2], password):
            session["user"] = email
            return redirect(url_for("profile"))
        else:
            return render_template(
                "login.html",
                error="Invalid email or password"
            )

    return render_template("login.html")

# ---------------- PROFILE ----------------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # UPDATE
    if request.method == "POST":
        username = request.form["username"]
        bio = request.form["bio"]

        c.execute("""
            UPDATE users
            SET username = ?, bio = ?
            WHERE email = ?
        """, (username, bio, email))

        conn.commit()

    # GET DATA
    c.execute("""
        SELECT username, email, bio
        FROM users
        WHERE email = ?
    """, (email,))

    user = c.fetchone()
    conn.close()

    return render_template(
        "profile.html",
        username=user[0],
        email=user[1],
        bio=user[2]
    )

# ---------------- RESET STEP 1 ----------------
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE email=? AND username=?",
            (email, username)
        )
        user = c.fetchone()
        conn.close()

        if user:
            session["reset_user"] = email
            return redirect(url_for("newpassword"))
        else:
            return render_template(
                "resetpassword.html",
                error="Invalid username or email"
            )

    return render_template("resetpassword.html")
# ---------------- RESET STEP 2 ----------------
@app.route("/newpassword", methods=["GET", "POST"])
def newpassword():
    if "reset_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form["password"]
        repeat = request.form["repeat-password"]

        # ❗后端 validation
        if not password:
            return render_template("newpassword.html", error="Password is required")

        if len(password) < 8:
            return render_template("newpassword.html", error="Password must be at least 8 characters")

        if password != repeat:
            return render_template("newpassword.html", error="Passwords do not match")

        hashed_pw = generate_password_hash(password)
        email = session["reset_user"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
        conn.commit()
        conn.close()

        session.pop("reset_user", None)

        return redirect(url_for("login"))

    return render_template("newpassword.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

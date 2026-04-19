from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey123"

# =======================
# BASE PATH (IMPORTANT FIX)
# =======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        username TEXT,
        password TEXT,
        bio TEXT,
        profile_pic TEXT
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
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            return render_template("register.html", error="All fields required")

        hashed_pw = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("""
                INSERT INTO users (email, username, password, bio)
                VALUES (?, ?, ?, ?)
            """, (email, username, hashed_pw, ""))

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template("register.html", error="This email is already registered!")

    return render_template("register.html")


# ---------------- CHECK EMAIL ----------------
@app.route("/check-email")
def check_email():
    email = request.args.get("email")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    conn.close()

    return {"exists": user is not None}


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = email
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------------- PROFILE ----------------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        bio = request.form["bio"]

        c.execute("""
            UPDATE users
            SET username = ?, bio = ?
            WHERE email = ?
        """, (username, bio, email))

        conn.commit()

    c.execute("""
    SELECT username, email, bio, profile_pic
    FROM users
    WHERE email = ?
    """, (email,))

    user = c.fetchone()
    conn.close()

    if not user:
        session.pop("user", None)
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        username=user[0],
        email=user[1],
        bio=user[2],
        profile_pic=user[3]
    )



# ---------------- UPLOAD PROFILE PIC ----------------
@app.route("/upload-profile-pic", methods=["POST"])
def upload_profile_pic():
    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files.get("image")

    if file and file.filename != "":
        filename = secure_filename(file.filename)

        email = session["user"]
        ext = filename.rsplit(".", 1)[-1]

        new_filename = f"{email}.{ext}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

        file.save(filepath)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            UPDATE users
            SET profile_pic = ?
            WHERE email = ?
        """, (new_filename, email))

        conn.commit()
        conn.close()

    return redirect(url_for("profile"))


# ---------------- RESET STEP 1 ----------------
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE email=? AND username=?
        """, (email, username))

        user = c.fetchone()
        conn.close()

        if user:
            session["reset_user"] = email
            return redirect(url_for("newpassword"))
        else:
            return render_template("resetpassword.html", error="Invalid username or email")

    return render_template("resetpassword.html")


# ---------------- RESET STEP 2 ----------------
@app.route("/newpassword", methods=["GET", "POST"])
def newpassword():
    if "reset_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form["password"]
        repeat = request.form["repeat-password"]

        if not password:
            return render_template("newpassword.html", error="Password is required")

        if len(password) < 8:
            return render_template("newpassword.html", error="Password must be at least 8 characters")

        if password != repeat:
            return render_template("newpassword.html", error="Passwords do not match")

        hashed_pw = generate_password_hash(password)
        email = session["reset_user"]

        conn = sqlite3.connect(DB_PATH)
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

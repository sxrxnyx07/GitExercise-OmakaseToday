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
        profile_pic TEXT,
        role TEXT DEFAULT 'user'
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
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
            session["role"] = user[5]
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
        profile_pic=user[3],
        role=session.get("role")
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
# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "403 Forbidden"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # recent users
    c.execute("SELECT email, username, role FROM users ORDER BY rowid DESC LIMIT 5")
    recent_users = c.fetchall()

    # recent recipes (如果你还没 table，我先给你结构)
    c.execute("SELECT title FROM recipes ORDER BY rowid DESC LIMIT 5")
    recent_recipes = c.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        recent_users=recent_users,
        recent_recipes=recent_recipes
    )

# =======================
# CREATE ADMIN (RUN ONCE ONLY)
# =======================
@app.route("/create-admin")
def create_admin():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    hashed_pw = generate_password_hash("admin123")

    c.execute("""
        INSERT OR IGNORE INTO users (email, username, password, bio, profile_pic, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("admin@test.com", "admin", hashed_pw, "", "", "admin"))

    conn.commit()
    conn.close()

    return "Admin created successfully!"

@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        return "403 Forbidden"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT email, username, role FROM users")
    users = c.fetchall()

    conn.close()

    return render_template("admin_users.html", users=users)
@app.route("/admin/delete/<email>")
def delete_user(email):
    if session.get("role") != "admin":
        return "403 Forbidden"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE email = ?", (email,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_users"))

@app.route("/admin/recipes")
def admin_recipes():
    if session.get("role") != "admin":
        return "403 Forbidden"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, title FROM recipes ORDER BY id DESC")
    recipes = c.fetchall()

    conn.close()

    return render_template("admin_recipes.html", recipes=recipes)

@app.route("/admin/recipes/add", methods=["POST"])
def add_recipe():
    if session.get("role") != "admin":
        return "403 Forbidden"

    title = request.form["title"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("INSERT INTO recipes (title) VALUES (?)", (title,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_recipes"))

@app.route("/admin/recipes/delete/<int:id>")
def delete_recipe(id):
    if session.get("role") != "admin":
        return "403 Forbidden"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM recipes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_recipes"))

@app.route("/seed-recipes")
def seed_recipes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    recipes = [
        ("Nasi Lemak"),
        ("Chicken Rice"),
        ("Fried Noodles"),
        ("Laksa"),
        ("Roti Canai")
    ]

    c.executemany("INSERT INTO recipes (title) VALUES (?)",
                  [(r,) for r in recipes])

    conn.commit()
    conn.close()

    return "Recipes added!"


if __name__ == "__main__":
    app.run(debug=True)

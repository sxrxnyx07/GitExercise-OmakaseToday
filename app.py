from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer   #Generate a secure password reset link  (token)
from flask_mail import Mail, Message              #Send the reset link to the user  (msg)
import secrets

app = Flask(__name__)
app.secret_key = "secretkey123"   #Used for encryption: session (login state) token (reset password)

# =======================
# EMAIL CONFIG
# =======================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'                #Gmail servers
app.config['MAIL_PORT'] = 587                               #Standard email port
app.config['MAIL_USE_TLS'] = True                           #Enable encrypted transmission
app.config['MAIL_USERNAME'] = 'xinfeic195@gmail.com'        #admin(my) gmail acc
app.config['MAIL_PASSWORD'] = 'jloc xdjj rcfe hufe'         #add password

mail = Mail(app)                                            #Initialize the email system

# Token serializer
s = URLSafeTimedSerializer(app.secret_key)                  #Create an "encryption tool" to encrypt data using your secret_key.

def generate_token(email):                                  #Turn email into a security token
    return s.dumps(email, salt='password-reset')

def verify_token(token):                                    #Decrypt the token back to email
    try:
        email = s.loads(token, salt='password-reset', max_age=300) #check Has the token been modified? Has the token expired (300 seconds = 5 minutes)?
        return email
    except:
        return None
# =======================
# Database path
# =======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     #Locate the current file path
DB_PATH = os.path.join(BASE_DIR, "users.db")              #create the location for users.db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'omakase.db')   #store recipe table and name/image/rating...
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =======================
# Recipe dataset (from Saranya)
# =======================
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) 
    image = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    clean_ingredients = db.Column(db.Text) 
    full_ingredients = db.Column(db.Text)  
    directions = db.Column(db.Text)        
    timing = db.Column(db.String(100))     
    meal_category = db.Column(db.String(50))
    flavor_type = db.Column(db.String(50))

# =======================
# Static resource configuration
# =======================
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")   #the img will store in static/uploads inside the folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)                     #auto createonce the file not exist

# ---------------- User table(users.db) ----------------
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
    CREATE TABLE IF NOT EXISTS saved_recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        user_email TEXT,
        recipe_id INTEGER
    )
    """)
    #id = the save record number (system-generated log ID)
    #user_email = who saved it
    #recipe_id = what recipe was saved
    conn.commit()
    conn.close()
init_db()

def add_reset_columns():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try: #To prevent others from creating unauthorized links
        c.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    except:
        pass

    try: #Preventing the same link from being reused (one-time use), 0 = Not used (valid) used == 1(invalid)
        c.execute("ALTER TABLE users ADD COLUMN reset_used INTEGER DEFAULT 0")
    except:
        pass
    try: #Reserved for tracking whether users view the reset link (currently unused)
        c.execute("ALTER TABLE users ADD COLUMN reset_viewed INTEGER DEFAULT 0")
    except:
        pass
    conn.commit()
    conn.close()

add_reset_columns()
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

# ---------------- CHECK EMAIL ----------------(real-time validation using AJAX)
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
        user = c.fetchone()        #get a tuple, example:'test@email.com', 'anna', 'hashed_password', '', '', 'admin'

        conn.close()

        if user and check_password_hash(user[2], password):     #check id exist indb, check password
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

    # user info
    c.execute("""
        SELECT username, email, bio, profile_pic
        FROM users
        WHERE email = ?
    """, (email,))
    user = c.fetchone()

    # saved recipes
    c.execute("""
        SELECT recipe_id FROM saved_recipes
        WHERE user_email = ?
    """, (email,))
    saved_ids = [row[0] for row in c.fetchall()]
    conn.close()

    saved_recipes = Recipe.query.filter(Recipe.id.in_(saved_ids)).all() if saved_ids else []
    suggested_recipes = Recipe.query.limit(3).all()  #It automatically retrieves 3 recipes from the database to display

    return render_template(
        "profile.html",
        username=user[0],
        email=user[1],
        bio=user[2],
        profile_pic=user[3],
        saved_recipes=saved_recipes,
        suggested_recipes=suggested_recipes,
        saved_ids=saved_ids, 
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

        new_filename = f"{email}.{ext}"             #rename the file to useremail
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


# ---------------- RESET ----------------
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "POST":
        email = request.form["email"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))      #Check the database to see if this email exists
        user = c.fetchone()

        if user:
            #generate encrypted token
            token = generate_token(email)
            # store in database
            c.execute("""
                UPDATE users
                SET reset_token=?, reset_used=0
                WHERE email=?
            """, (token, email))
            conn.commit()
            #Generate a reset link
            reset_link = url_for("reset_with_token", token=token, _external=True)

            msg = Message(
                "Password Reset",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.html = f"""
            <h2>Password Reset</h2>

            <p>Hi {email},</p>

            <p>You requested to reset your password.</p>

            <p>
            Click the link below:
            <br>
            <a href="{reset_link}">Reset Password</a>
            </p>

            <p style="color:red;">This link will expire in 5 minutes.</p>

            <p>If you did not request this, please ignore.</p>

            <p>— Omakase Team</p>
            """
            mail.send(msg)

        conn.close()

        return render_template("resetpassword.html", error="If email exists, link sent.")

    return render_template("resetpassword.html")

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    # 1. check expiry (token validity + time limit)
    email_from_token = verify_token(token)
    if not email_from_token:
        return "Link expired (5 minutes)"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 2. Does the token exist in the database? Has it already been used (reset_used == 1)? Do the token and email match?
    c.execute("""                        
        SELECT email, reset_used
        FROM users
        WHERE reset_token=?
    """, (token,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "Invalid link"
    email, used = row
    # 3. check single-use FIRST
    if used == 1:
        conn.close()
        return "This link has already been used"
    # 4. security check (token must match email)
    if email != email_from_token:
        conn.close()
        return "Invalid link"
    # ---------------- GET ----------------
    if request.method == "GET":
        conn.close()
        return render_template("newpassword.html")
    # ---------------- POST ----------------
    password = request.form["password"]
    repeat = request.form["repeat-password"]

    if not password:
        return render_template("newpassword.html", error="Password required")

    if len(password) < 8:
        return render_template("newpassword.html", error="Min 8 characters")

    if password != repeat:
        return render_template("newpassword.html", error="Passwords do not match")

    hashed_pw = generate_password_hash(password)
    # update password + mark token used + clear reset_token (no longer exists)
    c.execute("""
        UPDATE users
        SET password=?, reset_used=1, reset_token=NULL
        WHERE email=?
    """, (hashed_pw, email))
    conn.commit()
    conn.close()
    return redirect(url_for("login"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)             #clean user status
    return redirect(url_for("home"))

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "403 Forbidden"

    # 1. Get recent users (continue using sqlite3 to access users.db)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email, username, role FROM users ORDER BY rowid DESC LIMIT 5")   #sqlite
    recent_users = c.fetchall()
    conn.close()

    # 2. Gey recent recipes (continue using SQLAlchemy to access omakase.db)
    # This will prevent the "no such table: recipes" error.
    recent_recipes = Recipe.query.order_by(Recipe.id.desc()).limit(5).all()  #recipes(SQLAIchemy)

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

@app.route("/admin/users/update/<email>", methods=["POST"])
def update_user(email):
    if session.get("role") != "admin":
        return "403 Forbidden"

    role = request.form.get("role")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE users
        SET username = ?, role = ?
        WHERE email = ?
    """, (role, email))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_users"))

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
    recipes = Recipe.query.all()      #get recipes's data from datbase(omakase.db)
    return render_template("admin_recipes.html", recipes=recipes)

@app.route("/admin/recipes/add", methods=["POST"])
def add_recipe():
    name = request.form.get("name")
    rating = request.form.get("rating")
    clean = request.form.get("clean_ingredients")
    full = request.form.get("full_ingredients")
    directions = request.form.get("directions")
    timing = request.form.get("timing")
    category = request.form.get("meal_category")
    flavor = request.form.get("flavor_type")

    file = request.files.get("image_file")

    image_url = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)
        image_url = f"/static/uploads/{filename}"

    new_recipe = Recipe(
        name=name,
        rating=rating,
        image=image_url,
        clean_ingredients=clean,
        full_ingredients=full,
        directions=directions,
        timing=timing,
        meal_category=category,
        flavor_type=flavor
    )

    db.session.add(new_recipe)
    db.session.commit()

    return redirect("/admin/recipes")

@app.route("/admin/recipes/delete/<int:id>")
def delete_recipe(id):
    if session.get("role") != "admin":
        return "403 Forbidden"

    recipe_to_delete = Recipe.query.get(id)
    if recipe_to_delete:
        db.session.delete(recipe_to_delete)
        db.session.commit()

    return redirect(url_for("admin_recipes"))

@app.route("/admin/recipes/update/<int:id>", methods=["POST"])
def update_recipe(id):
    if session.get("role") != "admin":
        return "403 Forbidden"

    recipe = Recipe.query.get(id)

    if recipe:
        recipe.name = request.form.get("name")
        recipe.rating = request.form.get("rating")
        recipe.clean_ingredients = request.form.get("clean_ingredients")
        recipe.full_ingredients = request.form.get("full_ingredients")
        recipe.directions = request.form.get("directions")
        recipe.timing = request.form.get("timing")
        recipe.meal_category = request.form.get("meal_category")
        recipe.flavor_type = request.form.get("flavor_type")

        file = request.files.get("image_file")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            recipe.image = f"/static/uploads/{filename}"

        db.session.commit()

    return redirect(url_for("admin_recipes"))

@app.route("/save-recipe/<int:recipe_id>")
def save_recipe(recipe_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    #Prevent repeated save
    c.execute("SELECT 1 FROM saved_recipes WHERE user_email=? AND recipe_id=?",
              (session["user"], recipe_id))
    #insert new record
    if not c.fetchone():
        c.execute("INSERT INTO saved_recipes (user_email, recipe_id) VALUES (?,?)",
                  (session["user"], recipe_id))
    conn.commit()
    conn.close()
    return "OK"

@app.route("/unsave-recipe/<int:recipe_id>")
def unsave_recipe(recipe_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM saved_recipes WHERE user_email=? AND recipe_id=?",
              (session["user"], recipe_id))

    conn.commit()
    conn.close()

    return redirect(request.referrer)

@app.route("/saved-recipes")
def saved_recipes():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT recipe_id FROM saved_recipes
        WHERE user_email = ?
    """, (email,))

    saved_ids = [row[0] for row in c.fetchall()]
    conn.close()

    saved_recipes = Recipe.query.filter(Recipe.id.in_(saved_ids)).all() if saved_ids else []

    return render_template("saved_recipes.html", saved_recipes=saved_recipes)

if __name__ == "__main__":
    app.run(debug=True)

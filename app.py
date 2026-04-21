import os
import string
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey123"

# ---------------- DATABASE CONFIG (Recipe DB) ----------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'omakase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# ---------------- DATABASE INIT (User DB) ----------------
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



@app.route('/all_recipes')
def all_recipes():
    # 1. Get parameters from URL
    search_query = request.args.get('search', '').strip()
    active_flavor = request.args.get('flavor', 'ALL').strip() # Default to 'ALL'
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # 2. Start query
    query = Recipe.query

    # 3. Filter by Flavor (if not ALL)
    # Note: We capitalize the flavor to match 'Sour', 'Light', etc. in your DB
    if active_flavor != 'ALL':
        query = query.filter(Recipe.flavor_type == active_flavor.capitalize())

    # 4. Filter by Search (Name)
    if search_query:
        query = query.filter(Recipe.name.icontains(search_query))

    # 5. Execute Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'all_recipes.html',
        results=pagination.items,
        pagination=pagination,
        search_query=search_query,
        active_flavor=active_flavor # Pass this to highlight the active button
    )

# ---------------- YOUR INGREDIENT LOGIC ----------------

@app.route("/ingredient-search")  # Renamed so Friend's HOME works
def ingredient_index():
    all_recipes = Recipe.query.all()
    ingredients_dict = {char: [] for char in string.ascii_uppercase}
    all_names_flat = set()

    for r in all_recipes:
        if r.clean_ingredients:
            names = [i.strip().title() for i in str(r.clean_ingredients).split(',') if i.strip()]
            for name in names:
                if name:
                    first_letter = name[0].upper()
                    if first_letter in ingredients_dict:
                        if name not in ingredients_dict[first_letter]:
                            ingredients_dict[first_letter].append(name)
                            all_names_flat.add(name)

    active_ingredients = {k: v for k, v in ingredients_dict.items() if len(v) > 0}
    for char in active_ingredients:
        active_ingredients[char].sort()
    
    alphabet = list(string.ascii_uppercase)
    sorted_flat_list = sorted(list(all_names_flat))

    return render_template("ingredient.html", 
                           ingredients=active_ingredients, 
                           all_ingredients=sorted_flat_list,
                           alphabet=alphabet)

@app.route('/search', methods=['POST'])
def search():
    selected_raw = request.form.get('ingredients')
    user_input = [s.strip().lower() for s in selected_raw.split(',')] if selected_raw else []
    results = []

    if user_input:
        all_recipes = Recipe.query.all()
        for recipe in all_recipes:
            clean_db_text = str(recipe.clean_ingredients).lower()
            if all(item in clean_db_text for item in user_input):
                clean_db_list = [i.strip() for i in str(recipe.clean_ingredients).split(',') if i.strip()]
                percent = int((len(user_input) / len(clean_db_list)) * 100) if clean_db_list else 0
                missing = [i for i in clean_db_list if not any(u in i.lower() for u in user_input)]
                results.append({
                    "id": recipe.id, "name": recipe.name, "image": recipe.image,
                    "rating": recipe.rating, "match": percent, "missing": missing[:5]
                })

    results = sorted(results, key=lambda x: x['match'], reverse=True)
    return render_template('result.html', results=results, selected=user_input)

# ---------------- FRIEND'S AUTH LOGIC ----------------

@app.route("/")
def home():
    return render_template("home.html")

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
                c.execute("INSERT INTO users (email, username, password, bio) VALUES (?, ?, ?, ?)", (email, username, hashed_pw, ""))
                conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="This email is already registered!")
    return render_template("register.html")

@app.route("/check-email")
def check_email():
    email = request.args.get("email")
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        user = c.fetchone()
    return {"exists": user is not None}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = c.fetchone()
        if user and check_password_hash(user[2], password):
            session["user"] = email
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session: return redirect(url_for("login"))
    email = session["user"]
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    if request.method == "POST":
        username, bio = request.form["username"], request.form["bio"]
        c.execute("UPDATE users SET username = ?, bio = ? WHERE email = ?", (username, bio, email))
        conn.commit()
    c.execute("SELECT username, email, bio FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return render_template("profile.html", username=user[0], email=user[1], bio=user[2])

@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "POST":
        username, email = request.form["username"], request.form["email"]
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND username=?", (email, username))
        user = c.fetchone()
        conn.close()
        if user:
            session["reset_user"] = email
            return redirect(url_for("newpassword"))
        else:
            return render_template("resetpassword.html", error="Invalid username or email")
    return render_template("resetpassword.html")

@app.route("/newpassword", methods=["GET", "POST"])
def newpassword():
    if "reset_user" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        password, repeat = request.form["password"], request.form["repeat-password"]
        if not password: return render_template("newpassword.html", error="Password is required")
        if len(password) < 8: return render_template("newpassword.html", error="Too short")
        if password != repeat: return render_template("newpassword.html", error="No match")
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

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
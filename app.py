from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import random

app = Flask(__name__)

recipes = {
    "breakfast": ["🥐Toast🥪", "🥚Egg🍳", "🍚Congee🍲", "🥗Salad🥒", "🧇Pancake🥞"],
    "lunch": ["🍛Rice🍚", "🍜Mihun🍜", "🍝Noodles🍝", "🍜Kuey Teow🍜", "🥟Wrap🌯"],
    "dinner": ["🥩Protein🍖", "🍲Soup🍲", "🥕Vegetables🥦", "🥟Staple🍚"],
    "dessert": ["🧁Cake🍰", "🍨Ice Cream🍦", "🍮Pudding🍮", "🍪Cookies🍪", "🥧Kuih🥮"],
    "drinks": ["☕Caffeine Series☕", "🍵Tea Series🍵", "🍈Fresh Juice🍉", "🍋‍🟩Sparkling Drinks🍹", "❄️Blended Drinks🧊"]
}

def get_db_connection():
    conn = sqlite3.connect('omakase.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/db-test')
def db_test():
    conn = get_db_connection()
    rows = conn.execute("SELECT name FROM recipes LIMIT 5").fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/random-page')
def random_page():
    return render_template('random.html')

@app.route('/breakfast')
def breakfast():
    conn = get_db_connection()

    recipes = conn.execute(
        "SELECT name, image FROM recipe WHERE meal_category = ?",
        ("Breakfast",)
    ).fetchall()

    conn.close()

    return render_template('breakfast.html', recipes=recipes)

@app.route('/lunch')
def lunch():
    conn = get_db_connection()

    recipes = conn.execute(
        "SELECT name, image FROM recipe WHERE meal_category = ?",
        ("Lunch",)
    ).fetchall()

    conn.close()
    return render_template('lunch.html', recipes=recipes)

@app.route('/dinner')
def dinner():
    conn = get_db_connection()

    recipes = conn.execute(
        "SELECT name, image FROM recipe WHERE meal_category = ?",
        ("Dinner",)
    ).fetchall()

    conn.close()
    return render_template('dinner.html', recipes=recipes)

@app.route('/dessert')
def dessert():
    conn = get_db_connection()

    recipes = conn.execute(
        "SELECT name, image FROM recipe WHERE meal_category = ?",
        ("Dessert",)
    ).fetchall()

    conn.close()
    return render_template('dessert.html', recipes=recipes)

@app.route('/drinks')
def drinks():
    conn = get_db_connection()

    recipes = conn.execute(
        "SELECT name, image FROM recipe WHERE meal_category = ?",
        ("Drinks",)
    ).fetchall()

    conn.close()
    return render_template('drinks.html', recipes=recipes)

@app.route('/random')
def get_random_recipe():

    category = request.args.get('category')

    if not category:
        return jsonify({"recipe": "No category provided"})

    conn = get_db_connection()

    recipe = conn.execute(
        "SELECT name FROM recipes WHERE category = ? ORDER BY RANDOM() LIMIT 1",
        (category,)
    ).fetchone()

    conn.close()

    if not recipe:
        return jsonify({"recipe": "No recipe found"})

    return app.response_class(
    response=json.dumps({"recipe": recipe["name"]}, ensure_ascii=False),
    mimetype='application/json'
)

if __name__ == '__main__':
    app.run(debug=True)
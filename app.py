from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

recipes = {
    "breakfast": ["🥐Toast🥪", "🥚Egg🍳", "🍚Congee🍲", "🥗Salad🥒", "🧇Pancake🥞"],
    "lunch": ["🍛Rice🍚", "🍜Mihun🍜", "🍝Noodles🍝", "🍜Kuey Teow🍜", "🥟Wrap🌯"],
    "dinner": ["🥩Protein🍖", "🍲Soup🍲", "🥕Vegetables🥦", "🥟Staple🍚"],
    "dessert": ["🧁Cake🍰", "🍨Ice Cream🍦", "🍮Pudding🍮", "🍪Cookies🍪", "🥧Kuih🥮"],
    "drinks": ["☕Caffeine Series☕", "🍵Tea Series🍵", "🍈Fresh Juice🍉", "🍋‍🟩Sparkling Drinks🍹", "❄️Blended Drinks🧊"]
}

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
    return render_template('breakfast.html')

@app.route('/lunch')
def lunch():
    return render_template('lunch.html')

@app.route('/dinner')
def dinner():
    return render_template('dinner.html')

@app.route('/dessert')
def dessert():
    return render_template('dessert.html')

@app.route('/drinks')
def drinks():
    return render_template('drinks.html')

@app.route('/random')
def get_random_recipe():

    category = request.args.get('category')

    if category in recipes:
        recipe = random.choice(recipes[category])
    else:
        recipe = "No recipe found"

    return jsonify({"recipe": recipe})

if __name__ == '__main__':
    app.run(debug=True)
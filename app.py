from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

recipes = ["Pancake", "Spaghetti", "Fried Rice", "Chicken Rice"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/random-page')
def random_page():
    return render_template('random.html')

@app.route('/random')
def get_random_recipe():
    return jsonify({
        "recipe": random.choice(recipes)
    })

if __name__ == '__main__':
    app.run(debug=True)
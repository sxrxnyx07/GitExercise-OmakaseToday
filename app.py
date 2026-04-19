import os
import string
from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


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

@app.route("/")
def home():
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
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image,
                    "rating": recipe.rating,
                    "match": percent,
                    "missing": missing[:5]
                })

    results = sorted(results, key=lambda x: x['match'], reverse=True)
    return render_template('result.html', results=results, selected=user_input)

if __name__ == "__main__":
    app.run(debug=True)
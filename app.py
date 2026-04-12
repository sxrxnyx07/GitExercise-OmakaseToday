from flask import Flask, render_template, request
import string

app = Flask(__name__)

# ---------------- INGREDIENTS ----------------
ingredients = {
    "A": ["apple", "avocado"],
    "B": ["banana", "beef", "butter"],
    "C": ["carrot", "chicken", "chili"],
    "D": ["dried chili"],
    "E": ["egg", "evaporated milk"],
    "F": ["fish", "fish sauce", "flour"],
    "G": ["garlic", "ginger"],
    "H": ["honey"],
    "J": ["jackfruit"],
    "K": ["kidney beans"],
    "L": ["lamb" , "lemon", "lime"],
    "M": ["milk", "mushroom", "mango"],
    "N": ["noodles"],
    "O": ["onion", "oyster sauce"],
    "P": ["prawn", "potato"],
    "R": ["rice"],
    "S": ["salt", "sugar", "soy sauce"],
    "T": ["tomato", "tofu", "turmeric"],
    "V": ["vanilla extract" , "vinegar"],
    "W": ["watermelon"],
    "Y": ["yogurt"]
    
}

# ---------------- RECIPES ----------------
recipes = [

    {
        "name": "Turmeric Garlic Chicken",
        "image": "tur_chick.jpg",
        "ingredients": ["chicken", "turmeric", "garlic", "onion", "salt"]
    },
    {
        "name": "Honey Ginger Chicken",
        "image": "honey_chick.jpg",
        "ingredients": ["chicken", "honey", "ginger", "soy sauce", "butter"]
    },
    {
        "name": "Spicy Chicken & Carrot Stir-fry",
        "image": "spicy_chick.jpg",
        "ingredients": ["chicken", "carrot", "chili", "garlic", "oyster sauce"]
    },

    {
        "name": "Beef & Onion Udon",
        "image": "beef_udon.jpg",
        "ingredients": ["beef", "onion", "noodles", "oyster sauce", "garlic"]
    },
    {
        "name": "Dried Chili Beef",
        "image": "dried_beef.jpg",
        "ingredients": ["beef", "dried chili", "ginger", "soy sauce", "sugar"]
    },
    {
        "name": "Beef & Mushroom Broth",
        "image": "beef_mush.jpg",
        "ingredients": ["beef", "mushroom", "onion", "garlic", "salt"]
    },

    {
        "name": "Garlic Butter Prawns",
        "image": "garlic_prawn.jpg",
        "ingredients": ["prawn", "butter", "garlic", "salt", "lemon"]
    },
    {
        "name": "Spicy Prawn Rice",
        "image": "prawn_rice.jpg",
        "ingredients": ["prawn", "rice", "chili", "soy sauce", "egg"]
    },

    {
        "name": "Lamb & Potato Stew",
        "image": "lamb_potato.jpg",
        "ingredients": ["lamb", "potato", "tomato", "onion", "garlic"]
    },
    {
        "name": "Zesty Lime Lamb",
        "image": "zesty_lamb.jpg",
        "ingredients": ["lamb", "lime", "honey", "ginger", "salt"]
    },

    {
        "name": "Ginger Fish Fillet",
        "image": "ginger_fish.jpg",
        "ingredients": ["fish", "ginger", "soy sauce", "onion", "sugar"]
    },
    {
        "name": "Crispy Fried Fish",
        "image": "crispy_fish.jpg",
        "ingredients": ["fish", "flour", "turmeric", "salt", "garlic"]
    },

    {
        "name": "Tomato & Egg Scramble",
        "image": "tomato_egg.jpg",
        "ingredients": ["tomato", "egg", "onion", "salt", "butter"]
    },
    {
        "name": "Mushroom & Tofu Stir-fry",
        "image": "mush_tofu.jpg",
        "ingredients": ["mushroom", "tofu", "garlic", "oyster sauce", "chili"]
    },
    {
        "name": "Avocado & Tomato Salad",
        "image": "avo_tomato.jpg",
        "ingredients": ["avocado", "tomato", "onion", "lime", "salt"]
    },
    {
        "name": "Creamy Carrot & Potato Mash",
        "image": "carr_potato.jpg",
        "ingredients": ["carrot", "potato", "evaporated milk", "butter", "salt"]
    },
    {
        "name": "Mango Yogurt Bowl",
        "image": "mango_yogurt.jpg",
        "ingredients": ["mango", "yogurt", "honey", "banana"]
    },
    {
        "name": "Sweet Jackfruit Rice",
        "image": "jack_rice.jpg",
        "ingredients": ["jackfruit", "rice", "evaporated milk", "sugar", "pandan leaf"]
    },
    {
        "name": "Watermelon & Lime Refresher",
        "image": "water_lime.jpg",
        "ingredients": ["watermelon", "lime", "honey"]
    }
]
# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    alphabet = list(string.ascii_uppercase)

    return render_template(
        "index.html",
        ingredients=ingredients,
        alphabet=alphabet,
        all_ingredients=[i for v in ingredients.values() for i in v]
    )

# ---------------- RESULT PAGE ----------------
@app.route("/result", methods=["POST"])
def result():
    data = request.form.get("ingredients")
    
    selected = []
    if data:
        # Clean up the input into a list of lowercase ingredients
        selected = [i.strip().lower() for i in data.split(",") if i.strip()]

    results = []

    for recipe in recipes:
        recipe_ingredients = [i.lower() for i in recipe["ingredients"]]
        
        # STRICT "AND" LOGIC: 
        # Only show the recipe if EVERY selected item is in the recipe_ingredients
        if all(item in recipe_ingredients for item in selected):
            missing = [i for i in recipe_ingredients if i not in selected]
            
            # Calculate match based on how many you have vs how many are required
            match_percent = int((len(selected) / len(recipe_ingredients)) * 100) if recipe_ingredients else 0

            results.append({
                "name": recipe["name"],
                "image": recipe.get("image", "default.jpg"),
                "match": match_percent,
                "missing": missing
            })

    results.sort(key=lambda x: x["match"], reverse=True)

    return render_template(
        "result.html",
        selected=selected,
        results=results
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
import sqlite3

conn = sqlite3.connect('omakase.db')
cursor = conn.cursor()

def auto_food_type(name):
    name = name.lower()

    #_____________BREAKFAST___________#

    # 🍞 Bread (Done)
    if "bread" in name:
        return "Bread"
    
    # 🥞 Crepes (Done)
    if "crepes" in name:
        return "Crepes"
    
    # 🥞 Oats (Done)
    if "oats" in name:
        return "Oats"
    
    # 🥞 Smoothie (Done)
    if "smoothie" in name:
        return "Smoothie"
    
    #  Cocktail (Done)
    if "cranberry-pomegranate mimosa" in name:
        return "Cocktail"
    
    #_____________LUNCH___________#

    #  Pastry (Done)
    if any(x in name for x in ["pastry", "simple strawberry salsa"]):
        return "Pastry"
    
    #  Fruit (Done)
    if any(x in name for x in ["salad", "baby food", "fruit"]):
        return "Fruit"
    
    #  Meat (Done)
    if any(x in name for x in ["pork", "lamb", "chicken", "tacos", "egg", "beef"]):
        return "Meat"
    
    #  Sides (Done)
    if "goat cheese" in name:
        return "Sides"
    
    #  Jam (Done)
    if any(x in name for x in ["preserves", "sauce", "jam", "butter"]):
        return "Jam"
    
    #  Beverage (Done)
    if any(x in name for x in ["coco (coconut ice)", "chamoyada"]):
        return "Beverage"
    
    #  Fruit (Done)
    if "fruit" in name:
        return "Fruit"
    
    #_____________Dinner___________#

    # 🐟 Seafood (Done)
    if any(x in name for x in ["salmon", "tuna", "fish", "shrimp", "lobster"]):
        return "Seafood"
    
    #  Meat (Done)
    if any(x in name for x in ["pork", "lamb", "chicken", "bacon", "meatloaf", "meat", "ham"]):
        return "Meat"
    
    #  Toast (Done)
    if any(x in name for x in ["toast", "sandwich"]):
        return "Toast"
    
    # 🍚 Main Dishes (Done)
    if any(x in name for x in ["risotto", "grilled tilapia"]):
        return "Main Dishes"
    
    #  Pizza (Done)
    if "pizza" in name:
        return "Pizza"
    
    #  Tacos (Done)
    if "tacos" in name:
        return "Tacos"
    
    #  Sauce (Done)
    if "sauce" in name:
        return "Sauce"
    
    #  Fruit (Done)
    if "mission figs" in name:
        return "Fruit"
    
    #_____________Dessert___________#

    #  Fruit (Done)
    if any(x in name for x in ["watermelon", "fruit", "nectarines"]):
        return "Fruit"

    #  Tart (Done)
    if any(x in name for x in ["tart", "tarts"]):
        return "Tart"
    
    #  Pie (Done)
    if any(x in name for x in ["pie", "bars"]):
        return "Pie"
    
    #  Cake (Done)
    if any(x in name for x in ["cake", "cheesecake", "cheesecakes"]):
        return "Cake"
    
    #_____________Drinks___________#

    #  Cocktail (Done)
    if "cocktail" in name:
        return "Cocktail"
    
    #  Refreshing (Done)
    if "flavored water" in name:
        return "Refreshing"
    
    #  Juice (Done)
    if any(x in name for x in ["mango", "pineapple", "cherry"]):
        return "Soother"
    
    #  Sparkling Drinks (Done)
    if "sangria" in name:
        return "Sparkling Drink"
    

    return "Other"


# 1️⃣ update all
cursor.execute("SELECT id, name FROM recipe")
rows = cursor.fetchall()

updated = 0

for (rid, name) in rows:
    food_type = auto_food_type(name)

    cursor.execute(
        "UPDATE recipe SET food_type = ? WHERE id = ?",
        (food_type, rid)
    )

    updated += 1


conn.commit()

print(f"DONE ✔ updated {updated} recipes")


# 2️⃣ check result BEFORE closing
cursor.execute("SELECT name, food_type FROM recipe LIMIT 20")
for row in cursor.fetchall():
    print(row)


# 3️⃣ check missing
cursor.execute("""
SELECT name FROM recipe 
WHERE food_type IS NULL OR food_type = 'Other'
""")

rows = cursor.fetchall()

print("❗ NEED MANUAL CHECK:")
for r in rows:
    print(r[0])

conn.close()
import pandas as pd
from app import app, db, Recipe

# 1. Load the data
df = pd.read_csv('recipes.csv')

# 2. Filter out duplicates from the CSV file itself
# This ensures "Apple Pie" only stays in the list once.
df_clean = df.drop_duplicates(subset=['recipe_name'])

with app.app_context():
    # 3. CRITICAL: This wipes the old database so no "ghost" data remains
    db.drop_all()   
    db.create_all() 
    
    print(f"Starting fresh import of {len(df_clean.head(50))} unique recipes...")
    
    # 4. Import the first 50 UNIQUE recipes
    for index, row in df_clean.head(1000).iterrows():
        new_recipe = Recipe(
            name=row['recipe_name'], 
            ingredients_list=str(row['ingredients']), 
            flavor="General",
            image=row['img_src'] # Direct link for pictures
        )
        db.session.add(new_recipe)
    
    db.session.commit()
    print("Done! Everything is unique now.")
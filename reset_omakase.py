import pandas as pd
from app import db, Recipe, app

def reset_db():
    with app.app_context():
        print("--- DATABASE RESET START ---")
        db.drop_all()
        db.create_all()
        

        target_file = 'master_recipes.csv' 
        
        try:
            df = pd.read_csv(target_file)
            print(f"✅ Found {target_file}. Importing {len(df)} recipes...")
            
            for index, row in df.iterrows():
                new_recipe = Recipe(
                    name=row['recipe_name'],
                    image=row['img_src'],
                    clean_ingredients=row['simple_ingredients'],
                    full_ingredients=row['ingredients'],
                    directions=row['directions'],
                    timing=row['timing'],
                    meal_category=row['meal_category'],
                    flavor_type=row['flavor_type']
                )
                db.session.add(new_recipe)
            
            db.session.commit()
            print(f"🎉 SUCCESS! Your database is now ready.")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    reset_db()
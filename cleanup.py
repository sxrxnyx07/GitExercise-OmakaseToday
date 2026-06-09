from app import app, db, Recipe
import sqlite3

def clean_database():
    with app.app_context():
        print("Memulakan pembersihan database...")
        
       
        distinct_ids_query = db.session.query(db.func.min(Recipe.id)).group_by(db.func.lower(db.func.trim(Recipe.name)))
        distinct_ids = [r[0] for r in distinct_ids_query.all()]

        
        num_deleted = Recipe.query.filter(~Recipe.id.in_(distinct_ids)).delete(synchronize_session=False)
        
        db.session.commit()
        print(f"Selesai! {num_deleted} rekod duplicate telah dibuang.")

if __name__ == "__main__":
    clean_database()
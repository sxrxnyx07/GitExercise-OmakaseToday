import sqlite3


conn = sqlite3.connect('omakase.db')
cursor = conn.cursor()

print("Connecting to omakase.db...")


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
print("Users table checked/created.")


cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        recipe_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes ("no."),
        UNIQUE(user_id, recipe_id)
    )
''')
print("Favorites table checked/created.")

conn.commit()
conn.close()
print("Done! Your omakase.db is now updated.")
import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

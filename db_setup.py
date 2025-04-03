import sqlite3

# Conectar ao banco logs.db
conn = sqlite3.connect('/home/pi/Documents/rasp/teste/logs.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user TEXT NOT NULL,
        action TEXT NOT NULL
    )
""")

conn.commit()
conn.close()

print("Banco de dados e tabela 'logs' criados com sucesso!")

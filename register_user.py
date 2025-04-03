import RPi.GPIO as GPIO
import sqlite3
import requests
from mfrc522 import SimpleMFRC522
from datetime import datetime

reader = SimpleMFRC522()

def connect_db():
    return sqlite3.connect('/home/pi/Documents/rasp/teste/logs.db')


def create_logs_table():
    with connect_db() as conn:
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

create_logs_table()  

def get_user_by_tag(tag_id):
    with sqlite3.connect('/home/pi/Documents/rasp/teste/users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE tag_id = ?", (tag_id,))
        user = cursor.fetchone()
        return user[0] if user else None

# Salvar log no banco SQLite
def save_log(user, action):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (timestamp, user, action) VALUES (?, ?, ?)",
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, action))
        conn.commit()


def send_log(user, action):
    data = {"user": user, "action": action}
    try:
        response = requests.post('http://localhost:8080/log', json=data)
        print(response.json())
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

try:
    while True:
        print("Aproxime a tag RFID...")
        tag_id, _ = reader.read()
        tag_id = str(tag_id)

        user = get_user_by_tag(tag_id)
        if user:
            print(f"✅ Acesso concedido para {user} (Tag: {tag_id})")
            save_log(user, "Access Granted")  
            send_log(user, "Access Granted")  
        else:
            print(f"❌ Acesso negado para a tag {tag_id}")
            save_log("Usuário desconhecido", "Access Denied")  
            send_log("Usuário desconhecido", "Access Denied")  

except KeyboardInterrupt:
    GPIO.cleanup()

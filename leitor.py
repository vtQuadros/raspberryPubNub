import RPi.GPIO as GPIO
import time
import requests
import sqlite3
from mfrc522 import SimpleMFRC522  


reader = SimpleMFRC522()


DB_PATH = '/home/pi/Documents/rasp/teste/users.db'


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_users_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL
            )
        """)
        conn.commit()

create_users_table()  


def get_user_by_tag(tag_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE tag_id = ?", (tag_id,))
        user = cursor.fetchone()
        return user[0] if user else None  


def send_log(user, action):
    data = {"user": user, "action": action}
    try:
        response = requests.post('http://localhost:8080/log', json=data)
        print(response.json())  
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

print("Aproxime o cartão RFID...")

try:
    while True:
        tag_id, _ = reader.read()  
        tag_id = str(tag_id).strip()  

        print(f"Tag lida: {tag_id}")  
        
        user = get_user_by_tag(tag_id)  
        if user:
            print(f"✅ Acesso permitido para {user} (Tag: {tag_id})")
            send_log(user, "Access Granted")  
        else:
            print(f"❌ Acesso negado para a tag {tag_id}")
            send_log("Usuário desconhecido", "Access Denied")

        time.sleep(2)  

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Leitor RFID encerrado.")

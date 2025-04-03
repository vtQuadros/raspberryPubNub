import RPi.GPIO as GPIO
import sqlite3
import requests
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

def get_user_by_tag(tag_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE tag_id = ?", (tag_id,))
        user = cursor.fetchone()
        return user[0] if user else None

# Enviar dados ao backend
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
            send_log(user, "Access Granted")
        else:
            send_log("Usuário desconhecido", "Access Denied")

except KeyboardInterrupt:
    GPIO.cleanup()

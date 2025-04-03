import RPi.GPIO as GPIO
import time
import requests
import sqlite3
from mfrc522 import SimpleMFRC522  # Biblioteca para ler RFID

# Inicializa o leitor RFID
reader = SimpleMFRC522()

# Caminho do banco de dados
DB_PATH = '/home/pi/Documents/rasp/teste/users.db'

# Conexão com o banco de dados local
def connect_db():
    return sqlite3.connect(DB_PATH)

# Criar tabela de usuários se não existir
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

create_users_table()  # Garante que a tabela existe

# Função para buscar o usuário pelo ID da tag RFID
def get_user_by_tag(tag_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE tag_id = ?", (tag_id,))
        user = cursor.fetchone()
        return user[0] if user else None  # Retorna o nome do usuário ou None

# Função para enviar dados ao backend
def send_log(user, action):
    data = {"user": user, "action": action}
    try:
        response = requests.post('http://localhost:8080/log', json=data)
        print(response.json())  # Mostra resposta do servidor
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

print("Aproxime o cartão RFID...")

try:
    while True:
        tag_id, _ = reader.read()  # Lê a tag RFID
        tag_id = str(tag_id).strip()  # Converte ID para string e remove espaços extras

        print(f"Tag lida: {tag_id}")  # DEBUG: Mostra qual ID foi lido
        
        user = get_user_by_tag(tag_id)  # Busca usuário no banco de dados
        if user:
            print(f"✅ Acesso permitido para {user} (Tag: {tag_id})")
            send_log(user, "Access Granted")  # Envia o nome do usuário real
        else:
            print(f"❌ Acesso negado para a tag {tag_id}")
            send_log("Usuário desconhecido", "Access Denied")

        time.sleep(2)  # Evita múltiplas leituras seguidas

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Leitor RFID encerrado.")

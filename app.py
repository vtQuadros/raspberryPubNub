from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory


app = Flask(__name__)


pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-82152934-942c-4153-bd51-266dc746fc85"
pnconfig.subscribe_key = "sub-c-d731bd87-7ea3-4d11-81b7-d5f6a08f2edd"
pnconfig.uuid = "raspberry-client"
pnconfig.ssl = True

pubnub = PubNub(pnconfig)


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            print("Conectado ao PubNub!")

    def message(self, pubnub, message):
        print(f"Mensagem recebida: {message.message}")

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(["teste"]).execute()


@app.route('/')
def serve_home():
    return send_from_directory(os.path.dirname(__file__), "index.html")


def connect_db():
    return sqlite3.connect('access_logs.db')


def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

create_table()


def publish_log(user, action):
    pubnub.publish().channel("teste").message({"user": user, "action": action}).sync()


@app.route('/log', methods=['POST'])
def log_access():
    data = request.json
    user = data.get('user')
    action = data.get('action')
    
    if not user or not action:
        return jsonify({"error": "Dados insuficientes"}), 400
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user, action) VALUES (?, ?)", (user, action))
        conn.commit()
    
    publish_log(user, action) 
    
    return jsonify({"message": "Log registrado com sucesso"}), 201


@app.route('/logs', methods=['GET'])
def get_logs():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()
    
    return jsonify([{ "id": row[0], "user": row[1], "action": row[2], "timestamp": row[3]} for row in rows])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

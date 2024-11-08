from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from openai import OpenAI
import sqlite3

app = Flask(__name__)

# Configurez votre clé API OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Connexion à la base de données SQLite
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            incoming_message TEXT,
            response_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    phone_number = request.values.get("From", "")
    resp = MessagingResponse()

    try:
        # Appel à l'API OpenAI pour obtenir une réponse de ChatGPT
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        chat_response = chat_completion.choices[0].message.content  # Correction ici
        
        # Enregistrement du message et de la réponse dans la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (phone_number, incoming_message, response_message)
            VALUES (?, ?, ?)
        ''', (phone_number, incoming_msg, chat_response))
        conn.commit()
        conn.close()

    except Exception as e:
        print("Erreur lors de l'appel à OpenAI:", str(e))
        chat_response = "Erreur lors de la génération de la réponse."

    msg = resp.message(chat_response)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)

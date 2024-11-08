from flask import Flask, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Chargement des clés API à partir des variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Configuration de la base de données SQLite pour stocker les messages
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              numero TEXT,
              message TEXT,
              reponse TEXT)''')
conn.commit()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")
    resp = MessagingResponse()

    try:
        # Appel à l'API OpenAI avec la bonne méthode
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": incoming_msg}
            ]
        )
        chat_response = response['choices'][0]['message']['content']
    except Exception as e:
        print("Erreur lors de l'appel à OpenAI:", str(e))
        chat_response = "Erreur lors de la génération de la réponse."

    # Enregistrement du message et de la réponse dans la base de données
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (date, numero, message, reponse) VALUES (?, ?, ?, ?)",
              (date_now, from_number, incoming_msg, chat_response))
    conn.commit()

    # Réponse de Twilio
    msg = resp.message(chat_response)
    return str(resp)

@app.route("/admin", methods=["GET"])
def admin():
    c.execute("SELECT date, numero, message, reponse FROM messages ORDER BY id DESC LIMIT 30")
    messages = c.fetchall()
    return render_template("admin.html", messages=messages)

if __name__ == "__main__":
    app.run(port=5000)

from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
import openai
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"  # Remplace par ta clé OpenAI, ou utilise une variable d’environnement

# Connexion à la base de données SQLite (elle sera créée si elle n'existe pas)
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Création de la table des messages si elle n'existe pas encore
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        number TEXT,
        message TEXT,
        response TEXT
    )
''')
conn.commit()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    sender_number = request.values.get("From", "")
    resp = MessagingResponse()

    try:
        # Appel à l'API OpenAI pour obtenir une réponse de ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        chat_response = response.choices[0].message['content']
    except Exception as e:
        print("Erreur lors de l'appel à OpenAI:", str(e))
        chat_response = "Erreur lors de la génération de la réponse."

    # Enregistre le message et la réponse dans la base de données
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (timestamp, number, message, response) VALUES (?, ?, ?, ?)",
              (timestamp, sender_number, incoming_msg, chat_response))
    conn.commit()

    # Envoie la réponse au client
    msg = resp.message(chat_response)
    return str(resp)

@app.route("/admin")
def admin():
    # Récupère les 30 derniers messages pour les afficher dans l'interface
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
    messages = c.fetchall()
    return render_template("admin.html", messages=messages)

if __name__ == "__main__":
    app.run(port=5000)

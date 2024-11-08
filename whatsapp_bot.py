from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

# Récupère les clés API des variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurer l'API OpenAI
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    resp = MessagingResponse()

    try:
        # Appel à l'API OpenAI pour obtenir une réponse de ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        chat_response = response.choices[0].message['content']
    except Exception as e:
        print("Erreur lors de l'appel à OpenAI:", str(e))
        chat_response = "Erreur lors de la génération de la réponse."

    msg = resp.message(chat_response)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)

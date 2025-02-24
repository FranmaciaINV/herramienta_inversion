import os
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # Habilitamos CORS

# Cargar clave API desde variables de entorno
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

if not PERPLEXITY_API_KEY:
    raise ValueError("❌ ERROR: No se encontró la API Key de Perplexity. Asegúrate de configurarla en Render.")

def obtener_noticias_inmobiliarias():
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "Responde con 4 noticias sobre el mercado inmobiliario en España en formato JSON puro. Cada noticia debe incluir 'title', 'description' y 'url'."
            },
            {
                "role": "user",
                "content": "Proporciona 4 noticias recientes y relevantes sobre el mercado inmobiliario en España en formato JSON puro."
            }
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "search_recency_filter": "month"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Estado de la solicitud: {response.status_code}")
        print(f"Contenido de respuesta (RAW): {response.text}")

        if response.status_code == 200:
            data = response.json()
            noticias = []

            for choice in data.get("choices", []):
                content = choice.get("message", {}).get("content", "").strip()
                
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()

                try:
                    noticias_json = json.loads(content)
                    if isinstance(noticias_json, list):
                        noticias.extend(noticias_json)
                except json.JSONDecodeError as e:
                    print(f"Error al procesar JSON: {e}\nContenido fallido: {content}")

            return noticias[:4]  
        else:
            print(f"Error en la API: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error al solicitar noticias: {e}")
        return []

@app.route("/obtener-noticias", methods=["GET"])
def obtener_noticias():
    noticias = obtener_noticias_inmobiliarias()
    return jsonify(noticias)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

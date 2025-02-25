from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta del archivo donde guardaremos los emails en local
EMAILS_FILE = "scripts/emails_guardados.txt"

@app.route('/guardar-email-local', methods=["POST"])
def guardar_email_local():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email or "@" not in email:
            return jsonify({"error": "Email no válido"}), 400

        # Guardar en el archivo local
        with open(EMAILS_FILE, "a") as file:
            file.write(email + "\n")

        print(f"✅ Email guardado en local: {email}")
        return jsonify({"message": "Email guardado en local"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=6000)  # 🛠️ Puerto 6000 para diferenciarlo

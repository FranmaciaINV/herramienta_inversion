from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

app = Flask(__name__)
CORS(app)

# 📂 Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")  # Asegurar la ruta a /data/

# 📌 Cargar los datos desde los archivos CSV
try:
    BANCOS_FILE = os.path.join(DATA_DIR, "BancosEspaña.csv")
    TASADORAS_FILE = os.path.join(DATA_DIR, "TasadorasEspaña.csv")

    print(f"📂 Cargando bancos desde: {BANCOS_FILE}")
    print(f"📂 Cargando tasadoras desde: {TASADORAS_FILE}")

    bancos_data = pd.read_csv(BANCOS_FILE)
    tasadoras_data = pd.read_csv(TASADORAS_FILE)

    print("Bancos y tasadoras cargados correctamente")
except Exception as e:
    print(f"ERROR al cargar los archivos CSV: {e}")
    bancos_data = pd.DataFrame()  
    tasadoras_data = pd.DataFrame()

# 🚀 Ruta API para obtener datos de bancos y tasadoras
@app.route("/obtener-datos", methods=["GET"])
def obtener_datos():
    tipo = request.args.get("tipo", "bancos")
    if tipo == "bancos":
        if bancos_data.empty:
            return jsonify({"error": "No hay datos de bancos disponibles"}), 404
        return jsonify(bancos_data.to_dict(orient="records"))
    elif tipo == "tasadoras":
        if tasadoras_data.empty:
            return jsonify({"error": "No hay datos de tasadoras disponibles"}), 404
        return jsonify(tasadoras_data.to_dict(orient="records"))
    else:
        return jsonify({"error": "Tipo no válido"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
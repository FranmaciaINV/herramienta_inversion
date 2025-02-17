from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cargar los datos desde los archivos CSV
try:
    bancos_data = pd.read_csv(os.path.join(BASE_DIR, 'data', 'BancosEspaña.csv'))
    tasadoras_data = pd.read_csv(os.path.join(BASE_DIR, 'data', 'TasadorasEspaña.csv'))
except Exception as e:
    bancos_data = pd.DataFrame()  # Si hay un error, cargar un DataFrame vacío
    tasadoras_data = pd.DataFrame()
    print(f"Error al cargar los archivos CSV: {e}")

@app.route("/")
def home():
    return render_template("../tests/index.html")

@app.route("/obtener-datos", methods=["GET"])
def obtener_datos():
    tipo = request.args.get("tipo", "bancos")
    if tipo == "bancos":
        return bancos_data.to_json(orient="records")
    elif tipo == "tasadoras":
        return tasadoras_data.to_json(orient="records")
    else:
        return jsonify({"error": "Tipo no válido"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)

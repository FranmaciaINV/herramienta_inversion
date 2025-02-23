from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import os
import json

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
        
        # Convertir NaN en None (para que JSON lo entienda como null)
        bancos_data_clean = bancos_data.where(pd.notna(bancos_data), None)
        
        return jsonify(bancos_data_clean.to_dict(orient="records"))

        # 📌 Depuración: Ver los primeros registros en logs
        print("🔍 Datos de bancos que se enviarán:")
        print(json.dumps(bancos_limpios[:5], indent=2, ensure_ascii=False))  # Solo los primeros 5 registros

        return jsonify(bancos_limpios)

    elif tipo == "tasadoras":
        if tasadoras_data.empty:
            return jsonify({"error": "No hay datos de tasadoras disponibles"}), 404

        tasadoras_limpias = tasadoras_data.where(pd.notna(tasadoras_data), None).to_dict(orient="records")

        print("🔍 Datos de tasadoras que se enviarán:")
        print(json.dumps(tasadoras_limpias[:5], indent=2, ensure_ascii=False))

        return jsonify(tasadoras_limpias)

    else:
        return jsonify({"error": "Tipo no válido"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
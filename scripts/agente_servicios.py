from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Base path del proyecto
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Rutas absolutas a los archivos CSV
RUTA_LUZ = os.path.join(BASE_PATH, "../data/Compañia_Luz.csv")
RUTA_GAS = os.path.join(BASE_PATH, "../data/Compañia_Gas.csv")
RUTA_LUZYGAS = os.path.join(BASE_PATH, "../data/Compañia_LuzyGas.csv")


def leer_companias(tipo):
    """
    Lee las compañías según el tipo especificado (luz, gas, luzygas).
    """
    if tipo == "luz":
        ruta = RUTA_LUZ
    elif tipo == "gas":
        ruta = RUTA_GAS
    elif tipo == "luzygas":
        ruta = RUTA_LUZYGAS
    else:
        return []

    try:
        # Lee el archivo CSV
        df = pd.read_csv(ruta)
        # Renombrar columnas si es necesario
        df = df.rename(columns={"Compañia": "nombre", "Descripcion": "descripcion"})
        # Convierte a una lista de diccionarios
        return df[["nombre", "descripcion"]].to_dict(orient="records")
    except Exception as e:
        print(f"Error al leer el archivo {ruta}: {e}")
        return []


@app.route("/obtener-companias", methods=["GET"])
def obtener_companias():
    tipo = request.args.get("tipo")
    if not tipo:
        return jsonify({"error": "Debe especificar el tipo (luz, gas, luzygas)"}), 400

    datos = leer_companias(tipo)
    return jsonify(datos)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

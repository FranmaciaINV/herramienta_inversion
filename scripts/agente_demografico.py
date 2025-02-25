from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import openai
from dotenv import load_dotenv
import os

# Configurar la API Key de OpenAI

load_dotenv()  # Carga las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")  # Obtiene la clave

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Datos fijos para cada código postal
DATOS_MUNICIPIOS = {
    "28080": {
        "nombre": "Majadahonda",
        "demografia": {"2024": (73547, 64579, 8968), "2023": (72833, 64312, 8521)},
        "renta": {"persona": 22550, "hogar": 70529},
        "empleo": {"paro": 1910, "contratos": 1270}
    },
    "03065": {
        "nombre": "Elche",
        "demografia": {"2024": (242317, 209894, 32423), "2023": (238285, 208715, 29570)},
        "renta": {"persona": 11085, "hogar": 29648},
        "empleo": {"paro": 18612, "contratos": 4323}
    },
    "37085": {
        "nombre": "Carbajosa de la Sagrada",
        "demografia": {"2024": (7638, 7406, 232), "2023": (7553, 7320, 233)},
        "renta": {"persona": 13927, "hogar": 39348},
        "empleo": {"paro": 376, "contratos": 267}
    },
    "08019": {
        "nombre": "Barcelona",
        "demografia": {"2024": (1686208, 1272145, 414063), "2023": (1655956, 1271296, 384660)},
        "renta": {"persona": 18404, "hogar": 43991},
        "empleo": {"paro": 63045, "contratos": 67740}
    },
    "49275": {
        "nombre": "Zamora",
        "demografia": {"2024": (59553, 56449, 3054), "2023": (59362, 56716, 2646)},
        "renta": {"persona": 14117, "hogar": 30988},
        "empleo": {"paro": 3654, "contratos": 1279}
    },
    "30024": {
        "nombre": "Lorca",
        "demografia": {"2024": (97769, 76849, 20920), "2023": (97905, 76312, 21592)},
        "renta": {"persona": 10640, "hogar": 32974},
        "empleo": {"paro": 3686, "contratos": 5216}
    },
    "28079": {
        "nombre": "Madrid",
        "demografia": {"2024": (3422416, 2803330, 619086), "2023": (3340176, 2773935, 566241)},
        "renta": {"persona": 18632, "hogar": 46651},
        "empleo": {"paro": 137192, "contratos": 126825}
    },
    "48020": {
        "nombre": "Bilbao",
        "demografia": {"2024": (347342, 307156, 40186), "2023": (345235, 307921, 37314)},
        "renta": {"persona": 17870, "hogar": 40886},
        "empleo": {"paro": 21253, "contratos": 11936}
    },
    "13013": {
        "nombre": "Almagro",
        "demografia": {"2024": (9082, 8475, 607), "2023": (9003, 8476, 527)},
        "renta": {"persona": 11155, "hogar": 29145},
        "empleo": {"paro": 574, "contratos": 168}
    },
    "18087": {
        "nombre": "Granada",
        "demografia": {"2024": (233532, 210782, 22750), "2023": (232246, 211095, 21151)},
        "renta": {"persona": 14891, "hogar": 34339},
        "empleo": {"paro": 19831, "contratos": 9480}
    },
    "36038": {
        "nombre": "Pontevedra",
        "demografia": {"2024": (83106, 78578, 4528), "2023": (82592, 78548, 4044)},
        "renta": {"persona": 14460, "hogar": 34511},
        "empleo": {"paro": 4094, "contratos": 2068}
    }
}

# Función para calcular el porcentaje de extranjeros
def calcular_porcentaje(total, extranjeros):
    return (extranjeros / total) * 100 if total else 0

# Función para generar el resumen con los datos correctos
def generar_resumen(codigo_postal):
    if codigo_postal not in DATOS_MUNICIPIOS:
        return None  # No hay datos para este código postal

    datos = DATOS_MUNICIPIOS[codigo_postal]
    nombre = datos["nombre"]
    
    total_2024, espanoles_2024, extranjeros_2024 = datos["demografia"]["2024"]
    total_2023, espanoles_2023, extranjeros_2023 = datos["demografia"]["2023"]

    porcentaje_extranjeros_2024 = calcular_porcentaje(total_2024, extranjeros_2024)
    porcentaje_extranjeros_2023 = calcular_porcentaje(total_2023, extranjeros_2023)

    renta_persona = datos["renta"]["persona"]
    renta_hogar = datos["renta"]["hogar"]
    paro = datos["empleo"]["paro"]
    contratos = datos["empleo"]["contratos"]

    resumen = f"""
Resumen de los datos para el código postal {codigo_postal} ({nombre}):

    Demografía:
    - En 2024, la población total era de {total_2024:,} habitantes ({espanoles_2024:,} españoles y {extranjeros_2024:,} extranjeros, {porcentaje_extranjeros_2024:.2f}% extranjeros).
    - En 2023, la población total era de {total_2023:,} habitantes ({espanoles_2023:,} españoles y {extranjeros_2023:,} extranjeros, {porcentaje_extranjeros_2023:.2f}% extranjeros).

    Renta:
    - La renta media por persona en {codigo_postal} es de {renta_persona:,} €.
    - La renta neta media por hogar en 2022 fue de {renta_hogar:,} €.

    Empleo y Paro:
    - En 2022, hubo {paro:,} nuevas incorporaciones al paro.
    - En ese mismo año, se realizaron {contratos:,} nuevos contratos.
"""
    return resumen.strip()

# Endpoint para la consulta
@app.route("/consulta-demografica", methods=["POST"])
def consulta_demografica():
    try:
        data = request.get_json()
        codigo_postal = data.get("codigo_postal")

        if not codigo_postal:
            return jsonify({"error": "Debe proporcionar un código postal."}), 400

        # Generar resumen con los datos correctos
        resumen = generar_resumen(codigo_postal)
        if not resumen:
            return jsonify({"error": f"No se encontraron datos para el código postal {codigo_postal}."}), 404

        return jsonify({"respuesta_clara": resumen}), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar la consulta: {e}"}), 500

# Desactivar caché en Render
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)

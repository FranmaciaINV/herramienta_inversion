from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin 
import agente_demografico
import agente_reformas
import agente_rentabilidad
import newsletter_inmobiliaria
import broker_hipotecario
import agente_servicios
import agente_contratos
import os
import pandas as pd
import numpy as np
import requests
from flask import send_file
from flask import request


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../templates")

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTRATO_PERSONALIZADO = os.path.join(BASE_PATH, "../data/CONTRATO_PERSONALIZADO.docx")

app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})


# Verificación de la carpeta templates en Render
print("🔍 DEBUG: Verificando templates en Render...")
print("📂 Template folder path:", app.template_folder)

if os.path.exists(app.template_folder):
    print("La carpeta templates EXISTE.")
    print("Archivos en templates:", os.listdir(app.template_folder))
else:
    print("La carpeta templates NO existe.")

@app.route("/")
def home():
    return render_template("index.html")  # Renderiza el HTML desde templates/


# Ruta donde se guardarán los correos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMAILS_FILE = os.path.join(BASE_DIR, "scripts", "emails_guardados.txt")
print(f"📂 Guardando emails en: {EMAILS_FILE}")

@app.route('/guardar-email', methods=["GET", "POST"])
def guardar_email():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email or "@" not in email:
            return jsonify({"error": "Email no válido"}), 400

        # Guardar email en un archivo
        with open(EMAILS_FILE, "a") as file:
            file.write(email + "\n")

        print(f"Nuevo email guardado: {email}")

        return jsonify({"message": "Email guardado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

@app.route('/obtener-emails', methods=["GET"])
def obtener_emails():
    try:
        with open(EMAILS_FILE, "r") as file:
            emails = file.readlines()
        return jsonify({"emails": [email.strip() for email in emails]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Diccionario con los datos exactos para cada código postal
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

# Ruta para consultas demográficas
@app.route('/consulta-demografica', methods=["POST"])
def consulta_demografica():
    data = request.json
    codigo_postal = data.get('codigo_postal')

    if not codigo_postal or codigo_postal not in DATOS_MUNICIPIOS:
        return jsonify({"error": "Datos no disponibles para el código postal proporcionado."}), 404

    # Obtener los datos fijos del municipio
    datos = DATOS_MUNICIPIOS[codigo_postal]
    nombre_municipio = datos["nombre"]

    total_2024, espanoles_2024, extranjeros_2024 = datos["demografia"]["2024"]
    total_2023, espanoles_2023, extranjeros_2023 = datos["demografia"]["2023"]

    porcentaje_extranjeros_2024 = round((extranjeros_2024 / total_2024) * 100, 2)
    porcentaje_extranjeros_2023 = round((extranjeros_2023 / total_2023) * 100, 2)

    renta_persona = datos["renta"]["persona"]
    renta_hogar = datos["renta"]["hogar"]
    paro = datos["empleo"]["paro"]
    contratos = datos["empleo"]["contratos"]

    # Construir respuesta clara con datos correctos
    respuesta_clara = f"""
Resumen de los datos para el código postal {codigo_postal} ({nombre_municipio}):

    Demografía:
    - En 2024, la población total era de {total_2024:,} habitantes ({espanoles_2024:,} españoles y {extranjeros_2024:,} extranjeros, {porcentaje_extranjeros_2024}% extranjeros).
    - En 2023, la población total era de {total_2023:,} habitantes ({espanoles_2023:,} españoles y {extranjeros_2023:,} extranjeros, {porcentaje_extranjeros_2023}% extranjeros).

    Renta:
    - La renta media por persona en {codigo_postal} es de {renta_persona:,} €.
    - La renta neta media por hogar en 2022 fue de {renta_hogar:,} €.

    Empleo y Paro:
    - En 2022, hubo {paro:,} nuevas incorporaciones al paro.
    - En ese mismo año, se realizaron {contratos:,} nuevos contratos.
    """

    # Datos para gráficos
    graficos = {
        "labels": [
            "2024",
            "2023",
        ],
        "values": [espanoles_2024, extranjeros_2024, espanoles_2023, extranjeros_2023]
    }

    # Devolver respuesta
    return jsonify({
        "respuesta_clara": respuesta_clara,
        "graficos": graficos
    })

if __name__ == "__main__":
    app.run(debug=True)


# Ruta para consultas de reformas
@app.route("/consulta-reforma", methods=["GET", "POST"])
def consulta_reforma():
    try:
        datos = request.json
        reformas = datos.get("reformas", [])

        if not reformas:
            return jsonify({"error": "Debe seleccionar al menos una reforma."}), 400

        respuesta = agente_reformas.consulta_reforma(reformas)
        return jsonify(respuesta)
    except Exception as e:
        return jsonify({"error": f"Error en el agente de reformas: {str(e)}"}), 500

# Ruta para calcular la rentabilidad
@app.route("/calcular-rentabilidad", methods=["GET", "POST"])
def calcular_rentabilidad():
    try:
        datos = request.json
        valor_inmueble = datos.get("valorInmueble")
        renta_mensual = datos.get("rentaMensual")
        gastos_mensuales = datos.get("gastosMensuales")

        if not valor_inmueble or not renta_mensual or not gastos_mensuales:
            return jsonify({"error": "Faltan datos para calcular la rentabilidad."}), 400

        # Llama a la función del agente de rentabilidad
        resultado = agente_rentabilidad.calcular_rentabilidad_inmueble(
            valor_inmueble, renta_mensual, gastos_mensuales
        )

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error en el agente de rentabilidad: {str(e)}"}), 500
    
    # Ruta para obtener noticias inmobiliarias
@app.route("/obtener-noticias", methods=["GET", "POST"])
def obtener_noticias():
    try:
        noticias = newsletter_inmobiliaria.obtener_noticias_inmobiliarias()
        return jsonify(noticias)
    except Exception as e:
        return jsonify({"error": f"Error en el agente de noticias: {str(e)}"}), 500

    # Ruta para el Broker Hipotecario
@app.route("/verificar-bancos")
def verificar_bancos():
    import os
    import pandas as pd

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    ruta_bancos = os.path.abspath(os.path.join(BASE_PATH, "../data/BancosEspaña.csv"))

    if not os.path.exists(ruta_bancos):
        return jsonify({"error": "El archivo BancosEspaña.csv NO se encuentra en Render", "ruta": ruta_bancos})

    try:
        df = pd.read_csv(ruta_bancos)
        return jsonify({
            "mensaje": "Archivo cargado correctamente",
            "columnas": list(df.columns),
            "primeros_registros": df.head(5).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": f"Error al leer el archivo: {str(e)}"})
   
@app.route("/obtener-datos", methods=["GET", "POST"])
def obtener_datos():
    try:
        tipo = request.args.get("tipo", "bancos")

        if tipo == "bancos":
            if broker_hipotecario.bancos_data.empty:
                return jsonify({"error": "No hay datos de bancos disponibles"}), 404

            # 🔴 Convertimos NaN a None en TODA la tabla antes de enviar JSON
            bancos_data_clean = broker_hipotecario.bancos_data.replace({np.nan: None}).to_dict(orient="records")

            return jsonify(bancos_data_clean)
        
        elif tipo == "tasadoras":
            if broker_hipotecario.tasadoras_data.empty:
                return jsonify({"error": "No hay datos de tasadoras disponibles"}), 404
            
            # 🔴 Convertimos NaN a None en TODA la tabla
            tasadoras_data_clean = broker_hipotecario.tasadoras_data.replace({np.nan: None}).to_dict(orient="records")

            return jsonify(tasadoras_data_clean)
        
        else:
            return jsonify({"error": "Tipo no válido"}), 400
    except Exception as e:
        return jsonify({"error": f"Error en el Broker Hipotecario: {str(e)}"}), 500

# Ruta para obtener compañías de servicios
@app.route("/renombrar-archivo-gas")
def renombrar_archivo_gas():
    import os

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    ruta_actual = os.path.abspath(os.path.join(BASE_PATH, "../data/Compañia_GAS.csv"))  # Archivo con error
    ruta_nueva = os.path.abspath(os.path.join(BASE_PATH, "../data/Compañia_Gas.csv"))  # Nombre correcto

    if os.path.exists(ruta_actual):
        os.rename(ruta_actual, ruta_nueva)
        return jsonify({"mensaje": "Archivo renombrado correctamente", "nueva_ruta": ruta_nueva})
    else:
        return jsonify({"error": "El archivo Compañia_GAS.csv no existe en Render"}), 404


@app.route("/obtener-companias", methods=["GET", "POST"])
def obtener_companias():
    """
    Unifica el funcionamiento del agente de servicios para cargar compañías.
    """
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    RUTA_LUZ = os.path.join(BASE_PATH, "../data/Compañia_Luz.csv")
    RUTA_GAS = os.path.join(BASE_PATH, "../data/Compañia_GAS.csv")
    RUTA_LUZYGAS = os.path.join(BASE_PATH, "../data/Compañia_LuzyGas.csv")

    def leer_companias(ruta):
        try:
            if not os.path.exists(ruta):
                print(f"Archivo no encontrado: {ruta}")
                return []  # Retorna una lista vacía si el archivo no existe

            df = pd.read_csv(ruta)
            print(f"Contenido del archivo:\n", df.head())  # Depuración

            # Renombrar columnas
            df = df.rename(columns={"Compañia": "nombre", "Descripcion": "descripcion"})

            # Convierte el DataFrame en una lista de diccionarios
            datos = df[["nombre", "descripcion"]].to_dict(orient="records")
            print(f"Datos procesados:\n", datos)  # Depuración

            return datos
        except Exception as e:
            print(f"Error al leer el archivo {ruta}: {e}")
            return []  # Retorna una lista vacía en caso de error

    try:
        tipo = request.args.get("tipo", "").strip()
        if not tipo:
            return jsonify({"error": "Debe especificar el tipo (luz, gas, luzygas)"}), 400

        if tipo == "luz":
            datos = leer_companias(RUTA_LUZ)
        elif tipo == "gas":
            datos = leer_companias(RUTA_GAS)
        elif tipo == "luzygas":
            datos = leer_companias(RUTA_LUZYGAS)
        else:
            return jsonify({"error": "Tipo no válido. Use 'luz', 'gas' o 'luzygas'."}), 400

        return jsonify(datos)
    except Exception as e:
        print(f"Error en obtener-companias: {e}")
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500
    
    # Ruta para generar el contrato
@app.route("/generar-contrato", methods=["POST"])
@cross_origin()
def generar_contrato():
    try:
        nombre_vendedor = request.form.get("nombre_vendedor", "").strip()
        nombre_comprador = request.form.get("nombre_comprador", "").strip()
        tipo_contrato = request.form.get("tipo_contrato", "").strip()

        if not nombre_vendedor or not nombre_comprador:
            return jsonify({"error": "Faltan datos para generar el contrato"}), 400

        if tipo_contrato != "arras":
            return jsonify({"error": "Este tipo de contrato aún no está disponible"}), 400

        # Generar el contrato usando la función de agente_contratos
        contrato_path = agente_contratos.generar_contrato_personalizado(nombre_vendedor, nombre_comprador)

        if not os.path.exists(contrato_path):
            return jsonify({"error": "No se pudo generar el contrato"}), 500

        # Enviar el archivo directamente como respuesta
        return send_file(contrato_path, as_attachment=True, download_name="Contrato_Arras.docx")

    except Exception as e:
        return jsonify({"error": f"Error al generar el contrato: {str(e)}"}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000)) 
    app.run(debug=True, host='0.0.0.0', port=port)



from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import agente_demografico
import agente_reformas
import agente_rentabilidad
import newsletter_inmobiliaria
import broker_hipotecario
import agente_servicios
import agente_contratos
import os
import pandas as pd
from flask import send_file


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../templates")


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
EMAILS_FILE = "emails_guardados.txt"

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


# Ruta para consultas demográficas
@app.route('/consulta-demografica', methods=["GET", "POST"])
def consulta_demografica():
    data = request.json
    codigo_postal = data.get('codigo_postal')

    # Diccionario de datos genéricos por defecto para municipios
    municipios = {
        "28080": "Majadahonda",
        "03065": "Elche",
        "37085": "Carbajosa de la Sagrada",
        "08019": "Barcelona",
        "49275": "Zamora",
        "30024": "Lorca",
        "28079": "Madrid",
        "48020": "Bilbao",
        "13013": "Almagro",
        "18087": "Granada",
        "36038": "Pontevedra"
    }

    # Verificar si el código postal está en la lista
    if codigo_postal not in municipios:
        return jsonify({"error": "Datos no disponibles para el código postal proporcionado."}), 404

    # Generar datos simulados dinámicamente
    import random

    nombre_municipio = municipios[codigo_postal]
    poblacion_2024 = random.randint(5000, 1000000)  # Población total aleatoria
    porcentaje_extranjeros_2024 = round(random.uniform(5, 25), 2)  # Porcentaje de extranjeros
    extranjeros_2024 = int(poblacion_2024 * (porcentaje_extranjeros_2024 / 100))
    espanoles_2024 = poblacion_2024 - extranjeros_2024

    poblacion_2023 = random.randint(int(poblacion_2024 * 0.95), poblacion_2024)  # Población ligeramente menor en 2023
    porcentaje_extranjeros_2023 = round(random.uniform(5, 25), 2)
    extranjeros_2023 = int(poblacion_2023 * (porcentaje_extranjeros_2023 / 100))
    espanoles_2023 = poblacion_2023 - extranjeros_2023

    renta_media_persona = random.randint(15000, 50000)  # Renta media aleatoria
    renta_media_hogar_2022 = random.randint(35000, 70000)  # Renta por hogar
    nuevos_paro = random.randint(500, 20000)  # Nuevos casos de paro
    nuevos_contratos = random.randint(500, 20000)  # Nuevos contratos

    # Construir respuesta clara
    respuesta_clara = f"""
    Resumen de los datos para el código postal {codigo_postal} ({nombre_municipio}):
    
    Demografía:
    - En 2024, la población total era de {poblacion_2024} habitantes ({espanoles_2024} españoles y {extranjeros_2024} extranjeros, {porcentaje_extranjeros_2024}% extranjeros).
    - En 2023, la población total era de {poblacion_2023} habitantes ({espanoles_2023} españoles y {extranjeros_2023} extranjeros, {porcentaje_extranjeros_2023}% extranjeros).
    
    Renta:
    - La renta media por persona en {codigo_postal} es de {renta_media_persona} €.
    - La renta neta media por hogar en 2022 fue de {renta_media_hogar_2022} €.
    
    Empleo y Paro:
    - En 2022, hubo {nuevos_paro} nuevas incorporaciones al paro.
    - En ese mismo año, se realizaron {nuevos_contratos} nuevos contratos.
    """

    # Generar datos para gráficos
    graficos = {
        "labels": [
            "Población Española 2024",
            "Población Extranjera 2024",
            "Población Española 2023",
            "Población Extranjera 2023"
        ],
        "values": [espanoles_2024, extranjeros_2024, espanoles_2023, extranjeros_2023]
    }

    # Devolver respuesta
    return jsonify({
        "respuesta_clara": respuesta_clara,
        "graficos": graficos
    })

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
@app.route("/obtener-datos", methods=["GET"])
def obtener_datos():
    try:
        tipo = request.args.get("tipo", "bancos")
        if tipo == "bancos":
            if broker_hipotecario.bancos_data.empty:
                return jsonify({"error": "No hay datos de bancos disponibles"}), 404
            return jsonify(broker_hipotecario.bancos_data.to_dict(orient="records"))
        
        elif tipo == "tasadoras":
            if broker_hipotecario.tasadoras_data.empty:
                return jsonify({"error": "No hay datos de tasadoras disponibles"}), 404
            return jsonify(broker_hipotecario.tasadoras_data.to_dict(orient="records"))
        
        else:
            return jsonify({"error": "Tipo no válido"}), 400
    except Exception as e:
        return jsonify({"error": f"Error en el Broker Hipotecario: {str(e)}"}), 500

# Ruta para obtener compañías de servicios
@app.route("/obtener-companias", methods=["GET", "POST"])
def obtener_companias():
    """
    Unifica el funcionamiento del agente de servicios para cargar compañías.
    """
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    RUTA_LUZ = os.path.join(BASE_PATH, "../data/Compañia_Luz.csv")
    RUTA_GAS = os.path.join(BASE_PATH, "../data/Compañia_Gas.csv")
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
@app.route("/generar-contrato", methods=["GET", "POST"])
def generar_contrato():
    try:
        # Obtener los datos del formulario
        nombre_vendedor = request.form.get("nombre_vendedor", "").strip()
        nombre_comprador = request.form.get("nombre_comprador", "").strip()
        tipo_contrato = request.form.get("tipo_contrato", "").strip()

        if not nombre_vendedor or not nombre_comprador:
            return jsonify({"error": "Faltan datos para generar el contrato"}), 400

        # Solo permitimos "Contrato de Arras" por ahora
        if tipo_contrato != "arras":
            return jsonify({"error": "Este tipo de contrato aún no está disponible"}), 400

        # Generar el contrato usando el agente_contratos
        contrato_path = agente_contratos.generar_contrato_personalizado(
            nombre_vendedor, nombre_comprador
        )

        # Enviar el contrato al cliente
        return send_file(contrato_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Error al generar el contrato: {str(e)}"}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000)) 
    app.run(debug=True, host='0.0.0.0', port=port)



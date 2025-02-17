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

# Rutas de los archivos
ARCHIVOS = {
    "rentamediapersona": "../data/rentamediapersona_municipios_mvp.csv",
    "rentahogar": "../data/rentahogar_municipio_mvp.csv",
    "paro": "../data/estadistica_paro_mvp.csv",
    "empleo": "../data/estadistica_empleo_mvp.csv",
    "demografia": "../data/demografia_municipios_mvp.csv"
}

CP_MUNICIPIOS_PATH = "../data/CP_Municipios.csv"

# Cargar el archivo CP_Municipios.csv
try:
    cp_municipios_df = pd.read_csv(CP_MUNICIPIOS_PATH, dtype=str)
    cp_municipios_df["MUNICIPIO"] = cp_municipios_df["MUNICIPIO"].str.upper().str.strip()
    cp_dict = dict(zip(cp_municipios_df["CODIGO POSTAL"], cp_municipios_df["MUNICIPIO"]))
    print("Archivo CP_Municipios.csv cargado correctamente.")
except Exception as e:
    print(f"Error al cargar {CP_MUNICIPIOS_PATH}: {e}")
    exit()

# Función para procesar cada archivo y obtener datos basados en el código postal
def obtener_datos_por_codigo_postal(codigo_postal):
    codigo_postal = str(int(float(codigo_postal))).zfill(5)  # Normalizar el código postal a 5 dígitos
    resultados = []

    for nombre_archivo, ruta_archivo in ARCHIVOS.items():
        try:
            df = pd.read_csv(ruta_archivo, dtype=str)
            if "MUNICIPIO" in df.columns:
                # Normalizar la columna MUNICIPIO para buscar coincidencias
                df["MUNICIPIO"] = df["MUNICIPIO"].apply(
                    lambda x: str(int(float(x))).zfill(5) if pd.notna(x) and x.replace(".", "").isdigit() else x
                )
                # Filtrar por código postal
                datos_filtrados = df[df["MUNICIPIO"] == codigo_postal]
                if not datos_filtrados.empty:
                    resultados.append((nombre_archivo, datos_filtrados))
        except Exception as e:
            print(f"Error al procesar {nombre_archivo}: {e}")

    return resultados

# Función para limpiar y convertir valores numéricos
def limpiar_y_convertir(valor):
    try:
        return int(float(valor.replace(",", "").replace(".", "")))
    except:
        return None

# Generar un resumen con porcentajes y validaciones
def generar_resumen_con_porcentajes(codigo_postal, datos):
    demografia_resumen = []
    renta_resumen = []
    empleo_paro_resumen = []

    # Procesar datos
    for nombre_archivo, df in datos:
        if nombre_archivo == "demografia":
            try:
                total_2024 = limpiar_y_convertir(df[(df["Periodo"] == "2024") & (df["Nacionalidad"] == "Total")]["Total"].iloc[0])
                extranjeros_2024 = limpiar_y_convertir(df[(df["Periodo"] == "2024") & (df["Nacionalidad"] == "Extranjera")]["Total"].iloc[0])
                porcentaje_extranjeros_2024 = (extranjeros_2024 / total_2024) * 100 if total_2024 else 0

                total_2023 = limpiar_y_convertir(df[(df["Periodo"] == "2023") & (df["Nacionalidad"] == "Total")]["Total"].iloc[0])
                extranjeros_2023 = limpiar_y_convertir(df[(df["Periodo"] == "2023") & (df["Nacionalidad"] == "Extranjera")]["Total"].iloc[0])
                porcentaje_extranjeros_2023 = (extranjeros_2023 / total_2023) * 100 if total_2023 else 0

                demografia_resumen.append(
                    f"- En 2024, la población total era de {total_2024:,} habitantes "
                    f"({total_2024 - extranjeros_2024:,} españoles y {extranjeros_2024:,} extranjeros, "
                    f"{porcentaje_extranjeros_2024:.2f}% extranjeros)."
                )
                demografia_resumen.append(
                    f"- En 2023, la población total era de {total_2023:,} habitantes "
                    f"({total_2023 - extranjeros_2023:,} españoles y {extranjeros_2023:,} extranjeros, "
                    f"{porcentaje_extranjeros_2023:.2f}% extranjeros)."
                )
            except Exception as e:
                demografia_resumen.append(f"Error al procesar los datos de demografía: {e}")

        if nombre_archivo == "rentamediapersona":
            try:
                renta_media = limpiar_y_convertir(df["Renta"].iloc[0])
                renta_resumen.append(f"- La renta media por persona en {codigo_postal} es de {renta_media:,} €.")
            except:
                renta_resumen.append("- No se encontraron datos de renta media por persona.")

        if nombre_archivo == "rentahogar":
            try:
                renta_2022 = limpiar_y_convertir(df[df["Periodo"] == "2022"]["Total"].iloc[0])
                renta_2021 = limpiar_y_convertir(df[df["Periodo"] == "2021"]["Total"].iloc[0])
                renta_resumen.append(
                    f"- La renta neta media por hogar en 2022 fue de {renta_2022:,} €, "
                    f"representando un aumento frente a 2021 ({renta_2021:,} €)."
                )
            except:
                renta_resumen.append("- No se encontraron datos de renta media por hogar.")

        if nombre_archivo == "paro":
            try:
                total_paro = limpiar_y_convertir(df["TOTAL"].iloc[0])
                empleo_paro_resumen.append(f"- En 2022, hubo {total_paro:,} nuevas incorporaciones al paro.")
            except:
                empleo_paro_resumen.append("- No se encontraron datos sobre incorporaciones al paro.")

        if nombre_archivo == "empleo":
            try:
                total_empleo = limpiar_y_convertir(df["TOTAL"].iloc[0])
                empleo_paro_resumen.append(f"- En ese mismo año, se realizaron {total_empleo:,} nuevos contratos.")
            except:
                empleo_paro_resumen.append("- No se encontraron datos sobre nuevos contratos.")

    # Construir el resumen final
    resumen = f"""
Resumen de los datos para el código postal {codigo_postal}:

    Demografía:
    {"\n    ".join(demografia_resumen)}

    Renta:
    {"\n    ".join(renta_resumen)}

    Empleo y Paro:
    {"\n    ".join(empleo_paro_resumen)}
"""

    return resumen.strip()

# Endpoint para la consulta
@app.route("/consulta-demografica", methods=["POST"])
def consulta_demografica(codigo_postal):
    try:
        if not codigo_postal:
            return {"error": "Debe proporcionar un código postal."}

        # Obtener datos según el código postal
        datos = obtener_datos_por_codigo_postal(codigo_postal)
        if not datos:
            return {"error": f"No se encontraron datos para el código postal {codigo_postal}."}

        # Generar resumen
        resumen = generar_resumen_con_porcentajes(codigo_postal, datos)
        return {"respuesta_clara": resumen}
    except Exception as e:
        return {"error": f"Error al procesar la consulta: {e}"}


# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)

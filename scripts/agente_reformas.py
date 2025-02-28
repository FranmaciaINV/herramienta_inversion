import requests
from bs4 import BeautifulSoup

# URLs de las reformas
URLS_REFORMAS = {
    "ventana": "https://www.fixr.es/guias-de-precios/instalar-ventana",
    "radiadores": "https://www.fixr.es/guias-de-precios/instalacion-radiadores",
    "paredes": "https://www.fixr.es/guias-de-precios/pintar-paredes",
    "puerta": "https://www.fixr.es/guias-de-precios/puerta-de-entrada",
}

# Medias nacionales
MEDIA_NACIONAL = {
    "ventana": 420,
    "radiadores": 150,
    "paredes": 5.5,  # Precio fijo por metro cuadrado
    "puerta": 559
}

# Función para scrapear precios
def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        precios = []
        for parrafo in soup.find_all("p"):
            if "€" in parrafo.text or "euros" in parrafo.text.lower():
                precios.append(parrafo.text.strip())

        return {"precios": precios}
    except Exception as e:
        return {"error": f"Error al scrapear la URL: {str(e)}"}

# Función principal de consulta de reformas
def consulta_reforma(reformas):
    try:
        if not reformas:
            return {"error": "Debe seleccionar al menos una reforma."}

        detalles_reforma = []
        precio_total = 0.0  # Inicializamos el precio total correctamente

        for reforma in reformas:
            tipo = reforma.get("tipo")
            cantidad = reforma.get("cantidad", 0)
            metros = reforma.get("metros", 0)

            # Validar valores
            try:
                cantidad = int(cantidad)
                metros = float(metros)
            except ValueError:
                return {"error": f"Cantidad o metros inválidos para la reforma {tipo}"}

            # Obtener la URL y scrapear datos
            url = URLS_REFORMAS.get(tipo)
            if not url:
                detalles_reforma.append({"tipo": tipo, "error": "URL no encontrada"})
                continue

            scraping_result = scrape_url(url)
            if "error" in scraping_result:
                detalles_reforma.append({"tipo": tipo, "error": scraping_result["error"]})
                continue

            precios = scraping_result.get("precios", [])
            if precios:
                detalles_reforma.append({"tipo": tipo, "precios": precios})

            # 🔹 **Calcular el precio total correctamente**
            precio_medio = MEDIA_NACIONAL.get(tipo, 0)

            if tipo == "paredes":
                precio_total += precio_medio * metros  # 🔥 Se suma correctamente
            else:
                precio_total += precio_medio * cantidad  # 🔥 Se suma correctamente para cada elemento

        # 🔹 **Generar correctamente las descripciones de cada reforma**
        respuesta_html = f"<h3>Precio total de la Reforma: {round(precio_total, 2)}€</h3>"
        respuesta_html += "<ul>"

        for detalle in reformas:
            tipo = detalle["tipo"]
            precios_html = DESCRIPCION_DETALLADA.get(tipo, "Sin información disponible.")  # ✅ Obtener la descripción correcta

            respuesta_html += (
                f"<li>{tipo.capitalize()}: "
                f"<button onclick=\"document.getElementById('{tipo}').style.display = "
                f"(document.getElementById('{tipo}').style.display === 'none' ? 'block' : 'none')\">"
                f"Ver detalles</button>"
                f"<div id='{tipo}' style='display:none;'>{precios_html}</div></li>"
            )

        respuesta_html += "</ul>"

        return {"respuesta_html": respuesta_html}

    except Exception as e:
        return {"error": f"Error al procesar la consulta: {str(e)}"}


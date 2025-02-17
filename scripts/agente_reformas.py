import requests
from bs4 import BeautifulSoup
import pandas as pd

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
    "paredes": 1150,  # Precio medio por 250 m2
    "puerta": 559
}

# Texto personalizado de precios por reforma
DESCRIPCION_DETALLADA = {
    "ventana": """
La instalación de ventanas depende del sistema elegido:
- Sistema corredero: Precio entre 420 €/m² y 470 €/m².
- Sistema practicable: Incrementa el costo en aproximadamente 20 €/m².
- Sistema abatible: Incrementa el costo en aproximadamente 10 €/m².
- Oscilobatiente: Incrementa el costo en aproximadamente 100 €/m².
- Oscilo-paralelo: Incrementa el costo en aproximadamente 150 €/m².

Nota: Los precios incluyen instalación estándar.
    """,
    "radiadores": """
La instalación de radiadores puede ser eléctrica o de agua:

1. Radiadores eléctricos:
   - Instalación básica: No requieren obra, basta con colgarlos y enchufarlos.
   - Costos adicionales (mano de obra y transporte): 20 € - 30 €.
   - Costos aproximados:
     - Convector eléctrico para 10 m²: Desde 20 €.
     - Acumulador eléctrico: 150 €.
     - Emisor térmico seco: 100 €, de fluido: 140 €, cerámico: 240 €.

2. Radiadores de agua:
   - Radiador de acero (panel): Desde 70 €.
   - Radiador modular: Desde 90 €.
   - Radiador de hierro fundido: Desde 90 €.
   - Radiador de aluminio: Desde 129 €.

Nota: Los precios incluyen instalación estándar y están sujetos a variaciones según las dimensiones y el tipo de radiador.
    """,
    "paredes": """
Los precios para pintar paredes dependen del tipo de pintura utilizada:

1. Pintura temple:
   - Precio base: 5,5 €/m² (a partir de 10 m²).
   - Metros adicionales: Desde 3,5 €/m².
   - Ejemplo: Pintar 250 m² (piso de 50 m²): 850 €.

2. Gotelé:
   - Precio base: Desde 9,5 €/m² (a partir de 10 m²).
   - Metros adicionales: Desde 6,5 €/m².
   - Eliminar gotelé: 9 € - 12 €/m².
   - Ejemplo: Pintar 250 m² con gotelé y pintura plástica: Desde 1.600 €.

3. Pintura plástica lisa:
   - Precio base: Desde 6,5 €/m² (a partir de 10 m²).
   - Metros adicionales: Desde 4,6 €/m².
   - Ejemplo: Pintar 250 m²: 1.150 €.

4. Pintura decorativa:
   - Precio base: Desde 15 €/m².
   - Ejemplo: Pintar una pared de 4 x 20 m: 135 €.

5. Pintura antihumedad:
   - Precio base: Desde 895 € para 250 m².
    """,
    "puerta": """
El costo varía según el tipo de puerta instalada:

1. Puertas de seguridad: Desde 300 €, con instalación e IVA.
2. Puertas blindadas: Desde 559 €, con instalación e IVA.
3. Puertas acorazadas: Desde 1.200 €, con instalación e IVA.
4. Retirar una puerta antigua: Incremento de 50 € - 70 €.

Nota: Los precios pueden variar dependiendo del tamaño, material y estilo de la puerta.
    """
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
        precio_total = 0.0

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

            # Obtener la URL y scrapeo
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

            # Calcular el precio total
            precio_medio = MEDIA_NACIONAL.get(tipo, 0)
            if tipo == "paredes":
                precio_medio_por_metro = precio_medio / 250
                precio_total += precio_medio_por_metro * metros
            else:
                precio_total += precio_medio * cantidad

        # Construir la respuesta HTML
        respuesta_html = f"<h3>Precio total de la Reforma: {round(precio_total, 2)}€</h3>"
        respuesta_html += "<ul>"
        for detalle in detalles_reforma:
            tipo = detalle["tipo"].capitalize()
            precios_html = DESCRIPCION_DETALLADA.get(detalle["tipo"], "Sin información disponible.")
            respuesta_html += (
                f"<li>{tipo}: "
                f"<button onclick=\"document.getElementById('{tipo}').style.display = "
                f"(document.getElementById('{tipo}').style.display === 'none' ? 'block' : 'none')\">"
                f"Ver detalles</button>"
                f"<div id='{tipo}' style='display:none;'>{precios_html}</div></li>"
            )
        respuesta_html += "</ul>"

        return {"respuesta_html": respuesta_html}
    except Exception as e:
        return {"error": f"Error al procesar la consulta: {str(e)}"}

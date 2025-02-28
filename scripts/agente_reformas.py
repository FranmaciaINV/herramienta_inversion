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

            # Obtener el precio medio de la reforma
            precio_medio = MEDIA_NACIONAL.get(tipo, 0)

            # Calcular el precio total
            if tipo == "paredes":
                precio_total += precio_medio * metros  # 🔥 Corrección: ahora calcula bien las paredes
            else:
                precio_total += precio_medio * cantidad  # 🔥 Corrección: ahora suma todas las reformas correctamente

            # Añadir detalles de la reforma
            precios_html = DESCRIPCION_DETALLADA.get(tipo, "Sin información disponible.")
            detalles_reforma.append(
                {
                    "tipo": tipo,
                    "precio_total": round(precio_medio * (metros if tipo == "paredes" else cantidad), 2),
                    "descripcion": precios_html,
                }
            )

        # Construir la respuesta HTML
        respuesta_html = f"<h3>Precio total de la Reforma: {round(precio_total, 2)}€</h3>"
        respuesta_html += "<ul>"
        for detalle in detalles_reforma:
            tipo = detalle["tipo"].capitalize()
            precios_html = detalle["descripcion"]
            tipo_id = f"detalle_{tipo.lower()}"  # 🔹 Generamos un ID único

            respuesta_html += (
                f"<li>{tipo}: {detalle['precio_total']}€<br>"
                f"<button onclick=\"document.getElementById('{tipo_id}').style.display = "
                f"(document.getElementById('{tipo_id}').style.display === 'none' ? 'block' : 'none')\">"
                f"Ver detalles</button>"
                f"<div id='{tipo_id}' style='display:none; padding: 10px; background: #f3f3f3; border-radius: 5px;'>"
                f"{precios_html}</div></li>"
            )
        respuesta_html += "</ul>"

        return {"respuesta_html": respuesta_html}

    except Exception as e:
        return {"error": f"Error al procesar la consulta: {str(e)}"}

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

# Descripciones detalladas por tipo de reforma
DESCRIPCION_DETALLADA = {
    "ventana": """
    <b>Detalles sobre instalación de ventanas:</b><br>
    - Sistema corredero: Precio entre 420 €/m² y 470 €/m².<br>
    - Sistema practicable: Incrementa el costo en aproximadamente 20 €/m².<br>
    - Sistema abatible: Incrementa el costo en aproximadamente 10 €/m².<br>
    - Oscilobatiente: Incrementa el costo en aproximadamente 100 €/m².<br>
    - Oscilo-paralelo: Incrementa el costo en aproximadamente 150 €/m².<br>
    <i>Nota: Los precios incluyen instalación estándar.</i>
    """,
    "radiadores": """
    <b>Detalles sobre instalación de radiadores:</b><br>
    - Radiador de acero: Desde 70 €.<br>
    - Radiador modular: Desde 90 €.<br>
    - Radiador de hierro fundido: Desde 90 €.<br>
    - Radiador de aluminio: Desde 129 €.<br>
    <i>Nota: Los precios incluyen instalación estándar y pueden variar según dimensiones.</i>
    """,
    "paredes": """
    <b>Detalles sobre pintura de paredes:</b><br>
    - Pintura temple: 5,5 €/m².<br>
    - Pintura plástica: 6,5 €/m².<br>
    - Gotelé: 9,5 €/m².<br>
    - Pintura decorativa: Desde 15 €/m².<br>
    <i>Nota: Incluye material y mano de obra estándar.</i>
    """,
    "puerta": """
    <b>Detalles sobre instalación de puertas:</b><br>
    - Puertas de seguridad: Desde 300 €.<br>
    - Puertas blindadas: Desde 559 €.<br>
    - Puertas acorazadas: Desde 1.200 €.<br>
    - Retirar puerta antigua: Incremento de 50 € - 70 €.<br>
    <i>Nota: Precios pueden variar según tamaño y material.</i>
    """
}

# Función principal de consulta de reformas
def consulta_reforma(reformas):
    try:
        if not reformas:
            return {"error": "Debe seleccionar al menos una reforma."}

        precio_total = 0.0  # Inicializamos el precio total correctamente
        detalles_html = "<h3>Detalles de la Reforma</h3><ul>"

        for reforma in reformas:
            tipo = reforma.get("tipo")
            cantidad = reforma.get("cantidad", 0)
            metros = reforma.get("metros", 0)

            # Asegurar que los valores sean numéricos
            try:
                cantidad = int(cantidad)
                metros = float(metros)
            except ValueError:
                return {"error": f"Cantidad o metros inválidos para la reforma {tipo}"}

            # Obtener el precio medio
            precio_medio = MEDIA_NACIONAL.get(tipo, 0)

            # Cálculo del precio total por tipo de reforma
            if tipo == "paredes":
                subtotal = precio_medio * metros
            else:
                subtotal = precio_medio * cantidad

            precio_total += subtotal  # Sumamos al total

            precios_html = DESCRIPCION_DETALLADA.get(tipo, "Sin información disponible.")
            tipo_id = f"detalles_{tipo}"  # Generamos un ID único

            # Generar el HTML para los detalles de cada reforma
            detalles_html += (
                f"<li><b>{tipo.capitalize()}</b>: {round(subtotal, 2)} €<br>"
                f"<button class='detalle-btn' data-target='{tipo_id}'>Ver detalles</button>"
                f"<div id='{tipo_id}' class='detalle-contenido' style='display:none; padding: 10px; background: #f3f3f3; border-radius: 5px;'>"
                f"{precios_html}</div></li><br>"
            )

        detalles_html += "</ul>"

        # 🔹 **Incluir la función JavaScript en el HTML para asegurarnos de que se ejecuta correctamente**
        detalles_html += """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('.detalle-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        var targetId = this.getAttribute('data-target');
                        var elem = document.getElementById(targetId);
                        if (elem.style.display === "none" || elem.style.display === "") {
                            elem.style.display = "block";
                        } else {
                            elem.style.display = "none";
                        }
                    });
                });
            });
        </script>
        """

        return {
            "respuesta_html": f"<h3>Precio total de la Reforma: {round(precio_total, 2)}€</h3>{detalles_html}"
        }

    except Exception as e:
        return {"error": f"Error al procesar la consulta: {str(e)}"}

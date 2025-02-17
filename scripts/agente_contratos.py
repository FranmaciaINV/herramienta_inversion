from docx import Document
import os

# Definición de rutas
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTRATO_BASE = os.path.join(BASE_PATH, "../data/CONTRATO_ARRAS_TIPO.docx")
CONTRATO_PERSONALIZADO = os.path.join(BASE_PATH, "../data/CONTRATO_PERSONALIZADO.docx")

def generar_contrato_personalizado(nombre_vendedor, nombre_comprador):
    """
    Genera un contrato personalizado a partir de un documento base.
    Reemplaza los marcadores {nombre_vendedor} y {nombre_comprador} en el contrato.
    
    Args:
        nombre_vendedor (str): Nombre del vendedor que será reemplazado en el contrato.
        nombre_comprador (str): Nombre del comprador que será reemplazado en el contrato.

    Returns:
        str: Ruta al archivo del contrato personalizado generado.
    """
    try:
        # Cargar el documento base
        doc = Document(CONTRATO_BASE)

        # Reemplazar los marcadores en el contrato
        for parrafo in doc.paragraphs:
            if "{nombre_vendedor}" in parrafo.text:
                parrafo.text = parrafo.text.replace("{nombre_vendedor}", nombre_vendedor)
            if "{nombre_comprador}" in parrafo.text:
                parrafo.text = parrafo.text.replace("{nombre_comprador}", nombre_comprador)

        # Guardar el contrato personalizado
        doc.save(CONTRATO_PERSONALIZADO)
        return CONTRATO_PERSONALIZADO  # Retorna la ruta al contrato generado
    except Exception as e:
        raise RuntimeError(f"Error al generar el contrato: {str(e)}")

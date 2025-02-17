import os
import pandas as pd

def process_files_in_directory(directory, output_directory, fill_na=None):
    """
    Procesa todos los archivos .xlsx y .csv en un directorio dado.

    Args:
        directory (str): Ruta del directorio que contiene los archivos.
        output_directory (str): Ruta del directorio donde se guardarán los archivos limpios.
        fill_na (dict): Diccionario con valores para llenar valores nulos.

    Returns:
        dict: Un resumen con el estado de cada archivo procesado.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    summary = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if filename.endswith(".xlsx") or filename.endswith(".csv"):
            try:
                # Cargar archivo
                if filename.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_csv(file_path)

                # Limpiar datos
                if fill_na:
                    df.fillna(fill_na, inplace=True)

                # Guardar archivo limpio
                output_file = os.path.join(output_directory, f"cleaned_{filename}")
                if filename.endswith(".xlsx"):
                    df.to_excel(output_file, index=False)
                else:
                    df.to_csv(output_file, index=False)

                summary[filename] = "Processed successfully"
            except Exception as e:
                summary[filename] = f"Error: {str(e)}"

    return summary

import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de la página que quieres scrapear
url = "https://www.fixr.es/"

# Hacer una solicitud a la página
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lista para almacenar los datos
    data = []

    # Encuentra las secciones principales que contienen la información
    for item in soup.find_all('div', class_='price-guide'):  # Ajusta el selector según el HTML
        title = item.find('h2').get_text(strip=True) if item.find('h2') else "No title"
        price = item.find('span', class_='price').get_text(strip=True) if item.find('span', class_='price') else "No price"
        description = item.find('p').get_text(strip=True) if item.find('p') else "No description"

        # Agregar al diccionario
        data.append({
            'Título': title,
            'Precio': price,
            'Descripción': description
        })

    # Crear un DataFrame y guardarlo
    df = pd.DataFrame(data)
    df.to_csv('fixr_precios.csv', index=False, encoding='utf-8')
    print("Datos guardados en fixr_precios.csv")
else:
    print(f"Error al acceder a la página: {response.status_code}")


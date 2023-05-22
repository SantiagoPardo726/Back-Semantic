import requests
import json

def buscar_imagenes(keyword):
    # Configurar los parámetros de la solicitud
    url = 'https://api.unsplash.com/search/photos'
    parameters = {
        'query': keyword,
        'per_page': 1,  # Número de imágenes a obtener
        'client_id': '5vJW71kwQOqg7x-dp82TT0dovJtKF6MmsaMulBbr7BU'  # Reemplaza esto con tu propio Client ID de Unsplash
    }

    # Realizar la solicitud a la API de Unsplash
    response = requests.get(url, params=parameters)
    data = json.loads(response.text)

    # Extraer las URL de las imágenes de la respuesta
    urls = data['results'][0]['urls']['regular']
    return urls

# Ejemplo de uso
key_word = 'physics'
urls_images = buscar_imagenes(key_word)
print(urls_images)


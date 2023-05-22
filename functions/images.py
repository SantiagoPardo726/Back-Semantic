import requests
import json

def get_image_by_keyword(keyword):
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

    if len(data['results']) > 0:
        urls = data['results'][0]['urls']['regular']
    else:   
        urls = "https://static.vecteezy.com/system/resources/previews/004/141/669/non_2x/no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image-coming-soon-sign-simple-nature-silhouette-in-frame-isolated-illustration-vector.jpg"
    return urls




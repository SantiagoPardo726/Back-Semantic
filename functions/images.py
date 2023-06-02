import requests
import json

import requests
import json

def get_image_by_keyword(keyword):
    # Configurar los parámetros de la solicitud
    try:
        url = 'https://api.unsplash.com/search/photos'
        parameters = {
            'query': keyword,
            # 'per_page': 1,  # Número de imágenes a obtener
            'client_id': 'PQ_7eXIBaGONUQtpN3ai5I7qaXEZ4N7LgZb7QWxwu1c'  # Reemplaza esto con tu propio Client ID de Unsplash
        }

        # Realizar la solicitud a la API de Unsplash
        response = requests.get(url, params=parameters)
        print(response)
        data = json.loads(response.text)

        if len(data['results']) > 0:
            urls = data['results'][0]['urls']['regular']
        else:   
            urls = "https://static.vecteezy.com/system/resources/previews/004/141/669/non_2x/no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image-coming-soon-sign-simple-nature-silhouette-in-frame-isolated-illustration-vector.jpg"
        return urls
    except:
        return get_image_by_keyword2(keyword)
    # return "https://static.vecteezy.com/system/resources/previews/004/141/669/non_2x/no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image-coming-soon-sign-simple-nature-silhouette-in-frame-isolated-illustration-vector.jpg"

# print(get_image_by_keyword("hola"))

# import requests

def get_image_by_keyword2(keyword):
    api_key = "36966205-b991dda6737747ca70dc338c3"
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": keyword,
        "image_type": "photo"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["totalHits"] > 0:
        print(data["hits"][0]["webformatURL"])
        return data["hits"][0]["webformatURL"]
    else:
        return "https://static.vecteezy.com/system/resources/previews/004/141/669/non_2x/no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image-coming-soon-sign-simple-nature-silhouette-in-frame-isolated-illustration-vector.jpg"




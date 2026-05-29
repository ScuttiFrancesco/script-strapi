import json
import requests as req
import urllib3
import os
from dotenv import load_dotenv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"
proxies = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
    }

def get_articoli() -> list:
    path = strapi_url + 'articolis?pagination[page]=1&pagination[pageSize]=1000'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxies)
        get_response.raise_for_status()
        data = get_response.json()['data']
        #print(json.dumps(data, indent=2))
        return data
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return []
    
def get_image_id(testo: str) -> int:
    if "src=\"" in testo:
            start_index = testo.index("src=\"") + len("src=\"")
            end_index = testo.index("\"", start_index)
            image_path = '' + testo[start_index:end_index]
            return get_image_by_url(image_path)
    return -1

def get_image_by_url(image_url: str) -> int:
    url = image_url.replace('thumbnail', '')
    path = strapi_url + 'upload/files?filters[url][$contains]=' + url
    print(f"Searching for image with URL: {url}")
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxies)
        get_response.raise_for_status()
        data = get_response.json()
        if data:
            return data[0]['id']
        else:
            return -1
    except req.RequestException as e:
        print(f"Error retrieving image by URL: {e}")
        return -1
    
def link_image_to_articolo(articolo_id: str, image_id: int) -> bool:
    path = strapi_url + f'articolis/{articolo_id}'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
           'immagineInEvidenza': image_id,
           'immagineInPrimoPiano': image_id
        }
    }
    try:
        put_response = req.put(path, headers=headers, json=payload, verify=ssl_verify, proxies=proxies)
        put_response.raise_for_status()
        print(f"Image with ID {image_id} linked to articolo with ID {articolo_id} successfully.")
        return True
    except req.RequestException as e:
        print(f"Error linking image to articolo: {e.response.text}")
        return False
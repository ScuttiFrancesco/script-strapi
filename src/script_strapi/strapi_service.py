import requests as req
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"

def get_data(slug: str) -> str | None:
    path = strapi_url + 'paginas?pLevel=2&filters[slug][$eq]=' + slug
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }
    proxy = {
        "http": os.getenv("HTTP_PROXY"),
        "https": os.getenv("HTTPS_PROXY")    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        get_response.raise_for_status()
        data = get_response.json()['data'][0]
        documentId = data['documentId']
        return documentId
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

# Chiamata PUT verso Strapi per aggiornare il blocco centrale con i nuovi URL delle immagini
def update_data(documentId: str, blocco_centrale: list, spalla_destra: list) -> None:
    path = strapi_url + 'paginas/' + documentId
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
            "blocco_centrale": blocco_centrale,
            "spalla_destra": spalla_destra
        }
    }
    try:
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify)
        put_response.raise_for_status()
        print(f"Data updated successfully for document ID: {documentId}")
    except req.RequestException as e:
        print(f"Error updating data: {e.response}")
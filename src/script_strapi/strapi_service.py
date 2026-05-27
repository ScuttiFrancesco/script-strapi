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

def insert(collection_name: str, data: dict) :
    path = strapi_url + collection_name
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        response = req.post(path, json={"data": data}, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        print(f"Data inserted successfully")
        return True
    except req.RequestException as e:
        print(f"Error inserting data into {collection_name}: {e.response.text}")
        return False
    
def retrieve_data(collection_name: str, section: str) -> list:
    path = strapi_url + collection_name + f'?filters[url_addizionali][path][$contains]={section}&pLevel'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        response = req.get(path, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        return response.json().get("data", [])
    except req.RequestException as e:
        print(f"Error retrieving data from {collection_name}: {e.response.text}")
        return []
    
def replace_and_update(collection_name: str, id: int, data: dict, old: str, new: str) -> bool:
    path = strapi_url + collection_name + f'/{id}'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        blocco_centrale = data.get("blocco_centrale", [])
        if len(blocco_centrale) > 0 :
            for contenuto in blocco_centrale:
                if 'id' in contenuto:
                    del contenuto['id']
                if contenuto['__component'] == 'shared.contenuto':
                    contenuto['editor'] = replace(contenuto['editor'], old, new)
        spalla_destra = data.get("spalla_destra", [])
        if len(spalla_destra) > 0 :
            for contenuto in spalla_destra:
                if 'id' in contenuto:
                    del contenuto['id']
                if contenuto['__component'] == 'shared.contenuto':
                    contenuto['editor'] = replace(contenuto['editor'], old, new)
        data["blocco_centrale"] = blocco_centrale
        data["spalla_destra"] = spalla_destra
        if 'id' in data:
            del data['id']
        if 'documentId' in data:
            del data['documentId']
        if 'documentId' in data:
            del data['documentId']
        if 'createdAt' in data:
            del data['createdAt']
        if 'updatedAt' in data:
            del data['updatedAt']
        if 'url_addizionali' in data:
            del data['url_addizionali']
        if 'pagina' in data:
            del data['pagina']
        if 'publishedAt' in data:
            del data['publishedAt']
        print (f"Data to update for ID {id}: {json.dumps(data, indent=2)}")
        response = req.put(path, json={"data": data}, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        print(f"Data updated successfully for ID {id}")
        return True
    except req.RequestException as e:
        print(f"Error updating data in {collection_name} for ID {id}: {e.response.text}")
        return False

def replace(text: str, old: str, new: str) -> str:
    return text.replace(old, new) if text else text
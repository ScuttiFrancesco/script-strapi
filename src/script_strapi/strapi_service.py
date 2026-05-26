import requests as req
import os
from dotenv import load_dotenv
import random
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"
image_source_base_url = os.getenv("IMAGE_SOURCE_BASE_URL", "")

# Chiamata GET verso Strapi per recuperare i dati del blocco centrale e del documentId, con filtro per slug
def get_data(slug: str) -> str | None:
    path = strapi_url + 'paginas?pLevel=2&filters[slug][$eq]=' + slug
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify)
        get_response.raise_for_status()
        data = get_response.json()['data'][0]
        blocco_centrale = data['blocco_centrale']
        for blocco in blocco_centrale:
            if 'id' in blocco:
                del blocco['id']
        spalla_destra = data['spalla_destra']
        for blocco in spalla_destra:
            if 'id' in blocco:
                del blocco['id']
        documentId = data['documentId']
        blocco_centrale = handle_contenuto(blocco_centrale)
        spalla_destra = handle_contenuto(spalla_destra)
        return {"documentId": documentId, "blocco_centrale": blocco_centrale, "spalla_destra": spalla_destra}
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

# Funzione helper che collega il recupero da Strapi e la sostituzione degli URL delle immagini all'interno del blocco centrale
def handle_contenuto(blocchi: list) -> list:
    for blocco in blocchi:
        if blocco['__component'] == 'shared.contenuto':
            blocco['editor'] = find_and_replace_a(blocco['editor'])
    return blocchi

# Funzione per trovare e sostituire i vecchi URL dei link con i nuovi URL restituiti da Strapi
def find_and_replace_a(editor: str) -> str:
    if not editor:
        return editor
    editor_list = editor.split('<a ')
  
    for i, a_tag in enumerate(editor_list):
        print(f"Processing editor segment: {i}")
        if "href=\"" in a_tag:
            start_index = a_tag.index("href=\"") + len("href=\"")
            end_index = a_tag.index("\"", start_index)
            old_link_path = a_tag[start_index:end_index]
            print(f"Found link path: {old_link_path}")

            filename = old_link_path.split('/')[-1]
            new_link_url = file_exists(filename)
            if new_link_url:
                if 'https://portaleweb.servizi.arma.carabinieri.it/cms' in new_link_url:
                    new_link_url = new_link_url.replace('https://portaleweb.servizi.arma.carabinieri.it/cms', '')
                if 'https://www.armacc-prod-portale.local' in new_link_url:
                    new_link_url = new_link_url.replace('https://www.armacc-prod-portale.local', '')
                print(f"Replacing with new link URL: {new_link_url}")
                editor = editor.replace(old_link_path, new_link_url)
            else:
                print(f"File not found in Strapi: {filename}")
    return editor

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
        print(f"Error updating data: {e.response.text}")

    
def file_exists(name: str) -> str | None:
    path = strapi_url + "upload/files?filters[name][$eq]=" + name
    headers = { 
        'Authorization': 'Bearer ' + token
    }
    try:
        response = req.get(path, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]['url']
        return None
    except req.RequestException as e:
        print(f"Error checking image existence: {e}")
        return None
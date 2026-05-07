import requests as req
import os
from dotenv import load_dotenv
import random
import urllib3
from deserialize_image import deserialize_image
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
        documentId = data['documentId']
        blocco_centrale = handle_contenuto(blocco_centrale)
        return {"documentId": documentId, "blocco_centrale": blocco_centrale}
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

# Funzione helper che collega il recupero da Strapi e la sostituzione degli URL delle immagini all'interno del blocco centrale
def handle_contenuto(blocco_centrale: list) -> list:
    for blocco in blocco_centrale:
        if blocco['__component'] == 'shared.contenuto':
            blocco['editor'] = find_and_replace(blocco['editor'])
    return blocco_centrale

# Funzione per trovare e sostituire i vecchi URL delle immagini con i nuovi URL restituiti da Strapi
def find_and_replace(editor: str) -> str:
    editor_list = editor.split('<img ')
  
    for i, img_tag in enumerate(editor_list):
        print(f"Processing editor segment: {i}")
        if "src=\"" in img_tag:
            start_index = img_tag.index("src=\"") + len("src=\"")
            end_index = img_tag.index("\"", start_index)
            old_image_path = img_tag[start_index:end_index]
            print(f"Found image path: {old_image_path}")

            if old_image_path.startswith("/"):
                full_image_url = image_source_base_url.rstrip("/") + old_image_path
            else:
                full_image_url = old_image_path
            new_image_id = insert_image(full_image_url)
            if new_image_id:
                new_image_url = f"{strapi_url.replace('/api', '')}{new_image_id}"
                print(f"Replacing with new image URL: {new_image_url}")
                editor = editor.replace(old_image_path, new_image_url)
            
    return editor

# Chiamata PUT verso Strapi per aggiornare il blocco centrale con i nuovi URL delle immagini
def update_data(documentId: str, blocco_centrale: list):
    path = strapi_url + 'paginas/' + documentId
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
            "blocco_centrale": blocco_centrale
        }
    }
    try:
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify)
        put_response.raise_for_status()
        print(f"Data updated successfully for document ID: {documentId}")
    except req.RequestException as e:
        print(f"Error updating data: {e.response.text}")

# Chiamata POST verso Strapi per caricare una nuova immagine e ottenere il nuovo URL da inserire nel blocco centrale    
def insert_image(image_path: str) -> str | None:
    path = strapi_url + "upload"
    headers = {
        'Authorization': 'Bearer ' + token
    }
    try:
        files = deserialize_image(image_path)
        if files is None:
            print(f"Failed to deserialize image from path: {image_path}")
            return None
        response = req.post(path, files=files, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        image_id = response.json()[0]['id']
        image_path = response.json()[0]['url']
        print(f"Image uploaded successfully. Image ID: {image_id} URL: {strapi_url.replace('/api', '')}{image_path}")
        return image_path
    except req.RequestException as e:
        print(f"Error uploading image: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")
        return None
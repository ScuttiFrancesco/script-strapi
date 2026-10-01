import json
from urllib import response

import requests as req
import os
from dotenv import load_dotenv
import mimetypes
import urllib3
from deserialize_image import deserialize_image
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"
image_source_base_url = os.getenv("IMAGE_SOURCE_BASE_URL", "")
proxy = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
    }

def chiamata_test(url: str) -> None:
    endpoint = strapi_url + url
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        response = req.get(endpoint, headers=headers, verify=ssl_verify, proxies=proxy)
        response.raise_for_status()
        print(f"Test call successful. Status code: {response.status_code}")
        print(json.dumps(response.json(), indent=4))
    except req.RequestException as e:
        print(f"Error during test call: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")


# Chiamata GET verso Strapi per recuperare i dati del blocco centrale e del documentId, con filtro per slug
def get_data(slug: str,) -> str | None:
    path = strapi_url + 'paginas?pLevel=2&filters[slug][$eq]=' + slug
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
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
            blocco['editor'] = find_and_replace_img(blocco['editor'])
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

            if not ".pdf" in old_link_path and not ".doc" in old_link_path and not ".docx" in old_link_path and not ".xls" in old_link_path and not ".xlsx" in old_link_path:
                if old_link_path.startswith(("www.", "https://", "http://")):
                    print(f"Skipping external link: {old_link_path}")
                    continue
                if not old_link_path.startswith(("/doc", "/docs", "/image", "/images")):
                    print(f"Skipping non-document/image link: {old_link_path}")
                    continue
            if old_link_path.startswith("/"):
                full_link_url = image_source_base_url.rstrip("/") + old_link_path
            else:
                full_link_url = old_link_path
            new_link_url = insert_image(full_link_url)
            if new_link_url:
                print(f"Replacing with new link URL: {new_link_url}")
                editor = editor.replace(old_link_path, new_link_url)            
    return editor

# Funzione per trovare e sostituire i vecchi URL delle immagini con i nuovi URL restituiti da Strapi
def find_and_replace_img(editor: str) -> str:
    if not editor:
        return editor
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
                print(f"Replacing with new image URL: {new_image_id}")
                editor = editor.replace(old_image_path, new_image_id)            
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
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify, proxies=proxy)
        put_response.raise_for_status()
        print(f"Data updated successfully for document ID: {documentId}")
    except req.RequestException as e:
        print(f"Error updating data: {e}")
        if e.response is not None:
            print(f"  Body: {e.response.text}")

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
        old_image_url = image_exists(files['files'][0])
        if old_image_url:
            print(f"Image already exists in Strapi. Using existing URL: {old_image_url}")
            if 'https://portaleweb.servizi.arma.carabinieri.it/cms' in old_image_url:
                return old_image_url.replace('https://portaleweb.servizi.arma.carabinieri.it/cms', '')
            if 'https://www.armacc-prod-portale.local' in old_image_url:
                return old_image_url.replace('https://www.armacc-prod-portale.local', '')
            return old_image_url
        else:
            response = req.post(path, files=files, headers=headers, verify=ssl_verify, proxies=proxy)
            response.raise_for_status()
            image_id = response.json()[0]['id']
            image_path = response.json()[0]['url']
            print(f"Image uploaded successfully. Image ID: {image_id} URL: {strapi_url.replace('/api', '')}{image_path}")
            if 'https://portaleweb.servizi.arma.carabinieri.it/cms' in image_path:
                return image_path.replace('https://portaleweb.servizi.arma.carabinieri.it/cms', '')
            if 'https://www.armacc-prod-portale.local' in image_path:
                return image_path.replace('https://www.armacc-prod-portale.local', '')
            return image_path
    except req.RequestException as e:
        print(f"Error uploading image: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")
        return None
    
def image_exists(name: str) -> str | None:
    path = strapi_url + "upload/files?filters[name][$eq]=" + name
    headers = { 
        'Authorization': 'Bearer ' + token
    }
    try:
        response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]['url']
        return None
    except req.RequestException as e:
        print(f"Error checking image existence: {e}")
        return None

def download_image(image_path: str, file_name: str) -> None:    
    try:
        response = req.get(image_path, stream=True, verify=ssl_verify)
        response.raise_for_status()
        with open(file_name, "wb") as f:
            f.write(response.content)
    except:
        print(f"Error downloading image from {image_path}")

# Chiamata POST verso Strapi per caricare un file locale e ottenere l'URL restituito da Strapi
def insert_local_image(file_path: str) -> str | None:
    path = strapi_url + "upload"
    headers = {
        'Authorization': 'Bearer ' + token
    }
    file_name = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    old_image_url = image_exists(file_name)
    if old_image_url:
        print(f"Image already exists in Strapi. Using existing URL: {old_image_url}")
        return old_image_url
    try:
        with open(file_path, "rb") as f:
            files = {'files': (file_name, f, mime_type)}
            response = req.post(path, files=files, headers=headers, verify=ssl_verify, proxies=proxy)
        response.raise_for_status()
        uploaded = response.json()[0]
        print(f"Image uploaded successfully. Image ID: {uploaded['id']} URL: {uploaded['url']}")
        return uploaded['url']
    except OSError as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    except req.RequestException as e:
        print(f"Error uploading image: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")
        return None
    
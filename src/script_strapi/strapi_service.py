import requests as req
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import urllib.parse
import posixpath

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"

def get_data(slug: str) -> str | None:
    path = strapi_url + 'attis?pLevel=2&filters[slug][$eq]=' + slug
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify)
        get_response.raise_for_status()
        data_list = get_response.json().get('data', [])
        if not data_list:
            print(f"Nessun atto trovato per slug: {slug}")
            return None
        documentId = data_list[0]['documentId']
        return documentId
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

# Chiamata PUT verso Strapi per aggiornare l'atto con il file_id del documento caricato
def update_data(documentId: str, file_id: int) -> None:
    path = strapi_url + 'attis/' + documentId
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
            "documento": list([file_id])
        }
    }
    try:
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify)
        put_response.raise_for_status()
        print(f"Data updated successfully for document ID: {documentId}")
    except req.RequestException as e:
        print(f"Error updating data: {e.response.text if e.response else e}")

# Chiamata POST verso Strapi per caricare un nuovo file e ottenere il nuovo URL da inserire nel blocco centrale    
def insert_file(file_path: str) -> dict | None:
    path = strapi_url + "upload"
    headers = {
        'Authorization': 'Bearer ' + token
    }
    try:
        files = deserialize_file(file_path)
        if files is None:
            print(f"Failed to deserialize file from path: {file_path}")
            return None
        response = req.post(path, files=files, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        file_id = response.json()[0]['id']
        file_name = response.json()[0]['name']
        print(f"File uploaded successfully con NAME: {file_name}")
        return {'file_id':file_id, 'name': file_name}
    except req.RequestException as e:
        print(f"Error uploading file: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")
        return None
    

def deserialize_file(file_path: str) -> dict:
    """Deserializza un file da un percorso specificato.
    Args:
        file_path (str): Il percorso del file da deserializzare (URL o file locale).
    Returns:
        dict: Un dizionario contenente i dati binari del file deserializzato.
    """
    try:
        parsed_url = urllib.parse.urlparse(file_path)
        file_name = posixpath.basename(parsed_url.path)
        if not file_name:        
            file_name = "default_file.dat"

        ext = os.path.splitext(file_name)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        mime_type = mime_types.get(ext, "application/octet-stream")

        response = requests.get(
            file_path,
            timeout=60,
            verify=ssl_verify,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
        )
        print(f"Status Response: {response}")
        if response.status_code == 200:
            print(f"File downloaded successfully from {file_path}")
            return {'files': (file_name, response.content, mime_type)}
        else:
            raise requests.RequestException(f"Failed to download file. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
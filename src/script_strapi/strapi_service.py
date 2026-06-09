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
proxy = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
    }
headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
def get_data(title: str) -> str | None:
    path = strapi_url + 'attis?pLevel=2&filters[title][$eq]=' + title
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        get_response.raise_for_status()
        data_list = get_response.json().get('data', [])
        if not data_list:
            print(f"Nessun atto trovato per title: {title}")
            return None
        documentId = data_list[0]['documentId']
        print(f"Document ID retrieved successfully for title '{title}': {documentId}")
        return documentId
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

# Chiamata PUT verso Strapi per aggiornare l'atto con il file_id del documento caricato
def update_data(documentId: str, file_id: int) -> None:
    path = strapi_url + 'attis/' + documentId
    payload = {
        "data": {
            "documento": list([file_id])
        }
    }
    try:
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify, proxies=proxy)
        put_response.raise_for_status()
        print(f"Data updated successfully for document ID: {documentId}")
    except req.RequestException as e:
        print(f"Error updating data: {e.response.text if e.response else e}")

# Chiamata POST verso Strapi per caricare un nuovo file e ottenere il nuovo URL da inserire nel blocco centrale    
def insert_file(file_path: str) -> int | None:
    path = strapi_url + "upload"
    upload_headers = {'Authorization': 'Bearer ' + token}
    try:
        files = deserialize_file(file_path)
        if files is None:
            print(f"Failed to deserialize file from path: {file_path}")
            return None
        if_exists = image_exists(files['files'][0])
        if if_exists is None:
            response = req.post(path, files=files, headers=upload_headers, verify=ssl_verify, proxies=proxy)
            response.raise_for_status()
            file_id = response.json()[0]['id']
        else:
            print(f"File already exists with name: {if_exists['name']} and ID: {if_exists['id']}")
            file_id = None
        print(file_id if file_id is not None else f"Using existing file ID: {if_exists['id']} for file name: {if_exists['name']}")
        return file_id if if_exists is None else if_exists['id']
    except req.RequestException as e:
        print(f"Error uploading file: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text}")
        return None

def image_exists(name: str) -> dict | None:
    path = strapi_url + "upload/files?filters[name][$eq]=" + name
    try:
        response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        response.raise_for_status()
        data = response.json()
        if data:
            return {'id': data[0]['id'], 'name': data[0]['name']}
        return None
    except req.RequestException as e:
        print(f"Error checking image existence: {e}")
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
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"},
            proxies=proxy
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
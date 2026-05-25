import requests
import urllib3
import urllib.parse
import posixpath
import os
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"

def deserialize_image(image_path: str) -> dict:
    """Deserializza un'immagine o un documento da un percorso specificato.
    Args:
        image_path (str): Il percorso del file da deserializzare (URL o file locale).
    Returns:
        dict: Un dizionario contenente i dati binari del file deserializzato.
    """
    try:
        parsed_url = urllib.parse.urlparse(image_path)
        file_name = posixpath.basename(parsed_url.path)
        if not file_name:        
            file_name = "default_file.bin"

        ext = os.path.splitext(file_name)[1].lower()
        mime_types = {
            # Immagini
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            # Documenti
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        mime_type = mime_types.get(ext, "application/octet-stream")

        response = requests.get(
            image_path,
            timeout=60,
            verify=ssl_verify,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
        )
        print(f"Status Response: {response}")
        if response.status_code == 200:
            print(f"Image downloaded successfully from {image_path}")
            return {'files': (file_name, response.content, mime_type)}
        else:
            raise requests.RequestException(f"Failed to download image. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
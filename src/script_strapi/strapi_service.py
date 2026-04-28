import requests as req
import os
from dotenv import load_dotenv

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
        return response
    except req.RequestException as e:
        print(f"Error inserting data into {collection_name}: {e.response.text}")
        return None
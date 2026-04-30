import requests as req
import os
from dotenv import load_dotenv
import random

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"

def insert(collection_name: str, data: dict) -> str | None:
    path = strapi_url + collection_name
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        response = req.post(path, json={"data": data}, headers=headers, verify=ssl_verify)
        response.raise_for_status()
        document_id = response.json()['data']['documentId']
        print(f"Data inserted successfully. Document ID: {document_id}")
        return document_id
    except req.RequestException as e:
        print(f"Error inserting data into {collection_name}: {e.response.text}")
        slug = data.get('title', '').lower().replace(' ', '-').replace("'", '-').replace(',', '').replace('.', '').replace('(', '').replace(')', '').replace('&', '-e-') + '-' + random.randint(100,1000).__str__()
        if slug:
            try:
                data_with_slug = {**data, 'slug': slug}
                response = req.post(path, json={"data": data_with_slug}, headers=headers, verify=ssl_verify)
                response.raise_for_status()
                document_id = response.json()['data']['documentId']
                print(f"Retry OK con slug. Document ID: {document_id}")
                return document_id
            except req.RequestException as e2:
                print(f"Retry fallito: {e2.response.text}")
        return None
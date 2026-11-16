import csv
import filecmp
import json
from collections import Counter, defaultdict
from urllib import response
from urllib.parse import urljoin, urlparse

import requests as req
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import mimetypes
import urllib3
import re
from pathlib import Path
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
headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
    }

def deserialize_json(path: str) -> dict:
    file_path = Path(path)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}

def to_lista_link_component(stored_obj: dict) -> list:
    listaLink = stored_obj['listaLink']
    new_lista_link = list()
    soup = BeautifulSoup(listaLink, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        if link.has_attr('href'):
            new_lista_link.append({'link': link['href'], 'label': link.text})
    return new_lista_link

def update_lista_link_strapi(update_data: list, content_type: str, documentId: str) -> None:
    strapi_data = {
        'data':{
            'listaLink':{
                'title': 'LINK UTILI',
                'testo': None,
                'campoDaRenderizzare': None,
                'links': list()
            }
        }
    }                         
    lista_link = list(strapi_data['data']['listaLink']['links'])
    for item in update_data:
        link = {
            'etichetta': item['label'],
            'nuovaPagina': True,
            'url': item['link']
        }
        lista_link.append(link)
    strapi_data['data']['listaLink']['links'] = lista_link
    try:
        endpoint = f"{strapi_url}{content_type}/{documentId}"
        response = req.put(endpoint, json=strapi_data, headers=headers, proxies=proxy, verify=ssl_verify)
        response.raise_for_status
        print(response.status_code)
        if response.status_code == 200:
            print(f"listaLink updated for: {documentId}")
    except req.RequestException as e:
        print(f"Errore nella richiesta per id: {documentId} con errore: {e}")
"""Copia i contenuti da Strapi prod a Strapi dev."""

from __future__ import annotations


import json
import logging
import os
import time
from urllib.parse import urljoin

import urllib3
from strapi_fields import strapi_fields as sf
from dotenv import load_dotenv
from strapi_obj import *
import requests as req
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

token_prod = os.getenv("STRAPI_API_TOKEN", "")
strapi_url_prod = os.getenv("STRAPI_BASE_URL", "")
token_dev = os.getenv("STRAPI_API_TOKEN_DEV", "")
strapi_url_dev = os.getenv("STRAPI_BASE_URL_DEV", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"
proxies = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
    }
headers_prod = {
    'Authorization': 'Bearer ' + token_prod,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    # il WAF davanti al CMS risponde 403 allo User-Agent di default di requests
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
}
headers_dev = {**headers_prod, 'Authorization': 'Bearer ' + token_dev}
# per l'upload multipart il Content-Type lo imposta requests
headers_upload = {k: v for k, v in headers_dev.items() if k != 'Content-Type'}

lista_collection = [ 'gare-appaltos', ]
# campo relazione sul concorso -> collection dei figli, da inserire prima del concorso
figli_concorso = {
    'concorso_provas': 'concorso-provas',
    'concorso_novitas': 'concorso-novitas',
    'concorso_pubblico_proclamas': 'concorso-pubblico-proclamas',
}
campi_esclusi = {'id', 'documentId', 'createdAt', 'updatedAt', 'publishedAt', 'concorsis', *figli_concorso}

media_dev = {}  # id media prod -> id media dev


def get_all(base_url: str, headers: dict, content_type: str, query: str = ''):
        """Restituisce tutti i record di una collection, pagina per pagina."""    
        path = f'{base_url}{content_type}?pagination[page]=1&pagination[pageSize]=1{query}'
        response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        yield from data['data']
        


def copia_media(media: dict) -> int | None:
    """Scarica il file da prod, lo carica su dev e restituisce l'id del media su dev."""
    if media['id'] not in media_dev:
        try:
            file = req.get(urljoin(strapi_url_prod, media['url']), headers=headers_prod, verify=ssl_verify, proxies=proxies)
            file.raise_for_status()
            response = req.post(strapi_url_dev + 'upload', files={'files': (media['name'], file.content, media['mime'])},
                                headers=headers_upload, verify=ssl_verify, proxies=proxies)
            response.raise_for_status()
            media_dev[media['id']] = response.json()[0]['id']
        except req.RequestException as e:
            logger.warning("Media %s non copiato: %s", media['url'], e)
            media_dev[media['id']] = None
    return media_dev[media['id']]


def pulisci(valore):
    """Toglie i campi di sistema (anche dai componenti) e sostituisce i media con l'id su dev."""
    if isinstance(valore, list):
        return [v for v in map(pulisci, valore) if v is not None]
    if isinstance(valore, dict):
        if 'mime' in valore:
            return copia_media(valore)
        return {k: pulisci(v) for k, v in valore.items() if k not in campi_esclusi}
    return valore


def inserisci(content_type: str, item: dict, esistenti: dict, relazioni: dict | None = None) -> str | None:
    """Crea il record su dev (se lo slug non c'è già) e ne restituisce il documentId."""
    slug = item.get('slug')
    if slug in esistenti:
        return esistenti[slug]
    data = {**pulisci(item), **(relazioni or {})}
    response = req.post(strapi_url_dev + content_type, json={'data': data}, headers=headers_dev, verify=ssl_verify, proxies=proxies)
    if not response.ok:
        logger.error("%s '%s' non inserito: %s", content_type, slug, response.text)
        return None
    document_id = response.json()['data']['documentId']
    if slug:
        esistenti[slug] = document_id
    logger.info("%s '%s' inserito", content_type, slug)
    return document_id


def main() -> None:
    # slug -> documentId dei record già presenti su dev, per non duplicarli
    esistenti = {ct: {x['slug']: x['documentId'] for x in get_all(strapi_url_dev, headers_dev, ct, '&fields[0]=slug') if x.get('slug')}
                 for ct in [*lista_collection, *figli_concorso.values()]}
    # le categorie hanno documentId diversi tra prod e dev: si associano per code
    categorie_dev = {f['code']: f['documentId'] for c in get_all(strapi_url_dev, headers_dev, 'categorias', '&pLevel=2')
                     for f in c.get('categorieFiglie') or []}

    for content_type in lista_collection:
        for item in get_all(strapi_url_prod, headers_prod, content_type, '&pLevel=3'):
            relazioni = {}
            if content_type == 'concorsis' and item['slug'] not in esistenti['concorsis']:
                for campo, ct_figlio in figli_concorso.items():
                    figli = get_all(strapi_url_prod, headers_prod, ct_figlio, f'&pLevel=3&filters[concorsis][documentId][$eq]={item["documentId"]}')
                    relazioni[campo] = [d for d in (inserisci(ct_figlio, f, esistenti[ct_figlio]) for f in figli) if d]
            if 'categorias' in item:
                relazioni['categorias'] = [categorie_dev[c['code']] for c in item['categorias'] or [] if c['code'] in categorie_dev]
            inserisci(content_type, item, esistenti[content_type], relazioni)


if __name__ == "__main__":
    main()

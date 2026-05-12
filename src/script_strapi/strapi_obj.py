import requests
from strapi_interfaces import Pagina as pg
from bs4 import BeautifulSoup as bs


def retrive_html_block(url:str, class_name: str) -> str:
    """Recupera i blocchi HTML da una pagina web."""
    try:
        response = requests.get(url, verify=False, proxies={"http": None, "https": None}, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"})
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        return soup.find('div', class_=class_name)
    except requests.RequestException as e:
        print(f"Errore durante il recupero dei blocchi HTML: {e}")
        return ''

def parse_html_block(html_block) -> list:
    """Parsa i blocchi HTML e restituisce una lista di dizionari con titolo e figli."""
    if not html_block:
        return []
    return html_block.find_all('div', class_='sfContentBlock')


def create_pagina_object(url: str) -> dict:
    """Crea un oggetto Pagina a partire dai parametri."""
    blocco_centrale = []
    spalla_destra = []
    centrale = retrive_html_block(url, "docContenitore")
    destra = retrive_html_block(url, "docboxRight")
    for centro in parse_html_block(centrale):
        blocco_centrale.append({
            '__component': 'shared.contenuto',
            'editor': str(centro)
        })
    for destra_item in parse_html_block(destra):
        spalla_destra.append({
            '__component': 'shared.contenuto',
            'editor': str(destra_item)
        })
    spalla_destra.append({
            '__component': 'widget.menu',
        })
    return {'spalla_destra': spalla_destra, 'blocco_centrale': blocco_centrale}

lista =  {
    "-P-Codice Rosso": [],
    "-P-Una stanza tutta per sé": [],
    "-P-Gioco da tavolo": []
}
import requests
from strapi_interfaces import Pagina as pg
from bs4 import BeautifulSoup as bs


def retrive_html_block(url:str, elemento: str) -> str:
    """Recupera i blocchi HTML da una pagina web."""
    try:
        response = requests.get(url, verify=False, proxies={"http": None, "https": None}, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"})
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        return soup.find(elemento)
    except requests.RequestException as e:
        print(f"Errore durante il recupero dei blocchi HTML: {e}")
        return ''

def parse_html_block(html_block, elemento: str) -> list:
    """Parsa i blocchi HTML e restituisce una lista di dizionari con titolo e figli."""
    if not html_block:
        return []
    return html_block.find_all(elemento)


def parse_righe_tabella(url: str) -> list:
    """Parsa le righe di una tabella HTML e restituisce una lista di path estratti dagli href dei link presenti nelle righe."""
    try:
        t_body = retrive_html_block(url, "tbody")
        lista_path = []
        for righe in parse_html_block(t_body, "tr"):
            link = righe.find("a")
            if link and link.has_attr('href'):
                path = link['href']
                lista_path.append(path)
        return lista_path
    except Exception as e:
        print(f"Errore durante il parsing delle righe della tabella: {e}")
        return []

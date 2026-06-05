import requests as req
import os
from dotenv import load_dotenv
import urllib3
from openpyxl import load_workbook, Workbook

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FILE_EXCEL_REPORT = os.getenv("FILE_EXCEL_REPORT", r"C:\Users\francesco.scutti\Desktop\report_migrazione.xlsx")

load_dotenv()

token = os.getenv("STRAPI_API_TOKEN", "")
strapi_url = os.getenv("STRAPI_BASE_URL", "")
ssl_verify = os.getenv("STRAPI_SSL_VERIFY", "false").lower() == "true"
proxy = {
    "http": "",
    "https": ""
    }

def update_concorso(documentId: str, bando_ids: list, annullamento_ids: list, documentiCorrelati_ids: list, normeTecniche_ids: list, avvisi_ids: list, esiti_ids: list) -> None:
    path = strapi_url + 'concorsis/' + documentId
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": {
            "bando": bando_ids,
            "annullamento": annullamento_ids,
            "documentiCorrelati": documentiCorrelati_ids,
            "normeTecniche": normeTecniche_ids,
            "avvisi": avvisi_ids,
            "esiti": esiti_ids
        }
    }
    try:
        put_response = req.put(path, json=payload, headers=headers, verify=ssl_verify, proxies=proxy)
        put_response.raise_for_status()
        total = len(bando_ids) + len(annullamento_ids) + len(documentiCorrelati_ids) + len(normeTecniche_ids) + len(avvisi_ids) + len(esiti_ids)
        print(f"Concorso updated successfully for document ID: {documentId} - Totale documenti associati: {total}")
    except req.RequestException as e:
        print(f"Error updating concorso: {e.response}")

def get_doc_id(url: str) -> int | None:
    path = strapi_url + 'upload/files?filters[url][$containsi]=' + url
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        get_response.raise_for_status()
        data = get_response.json()
        print(f"Response data for URL {url}: {data}")
        if data:
            return data[0]['id']
        else:
            print(f"No document found with URL: {url}")
            return None
    except req.RequestException as e:
        print(f"Error retrieving document ID: {e}")
        return None

def get_docs_in_folder(folder_path: str) -> dict:
    """Recupera tutti i file Strapi che contengono folder_path nell'URL e restituisce una mappa {nome_normalizzato: id}."""
    path = strapi_url + f'upload/files?filters[url][$containsi]={folder_path}&pagination[pageSize]=100'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }
    try:
        response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        response.raise_for_status()
        files = response.json()
        doc_map = {}
        for f in files:
            file_url = f.get('url', '')
            filename = file_url.split('/')[-1]
            name_no_ext = filename.rsplit('.', 1)[0]
            normalized = name_no_ext.lower().replace('-', '')
            doc_map[normalized] = f['id']
            print(f"  Mappato: '{normalized}' -> id={f['id']} ({file_url})")
        print(f"Totale file trovati nella cartella '{folder_path}': {len(doc_map)}")
        return doc_map
    except req.RequestException as e:
        print(f"Errore nel recupero dei file dalla cartella {folder_path}: {e}")
        return {}

def find_doc_id_in_map(doc_map: dict, target_url: str) -> int | None:
    """Cerca l'id di un documento nel map normalizzando il nome file. Fallback progressivo con startswith."""
    filename = target_url.split('/')[-1].split('?')[0]
    name_no_ext = filename.rsplit('.', 1)[0]
    search_key = name_no_ext.lower().replace('-', '')

    # match esatto
    if search_key in doc_map:
        print(f"  Match esatto: '{search_key}'")
        return doc_map[search_key]

    # match progressivo con startswith (riduci prefisso di 1 char alla volta)
    min_length = 5
    for length in range(len(search_key) - 1, min_length - 1, -1):
        prefix = search_key[:length]
        matches = [(k, v) for k, v in doc_map.items() if k.startswith(prefix)]
        if len(matches) == 1:
            print(f"  Match con prefisso '{prefix}' (lunghezza={length}) -> '{matches[0][0]}'")
            return matches[0][1]
        elif len(matches) > 1:
            continue  # prefisso ancora ambiguo, riduci ancora

    print(f"  Nessun match trovato per: '{search_key}' (url: {target_url})")
    return None

def get_data(slug: str) -> str | None:
    path = strapi_url + 'paginas?pLevel=2&filters[slug][$eq]=' + slug
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }
    try:
        get_response = req.get(path, headers=headers, verify=ssl_verify, proxies=proxy)
        get_response.raise_for_status()
        data = get_response.json()['data'][0]
        documentId = data['documentId']
        return documentId
    except req.RequestException as e:
        print(f"Error retrieving data: {e}")               
        return None

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
        print(f"Error updating data: {e.response}")

# Funzione per scrivere un report su Excel con i dettagli della migrazione
def scrivi_report_excel(sezione: str, url: str, slug: str) -> None:
    try:
        if not os.path.exists(FILE_EXCEL_REPORT):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Report Migrazione"
            sheet.append(["DATA", "SEZIONE", "SLUG", "URL", "ESITO", "NOTE"])
            workbook.save(FILE_EXCEL_REPORT)
        workbook = load_workbook(FILE_EXCEL_REPORT)
        sheet = workbook['Report Migrazione']
        sheet.append(["", sezione, slug, url, "", ""])

        workbook.save(FILE_EXCEL_REPORT)
    except Exception as e:
        print(f"Error writing to Excel report: {e}")
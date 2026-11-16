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

# Scarica i PDF elencati nella tabella di una pagina del sito CC, in una cartella col nome dell'ultimo segmento dell'URL
def download_pdf_from_sito_cc(url: str, single_pdf: bool = True) -> bool:
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
        }
    folder = 'amm_trasp_collaborazione'    
    os.makedirs(folder, exist_ok=True)
    if not single_pdf:
        try:
            response = req.get(url, verify=ssl_verify, headers=headers, timeout=120)
            response.raise_for_status()
        except req.RequestException as e:
            print(f"Error downloading page {url}: {e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        links = [urljoin(url, a["href"]) for a in soup.select('a[href]') if '.pdf' in a["href"].lower()]
        if not links:
            print(f"No PDF found in {url}")
            return        
        downloaded = 0
        for link in links:
            try:
                pdf = req.get(link, verify=ssl_verify, headers=headers, timeout=120)
                pdf.raise_for_status()                            
            except req.RequestException as e:
                print(f"Error downloading PDF from {link}: {e}")
                continue
            with open(os.path.join(folder, os.path.basename(urlparse(link).path)), "wb") as f:
                f.write(pdf.content)
            downloaded += 1
        print(f"Downloaded {downloaded}/{len(links)} PDF in {folder}")
        return True
    else:
        try:
            pdf = req.get(url, verify=ssl_verify, headers=headers, timeout=120)
            pdf.raise_for_status()                        
        except req.RequestException as e:
            print(f"Error downloading PDF from {url}: {e}")        
            return False
        with open(os.path.join(folder, os.path.basename(urlparse(url).path)), "wb") as f:
            f.write(pdf.content)
            print(f"Download pdf: {Path(url).name} da: {url}")
        return True

# converte contenuto strapi in bozza
def to_draft(url: str, documentId: str) -> None:
    endpoint = strapi_url + url + documentId
    try:
        response = req.post(endpoint, headers=headers, proxies=proxy,verify=ssl_verify)
        response.raise_for_status
        print(f"{response.status_code} spubblicato correttamente {documentId}")
    except:
        print(f"Error updating item: {documentId}")

# Scarica i PDF gare appalto elencati nella tabella di una pagina del sito CC, in una cartella col nome dell'ultimo segmento dell'URL
def download_pdf_gare_from_sito_cc(url: str, pattern: str, codiceCig: str = '') -> None:
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
        }
    try:
        response = req.get(url, verify=ssl_verify, headers=headers, timeout=60)
        response.raise_for_status()
    except req.RequestException as e:
        print(f"Error downloading page {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    links = [urljoin(url, a["href"]) for a in soup.select('a[class*="sfdownloadTitle"][href]')]
    if not links:
        print(f"No PDF found in {url}")
        return

    if pattern == 'new':
        #folder = url.rstrip("/").split("/")[-1]
        folder = 'gare-appalto'
    elif pattern == 'old':
        cig_gara = codiceCig.replace(',', ' ').split() if codiceCig else []
        if not cig_gara: return
        folder = os.path.join("gare-appalto", cig_gara[0])
    os.makedirs(folder, exist_ok=True)
    downloaded = 0
    for link in links:
        try:
            pdf = req.get(link, verify=ssl_verify, headers=headers, timeout=60)
            pdf.raise_for_status()
        except req.RequestException as e:
            print(f"Error downloading PDF from {link}: {e}")
            continue
        with open(os.path.join(folder, os.path.basename(urlparse(link).path)), "wb") as f:
            f.write(pdf.content)
        downloaded += 1
    print(f"Downloaded {downloaded}/{len(links)} PDF in {folder}")

def exists_file_in_folder(folder: str, file_name: str) -> bool:
    if not Path(folder).is_dir():
        return False
    return Path(os.path.join(folder, file_name)).is_file()


def has_local_pdf_gare(id_gara: str, codice_cig: str | None, pattern: str) -> bool:
    cartella = r'C:\Users\francesco.scutti\Desktop\MIGRAZIONE\GareAppalto\2022'
    if pattern == 'new':
        pdf_files = [
                    f for f in os.listdir(cartella)
                    if f.lower().endswith(".pdf") or f.lower().endswith(".docx") and os.path.isfile(os.path.join(cartella, f))
                ]
        return any(id_gara in pdf for pdf in pdf_files)
    elif pattern == 'old':
        basi = [cartella]
        if os.path.isdir('gare-appalto'):
            basi.append('gare-appalto')
        if codice_cig:            
            # I nomi delle cartelle sono CIG uniti da "_", a volte solo una parte di quelli su Strapi: basta un CIG in comune
            cig_gara = set(codice_cig.replace(',', ' ').split())
            for base in basi:
                for nome in os.listdir(base):
                    if cig_gara & set(nome.split('_')) and os.path.isdir(os.path.join(base, nome)):
                        return True
            return False
        else:
            parsed_id_gara = parse_id_gara(id_gara)
            chiave = solo_alfanumerici(parsed_id_gara)
            for base in basi:
                for nome in os.listdir(base):
                    if solo_alfanumerici(nome) == chiave and os.path.isdir(os.path.join(base, nome)):
                        edit_folder_name(base, nome, parsed_id_gara)
                        return True
            return False

def get_data_strapi(pag: int, endpoint:str) -> list:
    pag = str(pag)
    endpoint = strapi_url + endpoint
    params = {
                "pagination[page]": pag,
                "pagination[pageSize]": "500"
            } 
    while True:
        try:
            response = req.get(endpoint, params=params, headers=headers, proxies=proxy, verify=ssl_verify)
            response.raise_for_status()
            return response.json()['data']
        except req.RequestException as e:
            print(f"Error rquesting : {e}")

def get_gare_strapi(pag: int) -> list:
    pag = str(pag)
    endpoint = strapi_url + f'gare-appaltos?filters[publicationDate][$between][0]=2022-01-01&filters[publicationDate][$between][1]=2022-12-31&pagination[page]={pag}&pagination[pageSize]=500'
    while True:
        try:
            response = req.get(endpoint, headers=headers, proxies=proxy, verify=ssl_verify)
            response.raise_for_status()
            return response.json()['data']
        except req.RequestException as e:
            print(f"Error rquesting : {e}")

# Rinomina la cartella e restituisce il nome finale; se il nuovo nome è già occupato la lascia com'è
def edit_folder_name(path: str, folder_name: str, new_folder_name: str) -> str:
    if folder_name == new_folder_name:
        return folder_name
    destinazione = os.path.join(path, new_folder_name)
    if os.path.exists(destinazione) and folder_name.lower() != new_folder_name.lower():
        print(f"Cartella NON rinominata, nome già esistente: {folder_name} -> {new_folder_name}")
        return folder_name
    os.rename(os.path.join(path, folder_name), destinazione)
    print(f"Rinominata: {folder_name} -> {new_folder_name}")
    return new_folder_name

def parse_id_gara(id_gara: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s_]", '_', id_gara).lower()

# Chiave di confronto: le cartelle e gli idGara possono differire per punteggiatura, spazi e maiuscole
def solo_alfanumerici(nome: str) -> str:
    return re.sub(r"[^a-z0-9]", "", nome.lower())

def check_pdf_inconsistency(path: str) -> None:
    percorso = Path(path)
    count = 0
    if not percorso.is_dir():
        return
    for file in os.listdir(percorso):
        if not os.path.isfile(os.path.join(percorso, file)):
            continue
        nome_file = re.sub(r"\.(pdf|docx)", "", file, flags=re.IGNORECASE)
        
         
        nome_file = nome_file[:60]
        params = {
            "filters[$or][0][title][$containsi]": nome_file,
            "filters[$or][1][codiceCig][$containsi]": nome_file,
            "filters[$or][2][slug][$containsi]": nome_file,
            "filters[$or][3][idGara][$containsi]": nome_file,
        }
        try:
            response = req.get(f"{strapi_url}gare-appaltos", params=params,
                               headers=headers, proxies=proxy, verify=ssl_verify, timeout=60)
            response.raise_for_status()
        except req.RequestException as e:
            print(f"Errore chiamata per la cartella {nome_file}: {e}")
            continue
        if not response.json()["data"]:
            print(f"Gara non trovata per il file: {nome_file}")
            count += 1
    print(f"Conteggio finale gare mancanti su Strapi: {count}")

# --- Unione dei file delle cartelle-gara in un'unica cartella, con l'idGara di Strapi nel nome ---

PAROLE_VUOTE = {"di", "del", "della", "delle", "dei", "degli", "dello", "e", "ed", "il", "lo", "la", "le", "i", "gli",
                "per", "a", "al", "alla", "alle", "ai", "da", "dal", "in", "con", "su", "un", "una", "n", "quot", "amp"}
CIG_RE = re.compile(r"^(?=.*\d)[a-z0-9]{10,16}$")  # CIG da 10 caratteri, più le versioni "espanse" da Excel


# Scarica tutte le gare pubblicate in un anno, solo con i campi che servono all'abbinamento
def get_gare_anno(anno: int) -> list[dict]:
    gare, pagina = [], 1
    while True:
        response = req.get(f"{strapi_url}gare-appaltos", headers=headers, proxies=proxy, verify=ssl_verify, timeout=60,
                           params={
                               "filters[publicationDate][$between][0]": f"{anno}-01-01",
                               "filters[publicationDate][$between][1]": f"{anno}-12-31",
                               "fields[0]": "idGara", "fields[1]": "title", "fields[2]": "codiceCig",
                               "pagination[page]": pagina, "pagination[pageSize]": 100,
                           })
        response.raise_for_status()
        body = response.json()
        gare += body["data"]
        if pagina >= body["meta"]["pagination"]["pageCount"]:
            return gare
        pagina += 1


# CIG come 7785888E05 che Excel ha trasformato in 778588800000 (in locale o su Strapi): li porto tutti alla forma espansa
def _espandi_excel(parola: str) -> str:
    m = re.fullmatch(r"(\d+)e(\d{1,2})", parola)
    return str(int(m.group(1)) * 10 ** int(m.group(2))) if m and len(parola) == 10 else parola


# Parole significative di un nome; le lettere accentate fanno da separatore ("vetustà" -> "vetust"), come nei nomi delle cartelle
def _parole(testo: str | None) -> set[str]:
    return {_espandi_excel(p) for p in re.split(r"[^a-z0-9]+", (testo or "").lower()) if p and p not in PAROLE_VUOTE}


def indicizza_gare(gare: list[dict]) -> dict:
    per_cig = defaultdict(set)
    for i, gara in enumerate(gare):
        for parola in _parole(gara.get("codiceCig")):
            if CIG_RE.match(parola):
                per_cig[parola].add(i)
    return {"gare": gare, "per_cig": per_cig,
            "parole": [_parole(g.get("idGara")) | _parole(g.get("title")) for g in gare]}


# Trova la gara di una cartella: prima per CIG (match esatto), poi per somiglianza del testo con idGara/titolo.
# Restituisce (idGara, metodo, candidati); idGara è None se non c'è un vincitore chiaro.
def abbina_gara(nome: str, indice: dict) -> tuple[str | None, str, str]:
    gare = indice["gare"]
    parole = _parole(nome)

    voti = Counter(i for p in parole if CIG_RE.match(p) for i in indice["per_cig"].get(p, ()))
    if voti:
        classifica = voti.most_common(3)
        candidati = " | ".join(gare[i]["idGara"] for i, _ in classifica)
        if len(classifica) == 1 or classifica[0][1] > classifica[1][1]:
            return gare[classifica[0][0]]["idGara"], "cig", candidati
        return None, "ambiguo", candidati

    # Punteggio = parole in comune / parole del nome più corto: le parole in più da una delle due parti non penalizzano
    punteggi = []
    if len(parole) >= 3:
        for i, parole_gara in enumerate(indice["parole"]):
            comuni = len(parole & parole_gara)
            if comuni >= 3:
                punteggi.append((comuni / min(len(parole), len(parole_gara)), comuni / len(parole | parole_gara), i))
    if not punteggi:
        return None, "nessuno", ""
    punteggi.sort(reverse=True)
    candidati = " | ".join(f"{gare[i]['idGara']} ({p:.2f})" for p, _, i in punteggi[:3])
    primo = punteggi[0]
    secondo = punteggi[1] if len(punteggi) > 1 else (0, 0, None)
    if primo[0] >= 0.8 and (primo[0] - secondo[0] >= 0.1 or primo[1] - secondo[1] >= 0.1):
        return gare[primo[2]]["idGara"], "testo", candidati
    return None, "ambiguo", candidati


# "<idGara>__<nome originale>[_n].ext": l'idGara resta sempre intero, se serve si accorcia solo il nome originale.
# progressivo > 1 distingue file con lo stesso nome ma contenuto diverso. None se l'idGara da solo supera il limite.
def _nome_destinazione(id_gara: str, nome_file: str, limite: int, progressivo: int = 1) -> tuple[str, bool] | None:
    stem, ext = os.path.splitext(nome_file)
    coda = f"{'_' + str(progressivo) if progressivo > 1 else ''}{ext}"
    spazio = limite - len(id_gara) - 2 - len(coda)
    if spazio < 1:
        return None
    return f"{id_gara}__{stem[:spazio]}{coda}", len(stem) > spazio


# Rinomina i file di ogni cartella-gara di source_folder come "<idGara>__<nome>" e li sposta in destination_folder.
# Con dry_run=True scrive solo l'anteprima CSV; con dry_run=False sposta e scrive il log (sorgente -> destinazione).
# manuali: {nome cartella: idGara} per le cartelle che l'abbinamento automatico non risolve.
def move_pdf_in_folder(source_folder: str, destination_folder: str, anno: int,
                       dry_run: bool = True, manuali: dict[str, str] | None = None) -> None:
    sorgente, destinazione = Path(source_folder), Path(destination_folder)
    if not sorgente.is_dir() or not destinazione.is_dir():
        print("Cartella sorgente o destinazione inesistente")
        return
    manuali = manuali or {}
    indice = indicizza_gare(get_gare_anno(anno))
    print(f"Gare {anno} su Strapi: {len(indice['gare'])}")
    limite = 255 - len(str(destinazione))  # percorso completo sotto i 260 caratteri (LongPathsEnabled è disattivato)

    abbinamenti: dict[str, tuple[str | None, str, str]] = {}

    def gara_di(cartella: Path) -> tuple[str | None, str, str]:
        if cartella.name not in abbinamenti:
            if cartella.name in manuali:
                abbinamenti[cartella.name] = (manuali[cartella.name], "manuale", "")
            else:
                abbinamenti[cartella.name] = abbina_gara(cartella.name, indice)
        return abbinamenti[cartella.name]

    # Fase 1: piano. Nessun file viene toccato finché il piano non è completo.
    occupati: dict[str, Path] = {}  # nome in destinazione (minuscolo, Windows non distingue) -> file che lo occuperà
    righe = []
    for voce in sorted(sorgente.iterdir()):
        if voce.is_file():
            righe.append({"sorgente": str(voce), "destinazione": "", "metodo": "", "idGara": "",
                          "esito": "saltato: file sfuso", "candidati": ""})
            continue
        for file in sorted(p for p in voce.rglob("*") if p.is_file()):
            # le sottocartelle (es. un CIG dentro un altro CIG) provano prima col proprio nome, poi con la cartella principale
            id_gara, metodo, candidati = gara_di(file.parent)
            if id_gara is None and file.parent != voce:
                id_gara, metodo, candidati = gara_di(voce)
            riga = {"sorgente": str(file), "destinazione": "", "metodo": metodo, "idGara": id_gara or "",
                    "esito": "", "candidati": candidati}
            righe.append(riga)
            if id_gara is None:
                riga["esito"] = f"saltato: cartella {metodo}"
                continue

            n = 1
            while True:
                risultato = _nome_destinazione(id_gara, file.name, limite, n)
                if risultato is None:
                    riga["esito"] = f"saltato: idGara di {len(id_gara)} caratteri, supera il limite di Windows"
                    break
                nome, troncato = risultato
                occupante = occupati.get(nome.lower())
                if occupante is None and (destinazione / nome).exists():
                    occupante = destinazione / nome
                if occupante is None:
                    riga["esito"] = "da spostare" + (" (nome accorciato)" if troncato else "")
                    riga["destinazione"] = str(destinazione / nome)
                    occupati[nome.lower()] = file
                    break
                if filecmp.cmp(file, occupante, shallow=False):
                    riga["esito"] = f"saltato: identico a {occupante}"
                    break
                n += 1

    # Fase 2: spostamento
    if not dry_run:
        for riga in righe:
            if not riga["esito"].startswith("da spostare"):
                continue
            try:
                Path(riga["sorgente"]).rename(riga["destinazione"])  # su Windows fallisce se la destinazione esiste: niente sovrascritture
                riga["esito"] = riga["esito"].replace("da spostare", "spostato")
            except OSError as e:
                riga["esito"] = f"errore: {e}"

    log = destinazione.parent / f"{destinazione.name}_{'anteprima' if dry_run else 'spostamenti'}.csv"
    with open(log, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["sorgente", "destinazione", "metodo", "idGara", "esito", "candidati"],
                                delimiter=";")
        writer.writeheader()
        writer.writerows(righe)

    print(f"Cartelle per metodo di abbinamento: {dict(Counter(m for _, m, _ in abbinamenti.values()))}")
    print(f"File per esito: {dict(Counter(r['esito'].split(':')[0] for r in righe))}")
    print(f"Dettaglio in {log}")

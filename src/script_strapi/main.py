"""Entry point principale dello script."""

from __future__ import annotations;
from pathlib import Path
import logging;
import os
from articoli import *
from lista_link import *
import time;
from strapi_service import *;
from gare_appalto import *;

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

#slug = "09-umorismo"
lista_slug = [
   
    "sommario"
   
]
#slug = "anafim"
lista = [
'Presentazione domande',
'Esercitazione Test',
'Prova preliminare',
'Esiti Prova preliminare',
'Prove efficienza fisica',
'Prove Psico fisiche',
'Accertamenti sanitari',
 'Accertamenti attitudinali',
 'Prova scritta',
 'Esiti Prova scritta',
 'Accertamenti lingua inglese',
 'Prova orale',
 'Prova orale matematica',
 'Prova facoltativa lingua straniera',
 'Prova orale facoltativa lingua straniera',
 'Graduatoria finale',
 'Incorporamento',
 'Tirocinio',
 'Riconvocati',
 'Prova di conoscenza della lingua inglese',
 'Prova di informatica'
]
MAX_RETRIES = 5
RETRY_DELAY = 10  # secondi
root = Path(__file__).resolve().parents[2]

def main() -> None:
    #insert_local_image(str(root / "Accertamenti attitudinali.png"))
    # compila campo anno in gara appalto in base a publicationDate
    """ for pag in range(1,95):
        print(f"------------PAGINA {pag}------------")
        chiamata_test('gare-appaltos',pag) """

    # inserisce su strapi listaLink salvati in locale come html
    """ folder = 'concorsi_listaLink'
    files = [file for file in os.listdir(folder)]
    for item in files:
        lista = to_lista_link_component(deserialize_json(os.path.join(folder, item)))
        update_lista_link_strapi(lista, 'concorsis', item.removesuffix('.json')) """


    """ for name in lista:
        download_image(f'https://www.carabinieri.it/images/default-source/iterconcorsuale/{name.replace(" ", "-")}.png', name + '.png') """

    #check_pdf_inconsistency(r'C:\Users\francesco.scutti\Desktop\MIGRAZIONE\GareAppalto\2024')
    #move_pdf_in_folder(r'C:\Users\francesco.scutti\Desktop\MIGRAZIONE\2023', r'C:\Users\francesco.scutti\Desktop\MIGRAZIONE\2023-UNITI', 2023, dry_run=False)

    # scarica i pdf dal sito cc verificando che non siano già presenti in locale
    """ items = list()
    for pag in range(1, 3):
        strapi_data = get_data_strapi(pag, 'amministrazione-trasparente-collaboraziones')
        items.extend(strapi_data)
    for item in items:
        anno_riferimento = item['annoRiferimento']
        dati_fiscali = item['datiFiscali']
        folder_to_check = ""
        exists = exists_file_in_folder(folder_to_check, dati_fiscali + '.pdf')
        if exists: continue
        has_error = download_pdf_from_sito_cc(f"https://www.carabinieri.it/docs/default-source/Amministrazione-trasparente/consulenze_{anno_riferimento}/{dati_fiscali}.pdf")
        if not has_error:
            to_draft('unpublish/amministrazione-trasparente-collaborazione/', item['documentId']) """
    
    # scarica i pdf di gare dal sito cc verificando che non siano già presenti in locale
    """ count = 0
    for ciclo in range(1, 3):
        gare = get_gare_strapi(ciclo)
        print(len(gare))
        for gara in gare:
            count += 1                   
            found_pdf = has_local_pdf_gare(gara['idGara'] ,gara['codiceCig'], 'old')
            if found_pdf:                
                print(f"Elemento n° {count} --- Pdf already present for: {gara['idGara']}")
                continue
            else:  
                print(f"Elemento n° {count} --- Pdf MISSING for: {gara['idGara']}")              
                download_pdf_gare_from_sito_cc(f"https://www.carabinieri.it/in-vostro-aiuto/amm-trasp/gare-appalto/gare-appalto/{gara['idGara']}", 'old', gara['codiceCig']) """
                

    """ cartella = './anno-2022/'
    for file in os.listdir(cartella):
        old_path = os.path.join(cartella, file)
        new_file_name = edit_file_name(file)
        if new_file_name is None:
            continue
        new_file_path = os.path.join(cartella, new_file_name)
        os.rename(old_path, new_file_path)
        print(f"Rinominato {file} in {new_file_name}") """
    
    """ doc_bloc = None
    for slug in lista_slug:
        for attempt in range(1, MAX_RETRIES + 1):
            doc_bloc = get_data(slug)
            if not doc_bloc:
                logger.error("Impossibile recuperare i dati da Strapi. Aggiornamento annullato.")
                return
            has_content = any(
                b.get('__component') == 'shared.contenuto' and b.get('editor')
            for b in doc_bloc["blocco_centrale"] + doc_bloc["spalla_destra"]
            )
            if has_content:
                break
            if attempt < MAX_RETRIES:
                logger.warning(f"Strapi non ha ancora i dati pronti (tentativo {attempt}/{MAX_RETRIES}). Nuovo tentativo tra {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Nessun contenuto HTML trovato in Strapi dopo tutti i tentativi. Aggiornamento annullato.")
                return
        update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"]) """

    """ for item in lista:
        slug = item
        doc_bloc = None
        for attempt in range(1, MAX_RETRIES + 1):
            doc_bloc = get_data(slug)
            if not doc_bloc:
                logger.error("Impossibile recuperare i dati da Strapi. Aggiornamento annullato.")
                return
            has_content = any(
                b.get('__component') == 'shared.contenuto' and b.get('editor')
                for b in doc_bloc["blocco_centrale"] + doc_bloc["spalla_destra"]
            )
            if has_content:
                break
            if attempt < MAX_RETRIES:
                logger.warning(f"Strapi non ha ancora i dati pronti (tentativo {attempt}/{MAX_RETRIES}). Nuovo tentativo tra {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
        else:
            logger.error("Nessun contenuto HTML trovato in Strapi dopo tutti i tentativi. Aggiornamento annullato.")
            return
        update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"])
        time.sleep(2)   """
    """ articoli = get_articoli()
        for articolo in articoli:
        if '<img ' in articolo['testo']:
            print(get_image_id(articolo['testo']))
            link_image_to_articolo(articolo['documentId'], get_image_id(articolo['testo'])) """

if __name__ == "__main__":
    main()
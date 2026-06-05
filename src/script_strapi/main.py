"""Entry point principale dello script."""

from __future__ import annotations

import logging
import os
from dotenv import load_dotenv
from strapi_service import *
from strapi_obj import *

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

collection_name = 'paginas'
#url = "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/introduzione"
#slug = "introduzione-5"

mappa = {
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/la-cattura-del-bandito-musolino": "la-cattura-del-bandito-musolino",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/il-moretto-e-il-biondin": "il-moretto-e-il-biondin",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/nella-campagna-di-novara": "nella-campagna-di-novara",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/il-leggendario-gasco": "il-leggendario-gasco",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/il-processo-cuocolo": "il-processo-cuocolo",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/i-personaggi-della-camorra": "i-personaggi-della-camorra",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/i-carabinieri-finti-camorristi": "i-carabinieri-finti-camorristi",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/nel-primo-centenario-dei-reali-carabinieri": "nel-primo-centenario-dei-reali-carabinieri",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/cimenti-eroismi-ideali-(1814---1914)": "cimenti-eroismi-ideali-1814-1914",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/siamo-vivi-perchè-lui-volle-morire-per-noi": "siamo-vivi-perche-lui-volle-morire-per-noi",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/salvo-d'acquisto-eroe-e-martire-cristiano": "salvo-dacquisto-eroe-e-martire-cristiano",
  "https://www.carabinieri.it/media---comunicazione/pubblicazioni/cronache-del-passato/i-racconti/parte-ii---1890---1964/i-carabinieri-durante-l'occupazione-nazista-da-fertilia-alle-fosse-ardeatine": "i-carabinieri-durante-loccupazione-nazista-da-fertilia-alle-fosse-ardeatine"
}

def main() -> None:   
        # recupera html e inserisce su strapi
    for item in mappa.items():
        url = item[0]        
        slug = item[1]
        try:
            document_id = get_data(slug)
            centro_spalla = create_pagina_object(url)
            blocco_centrale = centro_spalla['blocco_centrale']
            spalla_destra = centro_spalla['spalla_destra']
            if not blocco_centrale:
                logger.error("Scraping fallito: blocco_centrale vuoto. Aggiornamento Strapi annullato per evitare sovrascrittura.")
                return
            update_data(document_id, blocco_centrale, spalla_destra)
            scrivi_report_excel(url.replace("https://www.carabinieri.it/", "").replace("/" + slug, ""), url, slug)                
        except Exception as e:
            logger.error(f"Errore durante la creazione o l'inserimento della pagina: {e}")
        #recupera html concorso e associa i cod
        """ try:
            document_id = 'y7lnxy37b2azfb1fbojg0qw9'
            bando_ids = []
            annullamento_ids = []
            documentiCorrelati_ids = []
            normeTecniche_ids = []
            avvisi_ids = []
            esiti_ids = []
            spalla_destra = retrive_html_block(url, "docboxRight")
            docs = parse_html_block(spalla_destra, 'div', 'docAllegati')

            # estrai il folder path dal primo href disponibile e carica la mappa dei doc
            doc_map = {}
            for blocco in docs:
                tag_a = blocco.find('a')
                if tag_a and 'href' in tag_a.attrs:
                    first_url = tag_a['href'].replace('https://www.carabinieri.it/docs/default-source', '/docs/uploads').split('?')[0]
                    folder_path = '/'.join(first_url.split('/')[:-1])
                    doc_map = get_docs_in_folder(folder_path)
                    break

            for blocco in docs:
                tipo_doc = blocco.find('span', class_='TitoloListaAllegati')
                for tag_a in blocco.find_all('a'):
                    if 'href' not in tag_a.attrs:
                        continue
                    normalized_url = tag_a['href'].replace('https://www.carabinieri.it/docs/default-source', '/docs/uploads').split('?')[0]
                    doc_id = find_doc_id_in_map(doc_map, normalized_url)
                    if doc_id is None:
                        continue

                    match tipo_doc.text.strip():
                        case "Bando di concorso":
                            bando_ids.append(doc_id)
                        case "Annullamento":
                            annullamento_ids.append(doc_id)
                        case "Documenti Correlati":
                            documentiCorrelati_ids.append(doc_id)
                        case "Norme Tecniche":
                            normeTecniche_ids.append(doc_id)
                        case "Avvisi":
                            avvisi_ids.append(doc_id)
                        case "Esiti":
                            esiti_ids.append(doc_id)

            print(document_id, bando_ids, annullamento_ids, documentiCorrelati_ids, normeTecniche_ids, avvisi_ids, esiti_ids)
            update_concorso(document_id, bando_ids, annullamento_ids, documentiCorrelati_ids, normeTecniche_ids, avvisi_ids, esiti_ids)
        except Exception as e:
            logger.error(f"Errore durante l'associazione dei codici al concorso: {e}")  """

if __name__ == "__main__":
    main()

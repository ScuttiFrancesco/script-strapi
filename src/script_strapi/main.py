"""Entry point principale dello script."""

from __future__ import annotations;

import logging;
import os;
from articoli import *
import time;
from strapi_service import *;

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

#slug = "09-umorismo"
lista_slug = [
   
    "incarichi-conferiti-e-autorizzati-ai-dipendenti-dirigenti-e-non-dirigenti"
   
]
#slug = "anafim"
lista = [
    "un-episodio-del-brigantaggio-pseudo-politico-del-1862",
    "la-banda-insurrezionale-dellex-cuoco",
    "il-brigantaggio-in-sicilia",
    "un-sottotenente-e-tre-malfattori",
    "un-capitano-impavido",
    "un-masnadero-modello",
    "eran-figli-del-popolo-erano-contadini-difendevano-la-societa",
    "alla-stazione-di-chiavari",
    "gli-eroi-della-filantropia",
    "i-carabinieri-del-1885-lanno-del-colera",
    "una-notte-a-casteldaccia",
    "brigantaggio-moribondo",
    "luccisione-del-brigante-rinaldi",
    "lo-scontro-col-brigante-sanna-e-la-morte-del-tenente-palmas",
    "fine-di-domenico-tiburzi-brigante-maremmano",
    "i-carabinieri-e-il-re-della-macchia",
    "la-fine-del-brigantaggio-maremmano",
    "il-tenente-e-il-latitante",
    "la-battaglia-del-cap-petella",
    "carabinieri-e-briganti",
    "un-maresciallo-dei-carabinieri-decorato-della-medaglia-al-valore",
    "il-merito-del-capitano-fabbroni",
    "la-cattura-del-bandito-musolino",
    "il-moretto-e-il-biondin",
    "nella-campagna-di-novara",
    "il-leggendario-gasco",
    "il-processo-cuocolo",
    "i-personaggi-della-camorra",
    "i-carabinieri-finti-camorristi",
    "nel-primo-centenario-dei-reali-carabinieri",
    "cimenti-eroismi-ideali-1814-1914",
    "siamo-vivi-perche-lui-volle-morire-per-noi",
    "salvo-dacquisto-eroe-e-martire-cristiano",
    "i-carabinieri-durante-loccupazione-nazista-da-fertilia-alle-fosse-ardeatine",
]
MAX_RETRIES = 5
RETRY_DELAY = 10  # secondi

def main() -> None:
    doc_bloc = None
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
        update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"])

    for item in lista:
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
        time.sleep(2)  
    """ articoli = get_articoli()
        for articolo in articoli:
        if '<img ' in articolo['testo']:
            print(get_image_id(articolo['testo']))
            link_image_to_articolo(articolo['documentId'], get_image_id(articolo['testo'])) """

if __name__ == "__main__":
    main()
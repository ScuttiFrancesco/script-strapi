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

slug = "anafim"

MAX_RETRIES = 5
RETRY_DELAY = 10  # secondi

def main() -> None:
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

    """ articoli = get_articoli()
        for articolo in articoli:
        if '<img ' in articolo['testo']:
            print(get_image_id(articolo['testo']))
            link_image_to_articolo(articolo['documentId'], get_image_id(articolo['testo'])) """

if __name__ == "__main__":
    main()
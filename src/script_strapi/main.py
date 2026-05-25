"""Entry point principale dello script."""

from __future__ import annotations;

import logging;
import os;
from strapi_service import *;

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

slug = ""

def main() -> None:   
    doc_bloc = get_data(slug)
    if not doc_bloc:
        logger.error("Impossibile recuperare i dati da Strapi. Aggiornamento annullato.")
        return
    if not doc_bloc["blocco_centrale"] and not doc_bloc["spalla_destra"]:
        logger.error("Contenuto Strapi vuoto (probabilmente il retrieve URL non ha salvato correttamente). Aggiornamento annullato.")
        return
    update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"]) 

if __name__ == "__main__":
    main()
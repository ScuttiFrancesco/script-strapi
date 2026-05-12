"""Entry point principale dello script."""

from __future__ import annotations

import logging
import os
from strapi_fields import strapi_fields as sf
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
url = 'https://www.carabinieri.it/media---comunicazione/rassegna-dell-arma/informazioni'
slug = 'informazioni-1'

def main() -> None:   
        try:
            document_id = get_data(slug)
            centro_spalla = create_pagina_object(url)
            blocco_centrale = centro_spalla['blocco_centrale']
            spalla_destra = centro_spalla['spalla_destra']
            update_data(document_id, blocco_centrale, spalla_destra)
        except Exception as e:
            logger.error(f"Errore durante la creazione o l'inserimento della pagina: {e}")

if __name__ == "__main__":
    main()

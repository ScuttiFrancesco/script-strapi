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
url = 'https://www.carabinieri.it/in-vostro-aiuto/amm-trasp/amm-trasp-cc/bandi-di-gara-e-contratti/atti-amm-aggiudicatrici/atti-relativi-alle-procedure/2018-(ii-sem.)'

def main() -> None:   
        try:
           lista_files = parse_righe_tabella(url)
           for i, file_path in enumerate(lista_files):
                file_info = insert_file(file_path)
                slug = file_info['name'].split('.')[0]
                file_id = file_info['file_id']
                documentId = get_data(slug)
                update_data(documentId, file_id)
                if i >= 1:  
                    break
        except Exception as e:
            logger.error(f"Errore durante la creazione o l'inserimento dell'atto: {e}")

if __name__ == "__main__":
    main()

"""Entry point principale dello script."""

from __future__ import annotations

import logging
import os
import time
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
document_id_padre = 'm27nsj2yfbzobjp8yr02fhpe'  
mostraInMenu = ['header']

def ciclo_ricorsivo(array: list, parent_id: str) -> None:
    for index, item in enumerate(array):
        # item è {"-P-Titolo": [...figli...]}
        title = list(item.keys())[0]
        children = item[title]
        strapi_object = vars(create_pagina_object(title, (index + 1), parent_id, mostraInMenu))
        new_id = insert(collection_name, strapi_object)
        if new_id:
            logger.info(f"Pagina---->{title} <----inserita con successo.")
            if children:
                ciclo_ricorsivo(children, new_id)
        else:
            logger.error(f"******ATTENZIONE*******Errore durante l'inserimento della pagina---->{title} <----.")
        time.sleep(2)

def main() -> None:   
        try:
            for index, pag in enumerate(lista.keys()):
                strapi_object = vars(create_pagina_object(pag, (index + 1), document_id_padre, mostraInMenu))
                new_id = insert(collection_name, strapi_object)
                if new_id:
                    logger.info(f"Pagina---->{pag} <----inserita con successo.")
                    if lista[pag]:
                        ciclo_ricorsivo(lista[pag], new_id)
                else:
                    logger.error(f"******ATTENZIONE*******Errore durante l'inserimento della pagina---->{pag} <----.")
                time.sleep(2)
        except Exception as e:
            logger.error(f"Errore durante la creazione o l'inserimento della pagina: {e}")

if __name__ == "__main__":
    main()

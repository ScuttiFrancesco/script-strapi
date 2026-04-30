"""Entry point principale dello script."""

from __future__ import annotations


import json
import logging
import os
import time
from strapi_fields import strapi_fields as sf
from dotenv import load_dotenv
from strapi_service import *
from deserialize_excel import deserialize_excel, create_strapi_object
from strapi_obj import *

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

collection_name = input("Inserisci il nome della collection Strapi da popolare(pluralName): ")
if collection_name not in sf:
    print("Nome della collection non valido.")
    exit(1)

def ciclo_ricorsivo(array: list, parent_id: str) -> None:
    for index, item in enumerate(array):
        # item è {"-P-Titolo": [...figli...]}
        title = list(item.keys())[0]
        children = item[title]
        strapi_object = vars(create_pagina_object(title, (index + 1), parent_id))
        new_id = insert(collection_name, strapi_object)
        if new_id:
            logger.info(f"Pagina---->{title} <----inserita con successo.")
            if children:
                ciclo_ricorsivo(children, new_id)
        else:
            logger.error(f"******ATTENZIONE*******Errore durante l'inserimento della pagina---->{title} <----.")
        time.sleep(2)

def main() -> None:   
    if collection_name != 'paginas': 
        df = deserialize_excel(collection_name)
        inseriti = 0
        falliti = 0

        if df is not None:
            for dict in df.iloc:
                try:
                    strapi_object = create_strapi_object(collection_name, dict.to_dict())
                    if insert(collection_name, strapi_object):
                        inseriti += 1
                    else:
                        falliti += 1
                except Exception as e:
                    logger.warning(f"Record saltato per errore: {e}")
                    falliti += 1
                time.sleep(2)
        logger.info(f"Record inseriti: {inseriti}, Record falliti: {falliti}")
    else:
        try:
            for index, pag in enumerate(lista.keys()):
                strapi_object = vars(create_pagina_object(pag, (index + 1), 'ruib9v0ouejy8j8r959kodhc'))
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

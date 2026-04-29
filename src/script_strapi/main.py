"""Entry point principale dello script."""

from __future__ import annotations


import logging
import os
import time
from strapi_fields import strapi_fields as sf
from dotenv import load_dotenv
from strapi_service import insert
from deserialize_excel import deserialize_excel, create_strapi_object

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

def main() -> None:    
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

if __name__ == "__main__":
    main()

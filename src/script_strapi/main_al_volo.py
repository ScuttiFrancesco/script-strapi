"""Entry point principale dello script."""

from __future__ import annotations


import json
from slugify import slugify
import logging
import os
import re
from deserialize_excel_concorsi import create_strapi_object_concorsi, deserialize_excel_concorsi
from strapi_fields import strapi_fields as sf
from dotenv import load_dotenv
from strapi_service import *


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# "esiti"/"esito" come segmento intero dello slug (inizio, metà o fine), col trattino che lo precede
ESITO_RE = re.compile(r'(^|-)esit[io](?=-|$)')


def is_esito(slug: str) -> bool:
    return bool(ESITO_RE.search(slug))


def slug_senza_esito(slug: str) -> str:
    """esiti-prova-scritta -> prova-scritta, prova-orale-esito -> prova-orale"""
    return ESITO_RE.sub('', slug).strip('-')


def main() -> None:

    params = {
        'fields[0]': 'codiceConcorso',
        "pagination[page]": 1,
        "pagination[pageSize]": "500"
    }
    concorsi = get_data_strapi('concorsis', params)
    for concorso in concorsi:
        codice_concorso = concorso['codiceConcorso']        
        prove_params = {
            'filters[concorsis][codiceConcorso]': codice_concorso,
            'pagination[page]': 1,
            'pagination[pageSize]': 500
        }
        prove = get_data_strapi('concorso-provas', prove_params)
        prove_esiti = [p for p in prove if is_esito(p['slug'])]
        if not prove_esiti: continue

        # prove "normali" indicizzate per slug, per il match con gli esiti
        prove_by_slug = {p['slug']: p for p in prove if not is_esito(p['slug'])}

        # coppie (esito, prova): es. esiti-prova-scritta -> prova-scritta
        prove_con_esito: list[tuple[dict, dict]] = []
        for esito in prove_esiti:
            slug_prova = slug_senza_esito(esito['slug'])
            prova = prove_by_slug.get(slug_prova)
            if prova is None:
                logger.warning("%s: nessuna prova '%s' per l'esito '%s'", codice_concorso, slug_prova, esito['slug'])
                continue
            prove_con_esito.append((esito, prova))

        for esito in prove_con_esito:
            documentId_esito = esito[0]['documentId']
            documentId_prova = esito[1]['documentId']
            data_esito = {'tipologia': 'esito'}
            data_prova = {'tipologia': 'esito-con-prova'}
            put_al_volo(data_esito, documentId_esito, 'concorso-provas')
            put_al_volo(data_prova, documentId_prova, 'concorso-provas')

       
if __name__ == "__main__":
    main()

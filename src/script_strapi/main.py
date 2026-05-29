"""Entry point principale dello script."""

from __future__ import annotations;

import logging;
import os;
from articoli import *
from strapi_service import *;

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

slug = "carta-telefonica-2005"

def main() -> None:   
    """ doc_bloc = get_data(slug)
    update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"])  """
    articoli = get_articoli()
    for articolo in articoli:
        if '<img ' in articolo['testo']:
            print(get_image_id(articolo['testo']))
            link_image_to_articolo(articolo['documentId'], get_image_id(articolo['testo']))
if __name__ == "__main__":
    main()
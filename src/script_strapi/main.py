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

def main() -> None:   
    doc_bloc = get_data("il-carabiniere")
    update_data(doc_bloc["documentId"], doc_bloc["blocco_centrale"], doc_bloc["spalla_destra"]) 

if __name__ == "__main__":
    main()
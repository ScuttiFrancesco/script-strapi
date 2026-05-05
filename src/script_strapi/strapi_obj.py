from strapi_interfaces import Pagina as pg

def create_pagina_object(title: str, index: int, document_id: str) -> pg:
    """Crea un oggetto Pagina a partire dai parametri."""
    relation = {
        'connect': [
            {
                'documentId': document_id,
                'status': 'published'
            }
        ]
    }
    menu = [
            {
                '__component': 'widget.menu',
            }
        ]
    contenuto = [
            {
                '__component': 'shared.contenuto'
            }
    ]
    title_parsed = title.removeprefix('-W-').removeprefix('-P-')
    tipo_layout = 'wrapper' if title.startswith('-W-') else 'pagina'
    return pg(title_parsed, index, tipo_layout, relation, '2026-01-01', None, title_parsed, menu, contenuto)

lista =  {
    "-P-Codice Rosso": [],
    "-P-Una stanza tutta per sé": [],
    "-P-Gioco da tavolo": []
}
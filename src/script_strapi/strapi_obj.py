from strapi_interfaces import Pagina as pg

def create_pagina_object(title: str, index: int, document_id: str, mostra_in_menu: str) -> pg:
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
    return pg(title_parsed, index, tipo_layout, relation, '2026-01-01', None, title_parsed, menu, contenuto, mostra_in_menu)

lista =  { "-P-Enti pubblici vigilati": [] ,
    "-P-Società partecipate": [] ,
    "-P-Enti di diritto privato controllati": [] ,
    "-P-Rappresentazione grafica": [] 
}
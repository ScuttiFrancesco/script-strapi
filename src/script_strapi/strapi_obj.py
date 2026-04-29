from strapi_interfaces import Pagina as pg

def create_pagina_object(title: str, index: int) -> pg:
    """Crea un oggetto Pagina a partire dai parametri."""
    relation = {
        'connect': [
            {
                'documentId': 'rp3jgfrf3mxkf5q2h2dtvu1x',
                'status': 'published'
            }
        ]
    }
    return pg(title, index, 'wrapper', relation, '2026-01-01')

lista = [
"Ambiente e Istituzioni",
"Danno ambientale e bonifiche",
"Rifiuti",
"Sanzioni amministrative ambientali",
"Tecnica polizia giudiziaria ambientale",
"Tutela animali e caccia/pesca",
"Tutela territorio e aree protette"]
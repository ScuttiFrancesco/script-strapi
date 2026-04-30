from strapi_interfaces import Pagina as pg

def create_pagina_object(title: str, index: int, document_id: str, ) -> pg:
    """Crea un oggetto Pagina a partire dai parametri."""
    relation = {
        'connect': [
            {
                'documentId': document_id,
                'status': 'published'
            }
        ]
    }
    title_parsed = title.removeprefix('-W-').removeprefix('-P-')
    tipo_layout = 'wrapper' if title.startswith('-W-') else 'pagina'
    return pg(title_parsed, index, tipo_layout, relation, '2026-01-01', None)

lista =  {
  "-W-Anno 2026": [
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2025": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N. 2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2024": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Speciale I Martiri di Fiesole": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2023": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Speciale 'Le 4 Giornate di Napoli'": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2022": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2021": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2020": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2019": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2018": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2017": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Speciale 9 maggio": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ],
  "-W-Anno 2016": [
    { "-P-Notiziario N.6": [] },
    { "-P-Notiziario N.5": [] },
    { "-P-Notiziario N.4": [] },
    { "-P-Notiziario N.3": [] },
    { "-P-Notiziario N.2": [] },
    { "-P-Notiziario N.1": [] }
  ]
}


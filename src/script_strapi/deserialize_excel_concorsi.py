import pandas as pd
import os
from strapi_interfaces import AppuntamentiStoria as ap
from strapi_fields import strapi_fields as sf
from category_map import categories as cat

EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", "C:/Users/francesco.scutti/Desktop/strapi-file/")

def deserialize_excel_concorsi(collection_name: str):
    full_path = EXCEL_FILE_PATH + collection_name + ".xlsx"
    """Deserializza un file Excel in un DataFrame."""
    try:
        df = pd.read_excel(full_path)
        unset = set(df.keys())
        for field in sf[collection_name]:
            if field in unset:
                return df
                      
    except Exception as e:
        print(f"Errore durante la deserializzazione del file Excel: {e}")
        return None

def create_strapi_object_concorsi(collection_name: str, data: dict):
    """Crea un oggetto Strapi a partire da un dizionario."""
    if data['tipoOggettoFiglio'] == 'Prova' and collection_name != 'concorso-provas':
        return
    if data['tipoOggettoFiglio'] == 'Novità' and collection_name != 'concorso-novitas':
        return
    if data['tipoOggettoFiglio'] == 'Pubblico Proclama' and collection_name != 'concorso-pubblico-proclamas':
        return
    strapi_object = dict()
    for key in sf[collection_name].keys(): 
                if key == 'titoloProva' or key == 'titoloNovita' or key == 'titoloProclamo':
                    strapi_object['title'] = fields_validation_concorsi(key, collection_name, data[key])
                elif key == 'azioneLink':
                    strapi_object['azioneLink'] = fields_validation_concorsi(key, collection_name, data[key])
                else:           
                    strapi_object[key] = fields_validation_concorsi(key, collection_name, data[key])
    return strapi_object

def fields_validation_concorsi(field : str, collection_name: str, value) :
    """Valida un campo in base allo schema Strapi."""
    if field == 'azioneLink':
        return azione_link_mapping(value)
    field_type = sf[collection_name].get(field)
    if field_type is not None:
        if pd.isna(value) or value == '' or value == 'NULL' or value == 'null':
            return None
        match field_type.__name__:
            case 'int':
                return int(value)
            case 'float':
                return float(value)
            case 'bool':
                if str(value).lower() in ['true', '1', '1.0']:
                    return True
                elif str(value).lower() in ['false', '0', '0.0']:
                    return False
                else:
                    raise ValueError(f"Il campo '{field}' ha un valore booleano non valido: {value}")
            case 'dict':
                result = create_strapi_relation_concorsi(value)
                return result
            case _:
                return str(value)        
    else:    
        raise ValueError(f"Il campo '{field}' non è previsto dallo schema Strapi.")

def create_strapi_relation_concorsi(documentId: str):    
    if documentId is not None:
        pagina = dict(connect=[
            dict({
                'documentId': documentId,
                'status': 'published'
            })
        ])
        return pagina
    else:
        raise ValueError(f"errore nella creazione della relazione, documentId non valido: {documentId}")

def azione_link_mapping(azione: int) -> str:
    mapping = {
        1: "nessuna",
        2: "concorsi-online",
        3: "apri-pdf",
        4: "database",
        5: "simulatore",
        6: "simulatore-vecchio",
        7: "concorsi-online-vecchio"
    }
    return mapping.get(azione, "Azione non valida")
    
    
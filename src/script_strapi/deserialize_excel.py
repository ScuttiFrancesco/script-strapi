import pandas as pd
import os
from strapi_interfaces import AppuntamentiStoria as ap
from strapi_fields import strapi_fields as sf
from category_map import categories as cat

EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", "C:/Users/francesco.scutti/Desktop/strapi-file/")

def deserialize_excel(collection_name: str):
    full_path = EXCEL_FILE_PATH + collection_name + ".xlsx"
    """Deserializza un file Excel in un DataFrame."""
    try:
        df = pd.read_excel(full_path)
        unset = set(df.keys())
        for field in sf[collection_name]:
            if field in unset:
                return df
            else:
                raise ValueError(f"Il campo '{field}' è presente nel file Excel, ma non è previsto dallo schema Strapi.")           
    except Exception as e:
        print(f"Errore durante la deserializzazione del file Excel: {e}")
        return None

def create_strapi_object(collection_name: str, data: dict):
    """Crea un oggetto Strapi a partire da un dizionario."""
    strapi_object = dict()
    for key in sf[collection_name].keys():
            strapi_object[key] = fields_validation(key, collection_name, data[key])
    return strapi_object

def fields_validation(field : str, collection_name: str, value) :
    """Valida un campo in base allo schema Strapi."""
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
                if str(value).lower() in ['true', '1']:
                    return True
                elif str(value).lower() in ['false', '0']:
                    return False
                else:
                    raise ValueError(f"Il campo '{field}' ha un valore booleano non valido: {value}")
            case 'dict':
                result = create_strapi_relation(field, collection_name, value)
                return result
            case _:
                return str(value)        
    else:    
        raise ValueError(f"Il campo '{field}' non è previsto dallo schema Strapi.")

def create_strapi_relation(field: str, collection_name: str, value):
    """Recupera la relazione Strapi a partire dallo slug."""
    documentId = cat.get(collection_name, {}).get(value)
    if documentId is not None:
        category = dict(connect=[
            dict({
                'documentId': documentId,
                'status': 'published'
            })
        ])
        return category
    else:
        raise ValueError(f"Il campo '{field}' ha un valore di relazione non valido: {value}")
    
    
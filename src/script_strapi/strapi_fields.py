strapi_fields = {
    'amministrazione-trasparente-collaboraziones': {'datiFiscali': str, 'unitaAmministrativa': str, 'denominazione': str, 'oggettoIncarico': str, 'estremiAttoConferimentoIncarico': str, 'importoCompenso': str, 'incarichiAltrePA': str, 'retribuzioneDiRisultato': str, 'annoRiferimento': str, 'dataInizio': str, 'dataFine': str, 'publicationDate': str},
    'appuntamenti-storias': {'title': str, 'data': str, 'testo': str, 'linkUtili': str, 'publicationDate': str},
    'medaglies': {'title': str, 'grado': str, 'dataConcessione': str, 'dataLuogoNascita': str, 'dataLuogoMorte': str, 'dataLuogoFatto': str, 'motivazione': str, 'note': str, 'linkUtili': str, 'categoria_medaglieres': dict, 'publicationDate': str},
    'concrso-faqs': {'numero': int, 'titolo': str, 'risposta': str, 'domanda': str, 'richiedente': str, 'categoria_faqs': dict, 'publicationDate': str},
    'attis': {'title': str, 'titolo': str, 'cig': str, 'data': str, 'note': str, 'categoria_attis': dict, 'publicationDate': str},
    'concorsis': { 'titolo': str, 'stato': str,'numero': int, 'dataInizio': str, 'dataScadenzaDomanda': str, 'ruolo': str, 'mostraBoxPrenotaOnline': bool, 'tipologia': str, 'posti': str, 'sottotitolo': str, 'codiceConcorso': str, 'descrizione': str, 'listaLink': str, 'publicationDate': str},
    # VERIFICARE SE VIENE PASSATO IL CAMPO CATEGORIA-COCERS E IN CASO AGGIUNGERLO
    'comunicazioni-cocers': {'title': str, 'fonteTestoLibero': str, 'listaLink': str, 'fonte': str, 'contenuto': str, 'publicationDate': str},  
    'contattis': {'title': str, "telefono": str, 'sede': str, 'postaElettronicaCertificata': str, 'fax': str, 'email': str, 'publicationDate': str},
    'entis': {'title': str, 'filePrimoTrimestre': str, 'fileSecondoTrimestre': str, 'fileTerzoTrimestre': str, 'fileQuartoTrimestre': str, 'publicationDate': str},
    'appuntamentis': {'title': str, 'contenuto': str, 'comune': str, 'dataInizio': str, 'dataFine': str, 'ignoraDataFine': bool, 'publicationDate': str},
    'comunicati-stampas': {'title': str, 'comune': str, 'fontePrefisso': str, 'fonte': str, 'contenuto': str, 'scadenzaAutomatica': bool, 'publicationDate': str},
    'amministrazione-trasparente-incarichi-dirigenzialis': { 'incarico': str, 'cognome': str, 'nome': str, 'compensiIncarico': str, 'indennita': str, 'rimborsi': str, 'emolumenti': str, 'grado': str, 'publicationDate': str},
    # VERIFICARE SE VIENE PASSATO IL CAMPO SLUG E IN CASO AGGIUNGERLO
    'gare-appaltos': {'title': str, 'anno': int, 'codiceCig': str, 'codiceUnivoco': str, 'idGara': str, 'dataInizio': str, 'dataScadenza': str, 'statoPostScadenza': str, 'descrizione': str, 'enteAppaltante': str, 
                      'oggettoProcedura': str, 'sceltaContraente': str, 'protocollo': str, 'fonte': str, 'fonteLista': str, 'listaLink': str, 'numero': int, 'importo': float, 'publicationDate': str},
    'ordini-giornos': {'title': str, 'comune': str, 'publicationDate': str}
}

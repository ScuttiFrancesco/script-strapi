class AppuntamentiStoria:
    def __init__(self, title: str, data: str, testo: str, linkUtili: str, publicationDate: str) -> None:
        self.title = title
        self.data = data
        self.testo = testo
        self.linkUtili = linkUtili
        self.publicationDate = publicationDate

class AmministrazioneTrasparenteCollaborazione:
    def __init__(self, datiFiscali: str, unitaAmministrativa: str, denominazione: str, oggettoIncarico: str, estremiAttoConferimentoIncarico: str, importoCompenso: str, incarichiAltrePA: str, retribuzioneDiRisultato: str, annoRiferimento: str, dataInizio: str, dataFine: str, publicationDate: str) -> None:
        self.datiFiscali = datiFiscali
        self.unitaAmministrativa = unitaAmministrativa
        self.denominazione = denominazione
        self.oggettoIncarico = oggettoIncarico
        self.estremiAttoConferimentoIncarico = estremiAttoConferimentoIncarico
        self.importoCompenso = importoCompenso
        self.incarichiAltrePA = incarichiAltrePA
        self.retribuzioneDiRisultato = retribuzioneDiRisultato
        self.annoRiferimento = annoRiferimento
        self.dataInizio = dataInizio
        self.dataFine = dataFine
        self.publicationDate = publicationDate

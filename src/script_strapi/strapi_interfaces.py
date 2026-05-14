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

class Pagina:
    def __init__(self, title: str, ordineVisualizzazioneMenu: int, tipoLayout: str = 'wrapper', pagina: dict = None, publishedAt: str = '2026-01-01', slug: str = None, titolo: str = None, spalla_destra: list = None, blocco_centrale: list = None, mostraInMenu: list = None) -> None:
        self.title = title
        self.ordineVisualizzazioneMenu = ordineVisualizzazioneMenu
        self.tipoLayout = tipoLayout
        self.pagina = pagina
        self.publishedAt = publishedAt
        self.slug = slug
        self.titolo = titolo
        self.spalla_destra = spalla_destra
        self.blocco_centrale = blocco_centrale
        self.mostraInMenu = mostraInMenu

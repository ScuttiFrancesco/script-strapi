# script-strapi

Script Python per l'automazione di Strapi.

## Setup

```bash
# 1. Crea il virtual environment
python -m venv .venv

# 2. Attivalo
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Installa le dipendenze di sviluppo (opzionale)
pip install -r requirements-dev.txt

# 5. Configura le variabili d'ambiente
copy .env.example .env   # Windows
# oppure
cp .env.example .env     # Linux / macOS
# poi modifica .env con i tuoi valori
```

## Esecuzione

```bash
python -m script_strapi.main
```

## Test

```bash
pytest
```

## Linting

```bash
ruff check src tests
ruff format src tests
```

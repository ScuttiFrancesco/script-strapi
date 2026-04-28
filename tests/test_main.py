"""Test per il modulo main."""

from script_strapi.main import main


def test_main_runs(monkeypatch):
    monkeypatch.setenv("STRAPI_BASE_URL", "http://localhost:1337")
    monkeypatch.setenv("STRAPI_API_TOKEN", "test-token")
    main()  # non deve sollevare eccezioni

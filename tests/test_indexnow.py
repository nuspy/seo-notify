from __future__ import annotations

import json
import urllib.error

import pytest

from seo_notify import ClientIndexNow, RisultatoIndexNow, genera_chiave, nome_file_chiave


def test_genera_chiave_e_nome_file_coerenti():
    chiave = genera_chiave()
    assert len(chiave) == 32  # token_hex(16) -> 32 caratteri esadecimali
    assert nome_file_chiave(chiave) == f"{chiave}.txt"


def test_key_location_predefinita():
    client = ClientIndexNow("example.com", "abc123")
    assert client.key_location == "https://example.com/abc123.txt"


def test_invia_richiede_almeno_un_url():
    client = ClientIndexNow("example.com", "abc123")
    with pytest.raises(ValueError):
        client.invia([])


def test_invia_rifiuta_troppi_url():
    client = ClientIndexNow("example.com", "abc123")
    with pytest.raises(ValueError):
        client.invia([f"https://example.com/{i}" for i in range(10_001)])


class _RispostaFinta:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_invia_ok_su_200(monkeypatch):
    catturato = {}

    def urlopen_finto(richiesta, timeout=None):
        catturato["payload"] = json.loads(richiesta.data.decode("utf-8"))
        catturato["url"] = richiesta.full_url
        return _RispostaFinta(200)

    monkeypatch.setattr("seo_notify.indexnow.urllib.request.urlopen", urlopen_finto)
    client = ClientIndexNow("example.com", "abc123")
    risultato = client.invia_uno("https://example.com/articolo")

    assert risultato == RisultatoIndexNow(ok=True, endpoint=client.endpoint, codice_stato=200)
    assert catturato["payload"] == {
        "host": "example.com", "key": "abc123",
        "keyLocation": "https://example.com/abc123.txt",
        "urlList": ["https://example.com/articolo"],
    }


def test_invia_accetta_202_in_coda(monkeypatch):
    def urlopen_finto(richiesta, timeout=None):
        raise urllib.error.HTTPError(richiesta.full_url, 202, "Accepted", {}, None)

    monkeypatch.setattr("seo_notify.indexnow.urllib.request.urlopen", urlopen_finto)
    client = ClientIndexNow("example.com", "abc123")
    risultato = client.invia_uno("https://example.com/articolo")

    assert risultato.ok is True
    assert risultato.codice_stato == 202


def test_invia_segnala_errore_4xx(monkeypatch):
    def urlopen_finto(richiesta, timeout=None):
        raise urllib.error.HTTPError(richiesta.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr("seo_notify.indexnow.urllib.request.urlopen", urlopen_finto)
    client = ClientIndexNow("example.com", "abc123")
    risultato = client.invia_uno("https://example.com/articolo")

    assert risultato.ok is False
    assert risultato.codice_stato == 403

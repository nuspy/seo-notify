from __future__ import annotations

import urllib.error
import urllib.parse

from seo_notify import notifica_hub
from seo_notify.websub import HUB_PUBBLICO_PREDEFINITO


class _RispostaFinta:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_notifica_hub_ok(monkeypatch):
    catturato = {}

    def urlopen_finto(richiesta, timeout=None):
        catturato["url"] = richiesta.full_url
        catturato["corpo"] = urllib.parse.parse_qs(richiesta.data.decode("ascii"))
        return _RispostaFinta(204)

    monkeypatch.setattr("seo_notify.websub.urllib.request.urlopen", urlopen_finto)
    risultato = notifica_hub("https://tarots.chat/blog/feed.xml")

    assert risultato.ok is True
    assert risultato.hub == HUB_PUBBLICO_PREDEFINITO
    assert catturato["corpo"] == {
        "hub.mode": ["publish"], "hub.url": ["https://tarots.chat/blog/feed.xml"],
    }


def test_notifica_hub_errore(monkeypatch):
    def urlopen_finto(richiesta, timeout=None):
        raise urllib.error.URLError("connessione rifiutata")

    monkeypatch.setattr("seo_notify.websub.urllib.request.urlopen", urlopen_finto)
    risultato = notifica_hub("https://tarots.chat/blog/feed.xml", hub="https://hub.example.com/")

    assert risultato.ok is False
    assert "rifiutata" in (risultato.errore or "")

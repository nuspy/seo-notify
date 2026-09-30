"""Client minimale per il protocollo IndexNow (https://www.indexnow.org).

Supportato da Bing, Yandex, Naver, Seznam.cz e altri — non da Google (che ha il proprio meccanismo,
vedi `search_console.py`). Scritto senza dipendenze esterne: un POST JSON, niente di più — non c'è
libreria matura da cui dipendere che valga la candela (ricerca del 2026-09-30: le uniche trovate su
GitHub hanno poche stelle o non sono ancora rilasciate).
"""
from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional, Sequence

#: L'endpoint aggregatore: IndexNow lo propaga agli altri motori partecipanti. Un motore specifico
#: (es. `https://www.bing.com/indexnow`) funziona allo stesso modo, se si preferisce non passare
#: dall'aggregatore.
ENDPOINT_PREDEFINITO = "https://api.indexnow.org/indexnow"

#: IndexNow rifiuta richieste con più URL di questi (specifica del protocollo).
MASSIMO_URL_PER_RICHIESTA = 10_000


@dataclass(frozen=True)
class RisultatoIndexNow:
    ok: bool
    endpoint: str
    codice_stato: Optional[int] = None
    errore: Optional[str] = None


def genera_chiave() -> str:
    """Una chiave nuova, esadecimale: IndexNow ne accetta una fra 8 e 128 caratteri."""
    return secrets.token_hex(16)


def nome_file_chiave(chiave: str) -> str:
    """Il nome del file statico da servire alla radice del sito, es. `<chiave>.txt`. Il suo
    contenuto è la chiave stessa, nient'altro: è così che IndexNow verifica che il sito è tuo."""
    return f"{chiave}.txt"


class ClientIndexNow:
    """Un host, una chiave, un endpoint. Il file di verifica (`nome_file_chiave(chiave)`, contenuto
    = `chiave`) deve essere raggiungibile su `key_location` PRIMA della prima chiamata a `invia()` —
    la libreria non lo serve da sola, è compito di chi la usa (un file statico, una piccola route)."""

    def __init__(
        self, host: str, chiave: str, *,
        key_location: Optional[str] = None, endpoint: str = ENDPOINT_PREDEFINITO, timeout: float = 10.0,
    ) -> None:
        self.host = host
        self.chiave = chiave
        self.key_location = key_location or f"https://{host}/{nome_file_chiave(chiave)}"
        self.endpoint = endpoint
        self.timeout = timeout

    def invia(self, urls: Sequence[str]) -> RisultatoIndexNow:
        """Notifica uno o più URL nuovi/aggiornati. Una singola chiamata copre fino a 10.000 URL:
        per un blog, di solito un solo URL alla volta (l'articolo appena pubblicato)."""
        if not urls:
            raise ValueError("invia() richiede almeno un URL")
        if len(urls) > MASSIMO_URL_PER_RICHIESTA:
            raise ValueError(f"IndexNow accetta al massimo {MASSIMO_URL_PER_RICHIESTA} URL per richiesta")

        corpo = json.dumps({
            "host": self.host,
            "key": self.chiave,
            "keyLocation": self.key_location,
            "urlList": list(urls),
        }).encode("utf-8")
        richiesta = urllib.request.Request(
            self.endpoint, data=corpo, method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(richiesta, timeout=self.timeout) as risposta:
                codice = risposta.status
                return RisultatoIndexNow(ok=200 <= codice < 300, endpoint=self.endpoint, codice_stato=codice)
        except urllib.error.HTTPError as exc:
            # IndexNow usa anche 202 (accettato, in coda) — non è un errore.
            return RisultatoIndexNow(
                ok=exc.code == 202, endpoint=self.endpoint, codice_stato=exc.code, errore=str(exc),
            )
        except urllib.error.URLError as exc:
            return RisultatoIndexNow(ok=False, endpoint=self.endpoint, errore=str(exc.reason))

    def invia_uno(self, url: str) -> RisultatoIndexNow:
        return self.invia([url])

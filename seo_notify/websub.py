"""Notifica WebSub (ex PubSubHubbub, https://websub.rocks/): dice a un hub che un feed RSS/Atom è
appena cambiato, cosí gli abbonati (lettori, aggregatori) lo vedono senza dover fare polling. Non è
indicizzazione diretta sui motori di ricerca: è complementare a `indexnow`/`search_console`, a basso
sforzo se il sito ha già un feed pubblico.

Il feed deve dichiarare l'hub scelto con un `<link rel="hub" href="...">` (Atom) o l'equivalente RSS
— è compito di chi genera il feed, non di questa libreria.
"""
from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

#: Un hub pubblico storicamente usato per WebSub, se non se ne vuole gestire uno proprio.
HUB_PUBBLICO_PREDEFINITO = "https://pubsubhubbub.appspot.com/"


@dataclass(frozen=True)
class RisultatoWebSub:
    ok: bool
    hub: str
    codice_stato: Optional[int] = None
    errore: Optional[str] = None


def notifica_hub(url_feed: str, *, hub: str = HUB_PUBBLICO_PREDEFINITO, timeout: float = 10.0) -> RisultatoWebSub:
    """`hub.mode=publish&hub.url=<url_feed>`, form-encoded, come da specifica WebSub. L'hub stesso
    va poi a leggere il feed per vedere cos'è cambiato: questa chiamata è solo l'avviso."""
    corpo = urllib.parse.urlencode({"hub.mode": "publish", "hub.url": url_feed}).encode("ascii")
    richiesta = urllib.request.Request(
        hub, data=corpo, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=timeout) as risposta:
            codice = risposta.status
            return RisultatoWebSub(ok=200 <= codice < 300, hub=hub, codice_stato=codice)
    except urllib.error.HTTPError as exc:
        return RisultatoWebSub(ok=False, hub=hub, codice_stato=exc.code, errore=str(exc))
    except urllib.error.URLError as exc:
        return RisultatoWebSub(ok=False, hub=hub, errore=str(exc.reason))

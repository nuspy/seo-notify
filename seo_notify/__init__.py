"""seo-notify: notifica ai motori di ricerca quando un contenuto è pubblicato o aggiornato.

Tre canali indipendenti, ognuno attivabile da solo:

- `indexnow`: Bing, Yandex e gli altri motori che parlano il protocollo IndexNow. Non copre Google.
- `websub`: propaga un feed RSS/Atom aggiornato a un hub WebSub (ex PubSubHubbub) — non è
  indicizzazione diretta, ma accelera la scoperta da parte di lettori/aggregatori.
- `search_console`: risottomette una sitemap a Google tramite la Search Console API
  (`sitemaps.submit`). Richiede l'extra `search-console` (`pip install seo-notify[search-console]`)
  e un service account con accesso alla proprietà in Search Console.

Deliberatamente NON implementato: la Google Indexing API (`urlNotifications`) per contenuti
generici — è ufficialmente limitata a `JobPosting`/`BroadcastEvent`, usarla per un blog qualunque è
un uso non supportato (ricerca del 2026-09-30).
"""

from .indexnow import ClientIndexNow, RisultatoIndexNow, genera_chiave, nome_file_chiave
from .websub import RisultatoWebSub, notifica_hub

__all__ = [
    "ClientIndexNow", "RisultatoIndexNow", "genera_chiave", "nome_file_chiave",
    "RisultatoWebSub", "notifica_hub",
]

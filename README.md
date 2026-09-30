# seo-notify

Notifica ai motori di ricerca quando un contenuto è pubblicato o aggiornato. Nato per TAROTS chat
(`T-AI-rots`), scritto per essere riusabile in qualunque progetto con un blog o contenuti pubblici.

Tre canali indipendenti, ognuno attivabile da solo:

| Canale | Copre | Dipendenze | Setup |
|---|---|---|---|
| `indexnow` | Bing, Yandex, Naver, Seznam.cz | nessuna (solo stdlib) | genera una chiave, servi `<chiave>.txt` alla radice del sito con quel contenuto |
| `websub` | propagazione feed RSS/Atom (non indicizzazione diretta) | nessuna | il feed deve dichiarare l'hub scelto (`<link rel="hub">`) |
| `search_console` | Google | `pip install seo-notify[search-console]` | service account con accesso alla proprietà in Search Console |

**Deliberatamente non implementato**: la Google Indexing API (`urlNotifications`) per contenuti
generici. Ricerca del 2026-09-30: resta ufficialmente limitata a `JobPosting`/`BroadcastEvent` —
usarla per un blog qualunque è un uso non supportato, rischioso da offrire come funzione di prodotto.
Il "ping" classico della sitemap (`google.com/ping?sitemap=`) è morto (404 da agosto 2026, deprecato
da Google nel 2023): `search_console.sottometti_sitemap()` è il sostituto ufficiale.

## Uso

```python
from seo_notify import ClientIndexNow, notifica_hub

# IndexNow (Bing/Yandex/...)
client = ClientIndexNow(host="tuosito.com", chiave="...")
# genera_chiave() per crearne una nuova; nome_file_chiave(chiave) dice come si chiama il file
# statico da servire alla radice del sito, con la chiave stessa come contenuto.
risultato = client.invia_uno("https://tuosito.com/blog/articolo-nuovo")
print(risultato.ok, risultato.codice_stato)

# WebSub (propagazione feed)
risultato = notifica_hub("https://tuosito.com/blog/feed.xml")
```

```python
# Search Console (Google) — richiede l'extra [search-console]
from seo_notify.search_console import sottometti_sitemap

risultato = sottometti_sitemap(
    site_url="https://tuosito.com/",
    sitemap_url="https://tuosito.com/sitemap.xml",
    service_account_file="/percorso/al/service-account.json",
)
```

## Sviluppo

```bash
pip install -e .[search-console,dev]
pytest
```

## Perché scritto in casa invece di dipendere da un pacchetto esistente

Ricerca fatta prima di scrivere questo progetto (2026-09-30): per IndexNow non esiste su GitHub una
libreria Python abbastanza matura da giustificare la dipendenza (la più stellata ne ha 8, la più
moderna/adatta a stack async non è ancora rilasciata) — il protocollo stesso è un singolo POST JSON,
scriverlo in casa è meno rischioso che dipendere da un pacchetto fragile o non mantenuto.

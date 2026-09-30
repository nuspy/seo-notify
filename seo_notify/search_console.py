"""Risottomissione della sitemap a Google tramite la Search Console API.

Il vecchio "ping" (`google.com/ping?sitemap=...`) è morto — Google lo ha deprecato nel 2023 e
l'endpoint risponde 404 da agosto 2026. Questo è il sostituto ufficiale ancora funzionante:
`sitemaps.submit`, generico per qualunque proprietà verificata (non limitato, a differenza della
Google Indexing API, a `JobPosting`/`BroadcastEvent`).

Richiede l'extra `search-console` (`pip install seo-notify[search-console]`): a differenza di
`indexnow`/`websub`, qui non si può fare a meno di una libreria — la firma OAuth2 di un service
account non è qualcosa da reimplementare in casa con lo stdlib.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

SCOPE = "https://www.googleapis.com/auth/webmasters"


@dataclass(frozen=True)
class RisultatoSearchConsole:
    ok: bool
    errore: Optional[str] = None


def sottometti_sitemap(
    *, site_url: str, sitemap_url: str, service_account_file: str,
) -> RisultatoSearchConsole:
    """`site_url` è la proprietà come registrata in Search Console (es. `https://tarots.chat/` o
    `sc-domain:tarots.chat`), `sitemap_url` l'indirizzo pubblico della sitemap,
    `service_account_file` il percorso al JSON delle credenziali di un service account con accesso
    (come utente, aggiunto dalla UI di Search Console) a quella proprietà."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError as exc:
        raise ImportError(
            "sottometti_sitemap() richiede l'extra 'search-console': "
            "pip install seo-notify[search-console]",
        ) from exc

    credenziali = service_account.Credentials.from_service_account_file(service_account_file, scopes=[SCOPE])
    servizio = build("searchconsole", "v1", credentials=credenziali, cache_discovery=False)
    try:
        servizio.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
        return RisultatoSearchConsole(ok=True)
    except HttpError as exc:
        return RisultatoSearchConsole(ok=False, errore=str(exc))

"""Shared client for the RugbyViz feeds used by PREM Rugby and EPCR.

The public feeds started requiring the same ``X-*`` headers as their official
websites in October 2026. The values are public runtime configuration, so they
are read from the relevant official fixtures page instead of being copied into
the repository and becoming stale after the next rotation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (compatible; EuropeanRugbyRanking/1.0; "
    "+https://github.com/aymft/EuropeanRugbyRanking)"
)

PUBLIC_CONFIG_PATTERN = re.compile(
    r'apiKey:"(?P<api_key>[^"]+)"\s*,\s*'
    r'realmId:"(?P<realm>[^"]+)"\s*,\s*'
    r'appId:"(?P<app_id>[^"]+)"\s*,\s*'
    r'clientId:"(?P<client_id>[^"]+)"'
)


@dataclass(frozen=True)
class RugbyVizConfig:
    api_key: str
    realm: str
    app_id: str
    client_id: str
    origin: str


def parse_rugbyviz_config(raw_html: str, page_url: str) -> RugbyVizConfig:
    """Extract the official site's public RugbyViz runtime configuration."""

    match = PUBLIC_CONFIG_PATTERN.search(raw_html)

    if not match:
        raise RuntimeError(
            f"Could not find RugbyViz public configuration on {page_url}."
        )

    parsed_url = urlsplit(page_url)
    origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

    return RugbyVizConfig(
        api_key=match.group("api_key"),
        realm=match.group("realm"),
        app_id=match.group("app_id"),
        client_id=match.group("client_id"),
        origin=origin,
    )


@lru_cache(maxsize=8)
def fetch_rugbyviz_config(fixtures_url: str) -> RugbyVizConfig:
    request = Request(
        fixtures_url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": USER_AGENT,
        },
    )

    with urlopen(request, timeout=30) as response:
        raw_html = response.read().decode("utf-8", errors="replace")
        final_url = response.geturl()

    return parse_rugbyviz_config(raw_html, final_url)


def fetch_rugbyviz_matches(feed_url: str, fixtures_url: str) -> list[dict]:
    """Fetch matches using headers published by the corresponding website."""

    config = fetch_rugbyviz_config(fixtures_url)
    request = Request(
        feed_url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": USER_AGENT,
            "Origin": config.origin,
            "Referer": fixtures_url,
            "X-API-KEY": config.api_key,
            "X-APP-ID": config.app_id,
            "X-REALM": config.realm,
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("status") != "success":
        raise RuntimeError(
            f"Unexpected RugbyViz feed status: {data.get('status')!r}."
        )

    matches = data.get("data")

    if not isinstance(matches, list):
        raise RuntimeError("The RugbyViz feed returned an invalid matches payload.")

    return matches

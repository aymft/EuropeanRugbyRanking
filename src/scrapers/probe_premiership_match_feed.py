"""
Probe Premiership Rugby match feed endpoint.

The official Nuxt page exposes:
- season: 202601
- compId: 1011
- matchFeed: https://rugby-union-feeds.incrowdsports.com/v1/matches

This script tests likely query parameter combinations to identify the correct
endpoint format for fixtures/results.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from src.season_config import (
    PREMIERSHIP_COMPETITION_ID,
    PREMIERSHIP_FIXTURES_URL,
    PREMIERSHIP_SEASON_ID,
)


MATCH_FEED_URL = "https://rugby-union-feeds.incrowdsports.com/v1/matches"

API_KEY = "zDiLQ9o18oVrwn30etwT"
CLIENT_ID = "PRL"
SEASON = str(PREMIERSHIP_SEASON_ID)
COMP_ID = str(PREMIERSHIP_COMPETITION_ID)


QUERY_CANDIDATES = [
    # Current best guesses from Nuxt config
    {"clientId": CLIENT_ID, "season": SEASON, "competitionId": COMP_ID},
    {"clientId": CLIENT_ID, "seasonId": SEASON, "competitionId": COMP_ID},
    {"clientId": CLIENT_ID, "season_id": SEASON, "competition_id": COMP_ID},
    {"clientId": CLIENT_ID, "season": SEASON, "compId": COMP_ID},
    {"clientId": CLIENT_ID, "seasonId": SEASON, "compId": COMP_ID},
    {"clientId": CLIENT_ID, "season_id": SEASON, "comp_id": COMP_ID},

    # Plural variants
    {"clientId": CLIENT_ID, "seasonIds": SEASON, "competitionIds": COMP_ID},
    {"clientId": CLIENT_ID, "season_ids": SEASON, "competition_ids": COMP_ID},
    {"clientId": CLIENT_ID, "seasons": SEASON, "competitions": COMP_ID},

    # Without clientId
    {"season": SEASON, "competitionId": COMP_ID},
    {"seasonId": SEASON, "competitionId": COMP_ID},
    {"season_id": SEASON, "competition_id": COMP_ID},
    {"seasonIds": SEASON, "competitionIds": COMP_ID},
    {"season_ids": SEASON, "competition_ids": COMP_ID},

    # Competition only
    {"competitionId": COMP_ID},
    {"competitionIds": COMP_ID},
    {"competition_id": COMP_ID},
    {"competition_ids": COMP_ID},
    {"compId": COMP_ID},
    {"comp_id": COMP_ID},

    # Season only
    {"season": SEASON},
    {"seasonId": SEASON},
    {"season_id": SEASON},
    {"seasonIds": SEASON},
    {"season_ids": SEASON},

    # No useful filter, but useful to inspect response shape
    {},
]


HEADER_CANDIDATES = [
    {},
    {"x-api-key": API_KEY},
    {"X-Api-Key": API_KEY},
    {"apikey": API_KEY},
    {"apiKey": API_KEY},
    {"Authorization": f"Bearer {API_KEY}"},
]


def fetch_url(url: str, headers: dict) -> tuple[int, str]:
    request_headers = {
        "Accept": "application/json,text/plain,*/*",
        "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
        "Origin": "https://premiershiprugby.com",
        "Referer": PREMIERSHIP_FIXTURES_URL,
    }

    request_headers.update(headers)

    request = Request(url, headers=request_headers)

    with urlopen(request, timeout=30) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def main() -> None:
    for query_params in QUERY_CANDIDATES:
        url = f"{MATCH_FEED_URL}?{urlencode(query_params)}"

        print("\n" + "=" * 100)
        print(f"Testing URL: {url}")

        for headers in HEADER_CANDIDATES:
            print(f"\nHeaders: {headers or 'none'}")

            try:
                status, text = fetch_url(url, headers)
            except HTTPError as error:
                body = error.read().decode("utf-8", errors="replace")
                print(f"HTTPError: {error.code}")
                print(body[:500])
                continue
            except (URLError, TimeoutError) as error:
                print(f"Request failed: {error}")
                continue

            print(f"HTTP status: {status}")
            print(f"Response length: {len(text)}")

            preview = text[:1000]
            print("Preview:")
            print(preview)

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print("Not JSON.")
                continue

            if isinstance(data, list):
                print(f"JSON list length: {len(data)}")
                if data:
                    print("First item keys:", list(data[0].keys()))
                return

            if isinstance(data, dict):
                print("JSON dict keys:", list(data.keys()))

                for key in ["matches", "data", "results", "fixtures"]:
                    value = data.get(key)

                    if isinstance(value, list):
                        print(f"Found list under key {key!r}: {len(value)} items")

                        if value:
                            print("First item keys:", list(value[0].keys()))
                            print("\nFirst item preview:")
                            print(json.dumps(value[0], indent=2, ensure_ascii=False)[:3000])
                            return

                        print("List is empty, continuing with next candidate...")


if __name__ == "__main__":
    main()

"""
Probe Premiership match feed with app headers.

The previous probe showed:
- the endpoint responds;
- x-api-key alone triggers "X-APP-ID: Missing header";
- the current issue is likely missing app/realm/client headers.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


MATCH_FEED_URL = "https://rugby-union-feeds.incrowdsports.com/v1/matches"

API_KEY = "zDiLQ9o18oVrwn30etwT"
APP_ID = "web"
CLIENT_ID = "PRL"
REALM_ID = "prl"

SEASON = "202501"
COMP_ID = "1011"


QUERY_CANDIDATES = [
    {"season": SEASON, "competitionId": COMP_ID, "pageSize": 200},
    {"seasonId": SEASON, "competitionId": COMP_ID, "pageSize": 200},
    {"season_id": SEASON, "competition_id": COMP_ID, "pageSize": 200},
    {"competitionId": COMP_ID, "pageSize": 200},
    {"competition_id": COMP_ID, "pageSize": 200},
    {"compId": COMP_ID, "pageSize": 200},
    {"season": SEASON, "pageSize": 200},
    {"seasonId": SEASON, "pageSize": 200},
    {"pageSize": 200},
]


HEADER_CANDIDATES = [
    {
        "X-API-KEY": API_KEY,
        "X-APP-ID": APP_ID,
        "X-REALM": REALM_ID,
    },
    {
        "x-api-key": API_KEY,
        "x-app-id": APP_ID,
        "x-realm": REALM_ID,
    },
    {
        "X-API-KEY": API_KEY,
        "X-APP-ID": APP_ID,
        "X-REALM": REALM_ID,
        "X-CLIENT-ID": CLIENT_ID,
    },
    {
        "X-API-KEY": API_KEY,
        "X-APP-ID": APP_ID,
        "X-REALM": REALM_ID,
        "X-CLIENT-ID": CLIENT_ID,
        "X-DATA-PROVIDER": "rugbyviz",
    },
]


def fetch_url(url: str, headers: dict) -> tuple[int, str]:
    request_headers = {
        "Accept": "application/json,text/plain,*/*",
        "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
        "Origin": "https://premiershiprugby.com",
        "Referer": "https://premiershiprugby.com/content/202526-fixtures",
    }

    request_headers.update(headers)

    request = Request(url, headers=request_headers)

    with urlopen(request, timeout=30) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def inspect_response(text: str) -> bool:
    print(f"Response length: {len(text)}")
    print("Preview:")
    print(text[:1000])

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Not JSON.")
        return False

    if isinstance(data, dict):
        print("JSON dict keys:", list(data.keys()))

        for key in ["data", "matches", "results", "fixtures"]:
            value = data.get(key)

            if isinstance(value, list):
                print(f"List under {key!r}: {len(value)} items")

                if value:
                    print("\nFirst item:")
                    print(json.dumps(value[0], indent=2, ensure_ascii=False)[:4000])
                    return True

    elif isinstance(data, list):
        print(f"JSON list: {len(data)} items")

        if data:
            print("\nFirst item:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False)[:4000])
            return True

    return False


def main() -> None:
    for query_params in QUERY_CANDIDATES:
        url = f"{MATCH_FEED_URL}?{urlencode(query_params)}"

        print("\n" + "=" * 100)
        print(f"Testing URL: {url}")

        for headers in HEADER_CANDIDATES:
            print("\nHeaders:")
            print(headers)

            try:
                status, text = fetch_url(url, headers)
            except HTTPError as error:
                body = error.read().decode("utf-8", errors="replace")
                print(f"HTTPError: {error.code}")
                print(body[:1000])
                continue
            except (URLError, TimeoutError) as error:
                print(f"Request failed: {error}")
                continue

            print(f"HTTP status: {status}")

            found_non_empty = inspect_response(text)

            if found_non_empty:
                print("\nSUCCESS: non-empty match feed found.")
                return

    print("\nNo non-empty response found.")


if __name__ == "__main__":
    main()
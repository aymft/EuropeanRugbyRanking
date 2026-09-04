"""
Probe possible TOP 14 round URLs.

Goal:
- test several candidate URL patterns for each round J1...J26
- download the page
- parse the score-slider week metadata
- keep only URLs that really return the requested round
"""

import html
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.season_config import SEASON_LABEL, TOP14_SEASON_ID


ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

SEASON = SEASON_LABEL
BASE_URL = "https://top14.lnr.fr"


def build_candidate_urls(round_number: int) -> list[str]:
    """
    Build possible URL patterns for one TOP 14 round.
    """

    slug = f"j{round_number}"

    return [
        f"{BASE_URL}/calendrier-et-resultats/{SEASON}/{slug}",
        f"{BASE_URL}/calendrier-et-resultats?day={round_number}&season={TOP14_SEASON_ID}",
        f"{BASE_URL}/calendrier-et-resultats/{slug}",
        f"{BASE_URL}/calendrier-et-resultats?journee={round_number}",
        f"{BASE_URL}/calendrier-et-resultats?journee={slug}",
        f"{BASE_URL}/calendrier-et-resultats?week={round_number}",
        f"{BASE_URL}/calendrier-et-resultats?week={slug}",
        f"{BASE_URL}/calendrier-et-resultats?round={round_number}",
        f"{BASE_URL}/calendrier-et-resultats?round={slug}",
    ]


def fetch_url(url: str) -> str | None:
    """
    Fetch one candidate URL.
    """

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            )
        },
    )

    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")

    except (HTTPError, URLError, TimeoutError) as error:
        print(f"  failed: {url} ({error})")
        return None


def extract_current_week(raw_html: str) -> dict | None:
    """
    Extract the score-slider :current-week JSON object.
    """

    match = re.search(
        r"<score-slider\b[^>]*:current-week='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if match:
        current_week_raw = html.unescape(match.group(1))
        return json.loads(current_week_raw)

    match = re.search(
        r"<score-slider\b[^>]*:weeks='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not match:
        return None

    weeks = json.loads(html.unescape(match.group(1)))

    return weeks[0] if weeks else None


def extract_match_count(raw_html: str) -> int:
    """
    Count matches in score-slider :matches.
    """

    match = re.search(
        r"<score-slider\b[^>]*:matches='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not match:
        return 0

    matches_raw = html.unescape(match.group(1))
    matches = json.loads(matches_raw)

    return len(matches)


def main() -> None:
    valid_urls = []

    for round_number in range(1, 27):
        print("\n" + "=" * 80)
        print(f"Probing J{round_number}")

        for url in build_candidate_urls(round_number):
            raw_html = fetch_url(url)

            if raw_html is None:
                continue

            current_week = extract_current_week(raw_html)

            if current_week is None:
                print(f"  no score-slider: {url}")
                continue

            returned_round = current_week.get("number")
            match_count = extract_match_count(raw_html)

            print(
                f"  tested: J{round_number:02d} | "
                f"returned J{returned_round} | "
                f"matches={match_count} | "
                f"{url}"
            )

            if returned_round == round_number:
                valid_urls.append(
                    {
                        "round": round_number,
                        "url": url,
                        "matches": match_count,
                    }
                )
                break

    output_path = PROCESSED_DATA_DIR / "top14_round_urls.json"
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(valid_urls, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"Valid round URLs found: {len(valid_urls)}")
    print(f"Saved to: {output_path}")

    for item in valid_urls:
        print(f"J{item['round']:02d}: {item['matches']} matches | {item['url']}")


if __name__ == "__main__":
    main()

"""
Preview the current TOP 14 round from the official LNR website.

This script does not modify any file.
It only prints the matches currently exposed by the LNR score-slider component.

Useful to check:
- which round is currently displayed;
- which matches are scheduled for the weekend;
- which statuses are used by the LNR website before/after matches.
"""

import html
import json
import re
from urllib.request import Request, urlopen

from src.season_config import TOP14_RESULTS_URL
from src.team_registry import (
    get_display_name,
    normalize_team_name,
)


def fetch_top14_page() -> str:
    request = Request(
        TOP14_RESULTS_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            )
        },
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_current_week(raw_html: str) -> dict:
    current_week_match = re.search(
        r"<score-slider\b[^>]*:current-week='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if current_week_match:
        return json.loads(html.unescape(current_week_match.group(1)))

    weeks_match = re.search(
        r"<score-slider\b[^>]*:weeks='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not weeks_match:
        raise RuntimeError("Could not find score-slider week data.")

    weeks = json.loads(html.unescape(weeks_match.group(1)))

    if not weeks:
        raise RuntimeError("The score-slider weeks list is empty.")

    return weeks[0]


def extract_matches(raw_html: str) -> list[dict]:
    match = re.search(
        r"<score-slider\b[^>]*:matches='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not match:
        raise RuntimeError("Could not find score-slider :matches data.")

    return json.loads(html.unescape(match.group(1)))


def format_score(match: dict) -> str:
    score = match.get("score") or []

    if len(score) == 2:
        return f"{score[0]} - {score[1]}"

    return "vs"


def safe_display_name(source_name: str) -> str:
    """
    Convert LNR name to project display name.
    If a new name appears, return the raw source name to avoid crashing preview.
    """

    try:
        club_id = normalize_team_name("lnr_top14", source_name)
        return get_display_name(club_id)
    except ValueError:
        return source_name


def main() -> None:
    raw_html = fetch_top14_page()

    current_week = extract_current_week(raw_html)
    matches = extract_matches(raw_html)

    print("=" * 80)
    print("Current TOP 14 round")
    print("=" * 80)
    print(f"Name  : {current_week.get('name')}")
    print(f"Slug  : {current_week.get('slug')}")
    print(f"Number: {current_week.get('number')}")
    print(f"Matches found: {len(matches)}")

    statuses = sorted({match.get("status", "unknown") for match in matches})
    print(f"Statuses found: {statuses}")

    print("\n" + "=" * 80)
    print("Matches")
    print("=" * 80)

    for match in matches:
        home_raw = (match.get("hosting_club") or {}).get("name", "")
        away_raw = (match.get("visiting_club") or {}).get("name", "")

        home = safe_display_name(home_raw)
        away = safe_display_name(away_raw)

        print(
            f"{match.get('date', '??/??')} "
            f"{match.get('time', '??h??')} | "
            f"{match.get('status', 'unknown'):12s} | "
            f"{match.get('id')} | "
            f"{home} {format_score(match)} {away}"
        )

    upcoming = [
        match for match in matches
        if match.get("status") != "finished"
    ]

    print("\n" + "=" * 80)
    print("Upcoming / not finished")
    print("=" * 80)

    if not upcoming:
        print("No upcoming match found in the current LNR round.")
        return

    for match in upcoming:
        home_raw = (match.get("hosting_club") or {}).get("name", "")
        away_raw = (match.get("visiting_club") or {}).get("name", "")

        home = safe_display_name(home_raw)
        away = safe_display_name(away_raw)

        print(
            f"{match.get('date', '??/??')} "
            f"{match.get('time', '??h??')} | "
            f"{match.get('status', 'unknown'):12s} | "
            f"{home} vs {away}"
        )


if __name__ == "__main__":
    main()

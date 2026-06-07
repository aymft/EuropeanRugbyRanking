"""
Update match history with the latest TOP 14 round.

This script:
- downloads the current official TOP 14 fixtures/results page;
- extracts finished matches from the score-slider component;
- normalizes team names through the central registry;
- appends only new matches to data/processed/matches_history.csv.

It is designed to be run once per weekend.
"""

import csv
import html
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

TOP14_RESULTS_URL = "https://top14.lnr.fr/calendrier-et-resultats"
MATCH_HISTORY_PATH = PROCESSED_DATA_DIR / "matches_history.csv"


FIELDNAMES = [
    "source",
    "competition",
    "round",
    "match_id",
    "team_a_id",
    "team_b_id",
    "team_a",
    "team_b",
    "team_a_display",
    "team_b_display",
    "location",
    "score_a",
    "score_b",
    "status",
    "link",
]


def fetch_top14_page() -> str:
    """
    Download the current official TOP 14 fixtures/results page.
    """

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
    """
    Extract current week metadata from score-slider.
    """

    match = re.search(
        r"<score-slider\b[^>]*:current-week='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not match:
        raise RuntimeError("Could not find score-slider :current-week data.")

    return json.loads(html.unescape(match.group(1)))


def extract_score_slider_matches(raw_html: str) -> list[dict]:
    """
    Extract raw match dictionaries from score-slider.
    """

    match = re.search(
        r"<score-slider\b[^>]*:matches='([^']+)'",
        raw_html,
        flags=re.DOTALL,
    )

    if not match:
        raise RuntimeError("Could not find score-slider :matches data.")

    return json.loads(html.unescape(match.group(1)))


def parse_finished_matches(raw_html: str) -> list[dict]:
    """
    Parse finished TOP 14 matches into match-history rows.
    """

    current_week = extract_current_week(raw_html)
    round_slug = current_week.get("slug", "")
    raw_matches = extract_score_slider_matches(raw_html)

    parsed_matches = []

    for match in raw_matches:
        status = match.get("status")
        score = match.get("score") or []

        if status != "finished":
            continue

        if len(score) != 2:
            continue

        hosting_club = match.get("hosting_club") or {}
        visiting_club = match.get("visiting_club") or {}

        home_raw_name = hosting_club.get("name")
        away_raw_name = visiting_club.get("name")

        home_club_id = normalize_team_name("lnr_top14", home_raw_name)
        away_club_id = normalize_team_name("lnr_top14", away_raw_name)

        parsed_matches.append(
            {
                "source": "lnr_top14",
                "competition": "TOP14",
                "round": round_slug,
                "match_id": str(match.get("id")),
                "team_a_id": home_club_id,
                "team_b_id": away_club_id,
                "team_a": get_model_name(home_club_id),
                "team_b": get_model_name(away_club_id),
                "team_a_display": get_display_name(home_club_id),
                "team_b_display": get_display_name(away_club_id),
                "location": "home",
                "score_a": int(score[0]),
                "score_b": int(score[1]),
                "status": status,
                "link": match.get("link"),
            }
        )

    return parsed_matches


def load_existing_history(path: Path) -> list[dict]:
    """
    Load existing match history if it exists.
    """

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def save_history(path: Path, rows: list[dict]) -> None:
    """
    Save match history to CSV.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_new_matches(existing_rows: list[dict], latest_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Append only matches not already present in the history.

    Deduplication key:
    source + match_id
    """

    existing_keys = {
        (row["source"], row["match_id"])
        for row in existing_rows
    }

    new_rows = []

    for row in latest_rows:
        key = (row["source"], row["match_id"])

        if key not in existing_keys:
            new_rows.append(row)

    updated_rows = existing_rows + new_rows

    return updated_rows, new_rows


def main() -> None:
    raw_html = fetch_top14_page()

    current_week = extract_current_week(raw_html)
    raw_matches = extract_score_slider_matches(raw_html)
    statuses = sorted({match.get("status", "unknown") for match in raw_matches})

    latest_matches = parse_finished_matches(raw_html)

    print(f"Current TOP 14 round: {current_week.get('name')} ({current_week.get('slug')})")
    print(f"Statuses found: {statuses}")
    print(f"Total matches exposed by LNR: {len(raw_matches)}")

    existing_history = load_existing_history(MATCH_HISTORY_PATH)
    updated_history, new_matches = append_new_matches(
        existing_rows=existing_history,
        latest_rows=latest_matches,
    )

    save_history(MATCH_HISTORY_PATH, updated_history)

    print(f"Latest finished TOP 14 matches found: {len(latest_matches)}")
    print(f"Existing matches in history: {len(existing_history)}")
    print(f"New matches added: {len(new_matches)}")
    print(f"Updated history saved to: {MATCH_HISTORY_PATH}")

    if new_matches:
        print("\nNew matches:")
        for match in new_matches:
            print(
                f"  {match['round']} | "
                f"{match['team_a_display']} {match['score_a']} - "
                f"{match['score_b']} {match['team_b_display']}"
            )
    else:
        print("\nNo new TOP 14 match to add.")


if __name__ == "__main__":
    main()
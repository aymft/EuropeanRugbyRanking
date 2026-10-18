"""Update match history with completed EPCR matches.

This script:
- queries the official RugbyViz feeds for both EPCR competitions;
- keeps completed matches with final scores;
- normalizes team names through the central registry;
- appends only new matches to data/processed/matches_history.csv.
"""

import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

from src.season_config import (
    EPCR_CHALLENGE_CUP_FEED_URL,
    EPCR_CHALLENGE_CUP_FIXTURES_URL,
    EPCR_CHAMPIONS_CUP_FEED_URL,
    EPCR_CHAMPIONS_CUP_FIXTURES_URL,
)
from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
MATCH_HISTORY_PATH = ROOT_DIR / "data" / "processed" / "matches_history.csv"

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

EPCR_FEEDS = (
    (
        "CHAMPIONS_CUP",
        EPCR_CHAMPIONS_CUP_FEED_URL,
        EPCR_CHAMPIONS_CUP_FIXTURES_URL,
    ),
    (
        "CHALLENGE_CUP",
        EPCR_CHALLENGE_CUP_FEED_URL,
        EPCR_CHALLENGE_CUP_FIXTURES_URL,
    ),
)


def fetch_epcr_matches(feed_url: str, fixtures_url: str) -> list[dict]:
    request = Request(
        feed_url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://www.epcrugby.com",
            "Referer": fixtures_url,
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("status") != "success":
        raise RuntimeError(f"Unexpected EPCR feed status: {data.get('status')}")

    return data.get("data") or []


def is_completed_match(match: dict) -> bool:
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}

    return (
        match.get("status") == "result"
        and home_team.get("name")
        and away_team.get("name")
        and home_team.get("score") is not None
        and away_team.get("score") is not None
    )


def convert_epcr_match(competition: str, match: dict) -> dict:
    home_team = match["homeTeam"]
    away_team = match["awayTeam"]

    home_club_id = normalize_team_name("epcr", home_team["name"])
    away_club_id = normalize_team_name("epcr", away_team["name"])

    round_value = match.get("round")
    round_label = f"{competition.lower()}_round_{round_value}"

    return {
        "source": "epcr_rugbyviz",
        "competition": competition,
        "round": round_label,
        "match_id": str(match["id"]),
        "team_a_id": home_club_id,
        "team_b_id": away_club_id,
        "team_a": get_model_name(home_club_id),
        "team_b": get_model_name(away_club_id),
        "team_a_display": get_display_name(home_club_id),
        "team_b_display": get_display_name(away_club_id),
        "location": "home",
        "score_a": int(home_team["score"]),
        "score_b": int(away_team["score"]),
        "status": "finished",
        "link": "",
    }


def load_existing_history(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def save_history(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_new_matches(
    existing_rows: list[dict],
    latest_rows: list[dict],
) -> tuple[list[dict], list[dict]]:
    existing_keys = {
        (row["source"], row["match_id"])
        for row in existing_rows
    }
    new_rows = [
        row
        for row in latest_rows
        if (row["source"], row["match_id"]) not in existing_keys
    ]

    return existing_rows + new_rows, new_rows


def main() -> None:
    completed_matches = []
    feed_summaries = []

    for competition, feed_url, fixtures_url in EPCR_FEEDS:
        matches = fetch_epcr_matches(feed_url, fixtures_url)
        completed = [match for match in matches if is_completed_match(match)]

        feed_summaries.append((competition, len(matches), len(completed)))
        completed_matches.extend(
            (competition, match)
            for match in completed
        )

    completed_matches.sort(key=lambda item: item[1].get("date", ""))
    latest_rows = [
        convert_epcr_match(competition, match)
        for competition, match in completed_matches
    ]

    existing_history = load_existing_history(MATCH_HISTORY_PATH)
    updated_history, new_matches = append_new_matches(
        existing_rows=existing_history,
        latest_rows=latest_rows,
    )
    save_history(MATCH_HISTORY_PATH, updated_history)

    for competition, total_count, completed_count in feed_summaries:
        print(
            f"{competition}: {total_count} matches returned, "
            f"{completed_count} completed"
        )

    print(f"Existing matches in history: {len(existing_history)}")
    print(f"New matches added: {len(new_matches)}")
    print(f"Updated history saved to: {MATCH_HISTORY_PATH}")

    if new_matches:
        print("\nNew EPCR matches:")
        for match in new_matches:
            print(
                f"  {match['competition']} | {match['round']} | "
                f"{match['team_a_display']} {match['score_a']} - "
                f"{match['score_b']} {match['team_b_display']}"
            )
    else:
        print("\nNo new EPCR match to add.")


if __name__ == "__main__":
    main()

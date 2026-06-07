"""
Update match history with the latest completed Premiership Rugby round.

This script:
- queries the official Premiership Rugby Incrowd feed;
- selects the latest completed Premiership round;
- normalizes team names through the central registry;
- appends only new matches to data/processed/matches_history.csv.

It is designed to be run once per weekend.
"""

import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

MATCH_HISTORY_PATH = PROCESSED_DATA_DIR / "matches_history.csv"

PREMIERSHIP_FEED_URL = (
    "https://rugby-union-feeds.incrowdsports.com/v1/matches"
    "?compId=1011&season=202501&provider=rugbyviz"
)


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


def fetch_premiership_matches() -> list[dict]:
    request = Request(
        PREMIERSHIP_FEED_URL,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://premiershiprugby.com",
            "Referer": "https://premiershiprugby.com/content/202526-fixtures",
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("status") != "success":
        raise RuntimeError(f"Unexpected feed status: {data.get('status')}")

    return data.get("data") or []


def select_latest_completed_round(matches: list[dict]) -> list[dict]:
    """
    Select all result matches from the latest completed Premiership round.
    """

    result_matches = [
        match
        for match in matches
        if match.get("status") == "result"
        and match.get("homeTeam")
        and match.get("awayTeam")
        and match["homeTeam"].get("score") is not None
        and match["awayTeam"].get("score") is not None
        and match.get("round") is not None
    ]

    if not result_matches:
        return []

    latest_round = max(match["round"] for match in result_matches)

    latest_round_matches = [
        match
        for match in result_matches
        if match["round"] == latest_round
    ]

    return sorted(latest_round_matches, key=lambda match: match.get("date", ""))


def convert_premiership_match(match: dict) -> dict:
    home_team = match["homeTeam"]
    away_team = match["awayTeam"]

    home_raw_name = home_team["name"]
    away_raw_name = away_team["name"]

    home_club_id = normalize_team_name("premiership", home_raw_name)
    away_club_id = normalize_team_name("premiership", away_raw_name)

    round_label = f"premiership_round_{match['round']}"

    return {
        "source": "premiership_rugbyviz",
        "competition": "PREMIERSHIP",
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

    new_rows = []

    for row in latest_rows:
        key = (row["source"], row["match_id"])

        if key not in existing_keys:
            new_rows.append(row)

    updated_rows = existing_rows + new_rows

    return updated_rows, new_rows


def main() -> None:
    matches = fetch_premiership_matches()
    latest_completed = select_latest_completed_round(matches)

    latest_rows = [
        convert_premiership_match(match)
        for match in latest_completed
    ]

    existing_history = load_existing_history(MATCH_HISTORY_PATH)
    updated_history, new_matches = append_new_matches(
        existing_rows=existing_history,
        latest_rows=latest_rows,
    )

    save_history(MATCH_HISTORY_PATH, updated_history)

    statuses = sorted({match.get("status", "unknown") for match in matches})
    result_rounds = sorted(
        {
            match.get("round")
            for match in matches
            if match.get("status") == "result"
        }
    )

    print(f"Premiership matches returned: {len(matches)}")
    print(f"Statuses found: {statuses}")
    print(f"Completed rounds found: {result_rounds}")
    print(f"Latest completed Premiership matches selected: {len(latest_rows)}")
    print(f"Existing matches in history: {len(existing_history)}")
    print(f"New matches added: {len(new_matches)}")
    print(f"Updated history saved to: {MATCH_HISTORY_PATH}")

    if new_matches:
        print("\nNew Premiership matches:")
        for match in new_matches:
            print(
                f"  {match['round']} | "
                f"{match['team_a_display']} {match['score_a']} - "
                f"{match['score_b']} {match['team_b_display']}"
            )
    else:
        print("\nNo new Premiership match to add.")


if __name__ == "__main__":
    main()
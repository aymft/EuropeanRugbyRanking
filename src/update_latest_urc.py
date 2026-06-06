"""
Update match history with the latest completed URC weekend/round.

This script:
- queries the official URC GraphQL endpoint;
- selects the latest completed group of URC results;
- normalizes team names through the central registry;
- appends only new matches to data/processed/matches_history.csv.

It is designed to be run once per weekend.
"""

import csv
import json
from datetime import datetime, timedelta, timezone
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

URC_GRAPHQL_URL = "https://www.unitedrugby.com/graphql"
URC_SEASON_ID = 202501

# Include all results close to the latest result date.
# This catches Friday/Saturday/Sunday rounds as one weekend.
LATEST_RESULT_WINDOW_DAYS = 3


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


QUERY = """
query GetMatchesData(
  $season_id: [Int!]
  $limit: Int
  $orderBy: String
  $order: String
) {
  matches(
    season_id: $season_id
    limit: $limit
    orderBy: $orderBy
    order: $order
  ) {
    id
    season_id
    match_data {
      dateTime
      matchStatus
      homeTeam {
        id
        name
        shortName
        score {
          finalScore
        }
      }
      awayTeam {
        id
        name
        shortName
        score {
          finalScore
        }
      }
      venue {
        name
      }
    }
  }
}
"""


def post_graphql_query(query: str, variables: dict) -> dict:
    payload = json.dumps(
        {
            "query": query,
            "variables": variables,
        }
    ).encode("utf-8")

    request = Request(
        URC_GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://stats.unitedrugby.com",
            "Referer": "https://stats.unitedrugby.com/",
        },
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def parse_datetime_utc(value: str) -> datetime:
    """
    Parse URC ISO datetime as timezone-aware UTC datetime.
    """

    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def get_final_score(team: dict) -> int | None:
    score = team.get("score") or {}
    final_score = score.get("finalScore")

    if final_score is None:
        return None

    return int(final_score)


def fetch_urc_matches() -> list[dict]:
    variables = {
        "season_id": [URC_SEASON_ID],
        "limit": 120,
        "orderBy": "dateTime",
        "order": "DESC",
    }

    response = post_graphql_query(QUERY, variables)

    if "errors" in response:
        raise RuntimeError(json.dumps(response["errors"], indent=2, ensure_ascii=False))

    return response.get("data", {}).get("matches") or []


def select_latest_completed_results(matches: list[dict]) -> list[dict]:
    """
    Select the latest completed URC result group.

    We first find the most recent result, then include all result matches within
    LATEST_RESULT_WINDOW_DAYS before it.
    """

    result_matches = []

    for row in matches:
        match_data = row.get("match_data") or {}

        if match_data.get("matchStatus") != "result":
            continue

        home_team = match_data.get("homeTeam") or {}
        away_team = match_data.get("awayTeam") or {}

        if not home_team.get("name") or not away_team.get("name"):
            continue

        if get_final_score(home_team) is None or get_final_score(away_team) is None:
            continue

        result_matches.append(row)

    if not result_matches:
        return []

    latest_datetime = max(
        parse_datetime_utc((row.get("match_data") or {})["dateTime"])
        for row in result_matches
    )

    window_start = latest_datetime - timedelta(days=LATEST_RESULT_WINDOW_DAYS)

    latest_group = []

    for row in result_matches:
        match_datetime = parse_datetime_utc((row.get("match_data") or {})["dateTime"])

        if window_start <= match_datetime <= latest_datetime:
            latest_group.append(row)

    return sorted(
        latest_group,
        key=lambda row: parse_datetime_utc((row.get("match_data") or {})["dateTime"]),
    )


def convert_urc_match(row: dict) -> dict:
    match_data = row.get("match_data") or {}

    home_team = match_data.get("homeTeam") or {}
    away_team = match_data.get("awayTeam") or {}

    home_raw_name = home_team.get("name")
    away_raw_name = away_team.get("name")

    home_club_id = normalize_team_name("urc", home_raw_name)
    away_club_id = normalize_team_name("urc", away_raw_name)

    match_datetime = parse_datetime_utc(match_data["dateTime"])
    round_label = f"urc_weekend_{match_datetime.date().isoformat()}"

    return {
        "source": "urc_graphql",
        "competition": "URC",
        "round": round_label,
        "match_id": str(row.get("id")),
        "team_a_id": home_club_id,
        "team_b_id": away_club_id,
        "team_a": get_model_name(home_club_id),
        "team_b": get_model_name(away_club_id),
        "team_a_display": get_display_name(home_club_id),
        "team_b_display": get_display_name(away_club_id),
        "location": "home",
        "score_a": get_final_score(home_team),
        "score_b": get_final_score(away_team),
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


def append_new_matches(existing_rows: list[dict], latest_rows: list[dict]) -> tuple[list[dict], list[dict]]:
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
    matches = fetch_urc_matches()
    latest_completed = select_latest_completed_results(matches)

    latest_rows = [
        convert_urc_match(row)
        for row in latest_completed
    ]

    existing_history = load_existing_history(MATCH_HISTORY_PATH)
    updated_history, new_matches = append_new_matches(
        existing_rows=existing_history,
        latest_rows=latest_rows,
    )

    save_history(MATCH_HISTORY_PATH, updated_history)

    statuses = sorted(
        {
            (row.get("match_data") or {}).get("matchStatus", "unknown")
            for row in matches
        }
    )

    print(f"URC matches returned: {len(matches)}")
    print(f"Statuses found: {statuses}")
    print(f"Latest completed URC matches selected: {len(latest_rows)}")
    print(f"Existing matches in history: {len(existing_history)}")
    print(f"New matches added: {len(new_matches)}")
    print(f"Updated history saved to: {MATCH_HISTORY_PATH}")

    if new_matches:
        print("\nNew URC matches:")
        for match in new_matches:
            print(
                f"  {match['round']} | "
                f"{match['team_a_display']} {match['score_a']} - "
                f"{match['score_b']} {match['team_b_display']}"
            )
    else:
        print("\nNo new URC match to add.")


if __name__ == "__main__":
    main()
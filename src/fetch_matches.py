"""
Fetch rugby match data from external sources.

First experimental version:
- fetch raw TOP 14 season data from TheSportsDB
- save the raw JSON response locally
- print a few events to inspect the structure

This file is not yet connected to the Elo pipeline.
"""

import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.matches import Match
from src.season_config import SEASON_LABEL


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

THESPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/123/eventsseason.php"

THESPORTSDB_PAST_LEAGUE_URL = (
    "https://www.thesportsdb.com/api/v1/json/123/eventspastleague.php"
)

LEAGUES = {
    "TOP14": {
        "id": "4430",
        "season": SEASON_LABEL,
    },
    "PREMIERSHIP": {
        "id": "4414",
        "season": SEASON_LABEL,
    },
    "URC": {
        "id": "4446",
        "season": SEASON_LABEL,
    },
    "CHAMPIONS_CUP": {
        "id": "4550",
        "season": SEASON_LABEL,
    },
    "CHALLENGE_CUP": {
        "id": "5418",
        "season": SEASON_LABEL,
    },
}


def fetch_season_events(league_key: str) -> dict:
    """
    Fetch all available events for one league and one season.

    Parameters
    ----------
    league_key : str
        Internal league key, for example "TOP14" or "URC".

    Returns
    -------
    dict
        Raw JSON response from TheSportsDB.
    """

    if league_key not in LEAGUES:
        raise ValueError(f"Unknown league key: {league_key}")

    league = LEAGUES[league_key]

    params = urlencode(
        {
            "id": league["id"],
            "s": league["season"],
        }
    )

    url = f"{THESPORTSDB_BASE_URL}?{params}"

    request = Request(
        url,
        headers={
            "User-Agent": "EuropeanRugbyRanking/0.1"
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.load(response)

def fetch_latest_league_events(league_key: str) -> dict:
    """
    Fetch the latest finished events for one league.

    This uses TheSportsDB eventspastleague endpoint.
    """

    if league_key not in LEAGUES:
        raise ValueError(f"Unknown league key: {league_key}")

    league = LEAGUES[league_key]

    params = urlencode(
        {
            "id": league["id"],
        }
    )

    url = f"{THESPORTSDB_PAST_LEAGUE_URL}?{params}"

    request = Request(
        url,
        headers={
            "User-Agent": "EuropeanRugbyRanking/0.1"
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.load(response)

def save_raw_data(data: dict, league_key: str) -> Path:
    """
    Save raw JSON data locally.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    season = LEAGUES[league_key]["season"]
    output_path = RAW_DATA_DIR / f"{league_key.lower()}_{season}_raw.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_path

def convert_events_to_matches(data: dict, competition: str) -> list[Match]:
    """
    Convert raw TheSportsDB events into internal Match objects.

    Only finished matches with available scores are kept.
    """

    events = data.get("events") or []
    matches = []

    for event in events:
        status = event.get("strStatus")
        home_team = event.get("strHomeTeam")
        away_team = event.get("strAwayTeam")
        home_score = event.get("intHomeScore")
        away_score = event.get("intAwayScore")

        if status != "FT":
            continue

        if not home_team or not away_team:
            continue

        if home_score is None or away_score is None:
            continue

        match = Match(
            team_a=home_team,
            team_b=away_team,
            location="home",
            score_a=int(home_score),
            score_b=int(away_score),
            competition=competition,
        )

        matches.append(match)

    return matches


def save_clean_matches(matches: list[Match], output_path: Path) -> None:
    """
    Save cleaned matches to CSV.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "team_a",
                "team_b",
                "location",
                "score_a",
                "score_b",
                "competition",
            ],
        )

        writer.writeheader()

        for match in matches:
            writer.writerow(
                {
                    "team_a": match.team_a,
                    "team_b": match.team_b,
                    "location": match.location,
                    "score_a": match.score_a,
                    "score_b": match.score_b,
                    "competition": match.competition,
                }
            )


def main() -> None:
    """
    Fetch all configured competitions, convert finished events to Match objects,
    and save the cleaned matches to CSV.
    """

    all_matches = []

    for league_key in LEAGUES:
        print(f"\nFetching {league_key}...")

        # data = fetch_season_events(league_key)
        data = fetch_latest_league_events(league_key)
        output_path = save_raw_data(data, league_key)

        matches = convert_events_to_matches(data, league_key)
        all_matches.extend(matches)

        print(f"Saved raw data to: {output_path}")
        print(f"Finished matches found: {len(matches)}")

        for match in matches[:5]:
            print(
                f"  {match.team_a} {match.score_a} - "
                f"{match.score_b} {match.team_b}"
            )

    clean_matches_path = PROCESSED_DATA_DIR / "matches_clean.csv"
    save_clean_matches(all_matches, clean_matches_path)

    print("\n====================================")
    print(f"Total finished matches: {len(all_matches)}")
    print(f"Saved cleaned matches to: {clean_matches_path}")


if __name__ == "__main__":
    main()

"""
Generate European rugby club rankings.

This script applies Elo updates to all available matches and exports
the resulting rankings to CSV and JSON files.
"""

import csv
import json
from pathlib import Path

from src.elo import elo_update
from src.matches import get_all_matches
from src.teams import get_initial_teams


ROOT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"
DOCS_DATA_DIR = ROOT_DIR / "docs" / "data"

PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "rankings.csv"
DOCS_CSV_PATH = DOCS_DATA_DIR / "rankings.csv"
DOCS_JSON_PATH = DOCS_DATA_DIR / "rankings.json"


def compute_rankings() -> list[dict]:
    """
    Compute the current Elo ranking from the initial teams and match results.

    Returns
    -------
    list[dict]
        Sorted ranking table. Each item contains rank, team, and points.
    """

    teams = get_initial_teams()
    matches = get_all_matches()

    for match in matches:
        if match.team_a not in teams:
            raise ValueError(f"Unknown team: {match.team_a}")

        if match.team_b not in teams:
            raise ValueError(f"Unknown team: {match.team_b}")

        new_elo_a, new_elo_b = elo_update(
            team_elo=teams[match.team_a],
            opponent_elo=teams[match.team_b],
            location=match.location,
            score_a=match.score_a,
            score_b=match.score_b,
            competition=match.competition,
        )

        teams[match.team_a] = new_elo_a
        teams[match.team_b] = new_elo_b

    sorted_teams = sorted(
        teams.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    rankings = [
        {
            "rank": index + 1,
            "team": team,
            "points": points,
        }
        for index, (team, points) in enumerate(sorted_teams)
    ]

    return rankings


def export_csv(rankings: list[dict], output_path: Path) -> None:
    """
    Export rankings to a CSV file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["rank", "team", "points"],
        )
        writer.writeheader()
        writer.writerows(rankings)


def export_json(rankings: list[dict], output_path: Path) -> None:
    """
    Export rankings to a JSON file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(rankings, json_file, indent=2, ensure_ascii=False)


def main() -> None:
    """
    Generate and export rankings.
    """

    rankings = compute_rankings()

    export_csv(rankings, PROCESSED_CSV_PATH)
    export_csv(rankings, DOCS_CSV_PATH)
    export_json(rankings, DOCS_JSON_PATH)

    print(f"Generated {PROCESSED_CSV_PATH}")
    print(f"Generated {DOCS_CSV_PATH}")
    print(f"Generated {DOCS_JSON_PATH}")

    print("\nTop 10:")
    for row in rankings[:10]:
        print(f"{row['rank']:>2}. {row['team']:<20} {row['points']}")


if __name__ == "__main__":
    main()
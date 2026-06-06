"""
Generate European rugby club rankings.

This script applies Elo updates to all available matches and exports
the resulting rankings to CSV and JSON files.
"""

import csv
import json
import re
import unicodedata
from pathlib import Path

from src.elo import elo_update
from src.matches import Match, get_all_matches
from src.teams import get_initial_teams
from src.competitions import COMPETITION_LOGOS

from src.team_registry import (
    get_club_id_from_model_name,
    get_display_name,
    get_domestic_competition,
)


ROOT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"
DOCS_DATA_DIR = ROOT_DIR / "docs" / "data"

PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "rankings.csv"
DOCS_CSV_PATH = DOCS_DATA_DIR / "rankings.csv"
DOCS_JSON_PATH = DOCS_DATA_DIR / "rankings.json"

MATCH_HISTORY_PATH = ROOT_DIR / "data" / "processed" / "matches_history.csv"

PREVIOUS_RANKINGS_PATH = ROOT_DIR / "data" / "processed" / "previous_rankings.json"

def slugify_team_name(team_name: str) -> str:
    """
    Convert a team name into a filesystem-friendly slug.

    Examples
    --------
    "Union Bordeaux Bègles" -> "union-bordeaux-begles"
    "Racing Métro 92" -> "racing-metro-92"
    """

    normalized = unicodedata.normalize("NFKD", team_name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    lower_name = ascii_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower_name)
    slug = slug.strip("-")

    return slug

def get_logo_path(club_id: str) -> str:
    """
    Return the best available local logo path for a club_id.

    SVG files are preferred over PNG files when both exist.
    """

    svg_path = ROOT_DIR / "docs" / "assets" / "img" / "clubs" / f"{club_id}.svg"
    png_path = ROOT_DIR / "docs" / "assets" / "img" / "clubs" / f"{club_id}.png"

    if svg_path.exists():
        return f"assets/img/clubs/{club_id}.svg"

    if png_path.exists():
        return f"assets/img/clubs/{club_id}.png"

    return f"assets/img/clubs/{club_id}.png"

def build_rank_lookup(teams: dict[str, int]) -> dict[str, int]:
    """
    Build a dictionary giving the rank of each team.

    Parameters
    ----------
    teams : dict[str, int]
        Dictionary of team Elo ratings.

    Returns
    -------
    dict[str, int]
        Dictionary where keys are team names and values are ranks.
    """

    sorted_teams = sorted(
        teams.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return {
        team: index + 1
        for index, (team, _) in enumerate(sorted_teams)
    }

def load_previous_rankings_snapshot() -> dict[str, dict]:
    """
    Load the previous published ranking snapshot.

    This snapshot is used only to compute:
    - rank_change
    - points_change

    Elo values themselves remain cumulative.
    """

    if not PREVIOUS_RANKINGS_PATH.exists():
        return {}

    with PREVIOUS_RANKINGS_PATH.open("r", encoding="utf-8") as json_file:
        rows = json.load(json_file)

    snapshot = {}

    for row in rows:
        club_id = row.get("club_id")

        if not club_id:
            continue

        snapshot[club_id] = {
            "rank": int(row["rank"]),
            "points": int(row["points"]),
        }

    return snapshot

def compute_rankings() -> list[dict]:
    """
    Compute the current Elo ranking from the initial teams and match results.

    Returns
    -------
    list[dict]
        Sorted ranking table. Each item contains the current rank, previous
        rank, rank change, team name, current points, previous points,
        Elo points change, and logo path.
    """

    initial_teams = get_initial_teams()
    teams = get_initial_teams()
    matches = get_matches_for_ranking()

    previous_ranks = build_rank_lookup(initial_teams)

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

    rankings = []

    previous_snapshot = load_previous_rankings_snapshot()

    for index, (team, points) in enumerate(sorted_teams):
        current_rank = index + 1

        club_id = get_club_id_from_model_name(team)
        display_name = get_display_name(club_id)
        league = get_domestic_competition(club_id)

        previous_row = previous_snapshot.get(club_id, {})

        previous_rank = previous_row.get("rank", current_rank)
        previous_points = previous_row.get("points", points)

        rankings.append(
            {
                "rank": current_rank,
                "previous_rank": previous_rank,
                "rank_change": previous_rank - current_rank,

                "club_id": club_id,
                "team": display_name,
                "model_name": team,

                "points": points,
                "previous_points": previous_points,
                "points_change": points - previous_points,

                "logo": get_logo_path(club_id),
                "league": league,
                "league_logo": COMPETITION_LOGOS[league],
            }
        )

    return rankings


def export_csv(rankings: list[dict], output_path: Path) -> None:
    """
    Export rankings to a CSV file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "rank",
                "previous_rank",
                "rank_change",
                "club_id",
                "team",
                "model_name",
                "points",
                "previous_points",
                "points_change",
                "logo",
                "league",
                "league_logo",
            ],
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

def load_history_matches() -> list[Match]:
    """
    Load finished matches from data/processed/matches_history.csv.

    This file becomes the authoritative source for competitions progressively
    migrated to official scrapers.
    """

    if not MATCH_HISTORY_PATH.exists():
        return []

    matches = []

    with MATCH_HISTORY_PATH.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            if row["status"] != "finished":
                continue

            matches.append(
                Match(
                    team_a=row["team_a"],
                    team_b=row["team_b"],
                    location=row["location"],
                    score_a=int(row["score_a"]),
                    score_b=int(row["score_b"]),
                    competition=row["competition"],
                )
            )

    return matches


def get_matches_for_ranking() -> list[Match]:
    """
    Return matches used for Elo computation.

    For competitions already present in matches_history.csv, the history file
    becomes authoritative. Manual matches for those competitions are excluded
    to avoid double counting.
    """

    manual_matches = get_all_matches()
    history_matches = load_history_matches()

    if not history_matches:
        return manual_matches

    competitions_from_history = {
        match.competition
        for match in history_matches
    }

    manual_matches_to_keep = [
        match for match in manual_matches
        if match.competition not in competitions_from_history
    ]

    return manual_matches_to_keep + history_matches

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
        points_change = row["points_change"]
        rank_change = row["rank_change"]

        print(
            f"{row['rank']:>2}. "
            f"{row['team']:<28} "
            f"{row['points']:>4} "
            f"({points_change:+}) "
            f"rank change: {rank_change:+}"
        )



if __name__ == "__main__":
    main()
"""
Inspect team names across available data sources.

This script compares:
- the current Elo model team names from src/teams.py
- team names found in TheSportsDB raw files
- team names extracted from the official TOP 14/LNR scraper

The goal is to prepare a robust club registry based on stable club IDs
and source-specific aliases.
"""

import csv
import json
from pathlib import Path

from src.teams import get_initial_teams


ROOT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

OUTPUT_CSV_PATH = PROCESSED_DATA_DIR / "team_name_inventory.csv"


def add_record(records: list[dict], source: str, competition: str, team_name: str) -> None:
    """
    Add one team-name record to the inventory.
    """

    if not team_name:
        return

    records.append(
        {
            "source": source,
            "competition": competition,
            "team_name": team_name.strip(),
        }
    )


def collect_model_names(records: list[dict]) -> None:
    """
    Collect names currently used by the Elo model.
    """

    teams = get_initial_teams()

    for team_name in teams:
        add_record(
            records=records,
            source="elo_model",
            competition="ALL",
            team_name=team_name,
        )


def collect_thesportsdb_event_names(records: list[dict]) -> None:
    """
    Collect names from raw TheSportsDB event files, if available.
    """

    for path in sorted(RAW_DATA_DIR.glob("*_2025-2026_raw.json")):
        competition = path.name.replace("_2025-2026_raw.json", "").upper()

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        events = data.get("events") or []

        for event in events:
            add_record(
                records=records,
                source="thesportsdb_events",
                competition=competition,
                team_name=event.get("strHomeTeam"),
            )
            add_record(
                records=records,
                source="thesportsdb_events",
                competition=competition,
                team_name=event.get("strAwayTeam"),
            )


def collect_thesportsdb_team_names(records: list[dict]) -> None:
    """
    Collect names from raw TheSportsDB team metadata files, if available.
    """

    for path in sorted(RAW_DATA_DIR.glob("*_teams_raw.json")):
        competition = path.name.replace("_teams_raw.json", "").upper()

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        teams = data.get("teams") or []

        for team in teams:
            add_record(
                records=records,
                source="thesportsdb_teams",
                competition=competition,
                team_name=team.get("strTeam"),
            )


def collect_lnr_top14_names(records: list[dict]) -> None:
    """
    Collect names from the parsed official TOP 14/LNR CSV, if available.
    """

    path = PROCESSED_DATA_DIR / "top14_official_matches.csv"

    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            add_record(
                records=records,
                source="lnr_top14",
                competition="TOP14",
                team_name=row.get("team_a"),
            )
            add_record(
                records=records,
                source="lnr_top14",
                competition="TOP14",
                team_name=row.get("team_b"),
            )


def deduplicate_records(records: list[dict]) -> list[dict]:
    """
    Remove duplicate source/competition/team_name rows.
    """

    seen = set()
    unique_records = []

    for record in records:
        key = (
            record["source"],
            record["competition"],
            record["team_name"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_records.append(record)

    return sorted(
        unique_records,
        key=lambda row: (row["source"], row["competition"], row["team_name"]),
    )


def save_inventory(records: list[dict]) -> None:
    """
    Save inventory to CSV.
    """

    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["source", "competition", "team_name"],
        )
        writer.writeheader()
        writer.writerows(records)


def print_summary(records: list[dict]) -> None:
    """
    Print a compact terminal summary.
    """

    grouped = {}

    for record in records:
        key = (record["source"], record["competition"])
        grouped.setdefault(key, []).append(record["team_name"])

    print("\n====================================")
    print("Team name inventory summary")
    print("====================================")

    for (source, competition), names in grouped.items():
        print(f"\n{source} / {competition} ({len(names)} teams)")
        for name in names:
            print(f"  - {name}")


def main() -> None:
    records = []

    collect_model_names(records)
    collect_thesportsdb_event_names(records)
    collect_thesportsdb_team_names(records)
    collect_lnr_top14_names(records)

    records = deduplicate_records(records)

    save_inventory(records)
    print_summary(records)

    print("\n====================================")
    print(f"Saved inventory to: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
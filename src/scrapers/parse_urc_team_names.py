"""
Parse official URC team names and map them to the central club registry.

Input:
- data/processed/urc_official_team_names.json

Output:
- data/processed/urc_official_team_names.csv
"""

import csv
import json
from pathlib import Path

from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_JSON_PATH = ROOT_DIR / "data" / "processed" / "urc_official_team_names.json"
OUTPUT_CSV_PATH = ROOT_DIR / "data" / "processed" / "urc_official_team_names.csv"


def load_official_names(input_path: Path) -> list[str]:
    """
    Load official URC team names from JSON.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find {input_path}. "
            "Run python -m src.scrapers.test_urc_graphql first."
        )

    with input_path.open("r", encoding="utf-8") as file:
        names = json.load(file)

    return names


def save_team_names(names: list[str], output_path: Path) -> None:
    """
    Save official URC team names with registry mapping to CSV.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "competition",
        "club_id",
        "official_name",
        "model_name",
        "display_name",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for official_name in names:
            club_id = normalize_team_name("urc", official_name)

            writer.writerow(
                {
                    "competition": "URC",
                    "club_id": club_id,
                    "official_name": official_name,
                    "model_name": get_model_name(club_id),
                    "display_name": get_display_name(club_id),
                }
            )


def main() -> None:
    names = load_official_names(INPUT_JSON_PATH)
    save_team_names(names, OUTPUT_CSV_PATH)

    print(f"Official URC team names found: {len(names)}")
    print(f"Saved team names to: {OUTPUT_CSV_PATH}")

    print("\nTeams:")
    for official_name in names:
        club_id = normalize_team_name("urc", official_name)

        print(
            f"  - {official_name:28s} "
            f"-> {club_id:22s} "
            f"-> {get_model_name(club_id)}"
        )


if __name__ == "__main__":
    main()
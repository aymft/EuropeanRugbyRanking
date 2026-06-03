"""
Parse official Premiership Rugby team names from the downloaded HTML page.

This script extracts the active club list from the official Premiership Rugby
fixtures page and saves it to a CSV file.
"""

import csv
import html
import re
from pathlib import Path

from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[2]

HTML_PATH = ROOT_DIR / "data" / "raw" / "premiership_official_page.html"
OUTPUT_CSV_PATH = ROOT_DIR / "data" / "processed" / "premiership_official_team_names.csv"


def extract_active_club_names(raw_html: str) -> list[str]:
    """
    Extract active club names from links like:

    /clubs/bath-rugby/news
    /clubs/bristol-bears/news
    """

    pattern = (
        r'<a href="/clubs/[^"]+/news"[^>]*>\s*'
        r'<p[^>]*>(.*?)</p>\s*'
        r"</a>"
    )

    names = re.findall(pattern, raw_html, flags=re.DOTALL)

    cleaned_names = []

    for name in names:
        clean_name = re.sub(r"\s+", " ", name)
        clean_name = html.unescape(clean_name).strip()

        if clean_name and clean_name not in cleaned_names:
            cleaned_names.append(clean_name)

    return cleaned_names


def save_team_names(names: list[str], output_path: Path) -> None:
    """
    Save official Premiership team names with registry mapping to CSV.
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
            club_id = normalize_team_name("premiership", official_name)

            writer.writerow(
                {
                    "competition": "PREMIERSHIP",
                    "club_id": club_id,
                    "official_name": official_name,
                    "model_name": get_model_name(club_id),
                    "display_name": get_display_name(club_id),
                }
            )


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_PATH}. "
            "Run python -m src.scrapers.premiership_scraper first."
        )

    raw_html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    names = extract_active_club_names(raw_html)
    save_team_names(names, OUTPUT_CSV_PATH)

    print(f"Official Premiership team names found: {len(names)}")
    print(f"Saved team names to: {OUTPUT_CSV_PATH}")

    print("\nTeams:")
    for official_name in names:
        club_id = normalize_team_name("premiership", official_name)

        print(
            f"  - {official_name:22s} "
            f"-> {club_id:22s} "
            f"-> {get_model_name(club_id)}"
        )


if __name__ == "__main__":
    main()
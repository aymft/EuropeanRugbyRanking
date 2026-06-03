"""
Parse TOP 14 matches from the official LNR HTML page.

This script reads the downloaded TOP 14 fixtures/results page and extracts
the JSON data embedded in the score-slider component.
"""

import csv
import html
import json
import re
from pathlib import Path

from src.team_registry import (
    get_display_name,
    get_model_name,
    normalize_team_name,
)


ROOT_DIR = Path(__file__).resolve().parents[2]

HTML_PATH = ROOT_DIR / "data" / "raw" / "top14_official_page.html"
OUTPUT_CSV_PATH = ROOT_DIR / "data" / "processed" / "top14_official_matches.csv"


def extract_score_slider_matches(raw_html: str) -> list[dict]:
    """
    Extract the JSON list stored in the score-slider :matches attribute.
    """

    pattern = r"<score-slider[^>]+:matches='([^']+)'"

    match = re.search(pattern, raw_html)

    if not match:
        raise RuntimeError("Could not find score-slider :matches data in HTML.")

    raw_matches = match.group(1)

    # Convert HTML entities and escaped sequences into valid JSON text.
    decoded_matches = html.unescape(raw_matches)

    return json.loads(decoded_matches)


def parse_matches(matches_data: list[dict]) -> list[dict]:
    """
    Convert raw TOP 14 match dictionaries into a clean tabular format.
    """

    parsed_matches = []

    for match in matches_data:
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
                "competition": "TOP14",
                "match_id": match.get("id"),

                "team_a_id": home_club_id,
                "team_b_id": away_club_id,

                "team_a": get_model_name(home_club_id),
                "team_b": get_model_name(away_club_id),

                "team_a_display": get_display_name(home_club_id),
                "team_b_display": get_display_name(away_club_id),

                "location": "home",
                "score_a": score[0],
                "score_b": score[1],
                "status": status,
                "link": match.get("link"),
            }
        )

    return parsed_matches


def save_matches_csv(matches: list[dict], output_path: Path) -> None:
    """
    Save parsed matches to CSV.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "competition",
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

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_PATH}. "
            "Run python -m src.scrapers.top14_scraper first."
        )

    raw_html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    matches_data = extract_score_slider_matches(raw_html)
    matches = parse_matches(matches_data)

    save_matches_csv(matches, OUTPUT_CSV_PATH)

    print(f"Raw matches in score-slider: {len(matches_data)}")
    print(f"Finished matches extracted: {len(matches)}")
    print(f"Saved parsed matches to: {OUTPUT_CSV_PATH}")

    print("\nPreview:")
    for match in matches:
        print(
            f"{match['team_a_display']} {match['score_a']} - "
            f"{match['score_b']} {match['team_b_display']}"
        )


if __name__ == "__main__":
    main()
"""
Fetch rugby club logos from TheSportsDB.

This script:
- reads the canonical team names from src/teams.py
- searches each team individually on TheSportsDB
- downloads the best available badge/logo
- saves it in docs/assets/img/clubs/
"""

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.generate_rankings import slugify_team_name
from src.teams import get_initial_teams


ROOT_DIR = Path(__file__).resolve().parents[1]

LOGO_OUTPUT_DIR = ROOT_DIR / "docs" / "assets" / "img" / "clubs"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

THESPORTSDB_SEARCH_TEAM_URL = (
    "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
)

SLEEP_BETWEEN_REQUESTS_SECONDS = 2.1


def fetch_team_metadata(team_name: str) -> dict:
    """
    Search one team by name on TheSportsDB.
    """

    params = urlencode({"t": team_name})
    url = f"{THESPORTSDB_SEARCH_TEAM_URL}?{params}"

    request = Request(
        url,
        headers={
            "User-Agent": "EuropeanRugbyRanking/0.1",
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.load(response)


def choose_logo_url(team_metadata: dict) -> str | None:
    """
    Choose the best available image URL for a team.

    strBadge is preferred because it usually corresponds to the club crest.
    """

    teams = team_metadata.get("teams") or []

    if not teams:
        return None

    team = teams[0]

    return (
        team.get("strBadge")
        or team.get("strLogo")
        or team.get("strTeamBadge")
        or team.get("strTeamLogo")
    )


def download_logo(logo_url: str, output_path: Path) -> None:
    """
    Download one logo image.
    """

    request = Request(
        logo_url,
        headers={
            "User-Agent": "EuropeanRugbyRanking/0.1",
        },
    )

    with urlopen(request, timeout=30) as response:
        image_data = response.read()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as file:
        file.write(image_data)


def main() -> None:
    """
    Fetch and download logos for all teams in the Elo model.
    """

    teams = get_initial_teams()

    LOGO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    report = []

    for index, team_name in enumerate(teams, start=1):
        slug = slugify_team_name(team_name)
        output_path = LOGO_OUTPUT_DIR / f"{slug}.png"

        print(f"[{index:02d}/{len(teams)}] Searching logo for {team_name}...")

        try:
            metadata = fetch_team_metadata(team_name)
            logo_url = choose_logo_url(metadata)

            if not logo_url:
                print("  No logo found.")
                report.append(
                    {
                        "team": team_name,
                        "status": "missing",
                        "logo_url": None,
                        "output_path": None,
                    }
                )
            else:
                download_logo(logo_url, output_path)
                print(f"  Saved: {output_path}")

                report.append(
                    {
                        "team": team_name,
                        "status": "downloaded",
                        "logo_url": logo_url,
                        "output_path": str(output_path),
                    }
                )

        except Exception as error:
            print(f"  Error: {error}")

            report.append(
                {
                    "team": team_name,
                    "status": "error",
                    "logo_url": None,
                    "output_path": None,
                    "error": str(error),
                }
            )

        time.sleep(SLEEP_BETWEEN_REQUESTS_SECONDS)

    report_path = PROCESSED_DATA_DIR / "logos_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    downloaded = sum(1 for item in report if item["status"] == "downloaded")
    missing = sum(1 for item in report if item["status"] == "missing")
    errors = sum(1 for item in report if item["status"] == "error")

    print("\n====================================")
    print("Logo download summary")
    print("====================================")
    print(f"Downloaded: {downloaded}")
    print(f"Missing:    {missing}")
    print(f"Errors:     {errors}")
    print(f"Report:     {report_path}")


if __name__ == "__main__":
    main()
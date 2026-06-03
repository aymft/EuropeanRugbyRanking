"""
Test the official URC GraphQL endpoint.

Goal:
- query team ranking/matrix data for the 2025-26 season
- extract official URC team names
"""

import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

URC_GRAPHQL_URL = "https://www.unitedrugby.com/graphql"

OUTPUT_RAW_PATH = RAW_DATA_DIR / "urc_graphql_team_matrix_raw.json"
OUTPUT_NAMES_PATH = PROCESSED_DATA_DIR / "urc_official_team_names.json"


QUERY = """
query getClubMatrixRank($seasonId: [Int]) {
  teammatrixstats(season_id: $seasonId) {
    matrix_name
    teams_data {
      position
      team_id
      team_name
    }
  }
}
"""


def post_graphql_query(query: str, variables: dict) -> dict:
    """
    Send a POST request to the URC GraphQL endpoint.
    """

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
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            ),
            "Origin": "https://stats.unitedrugby.com",
            "Referer": "https://stats.unitedrugby.com/",
        },
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def extract_team_names(response_data: dict) -> list[str]:
    """
    Extract unique team names from the team matrix response.
    """

    matrices = response_data.get("data", {}).get("teammatrixstats") or []

    names = []

    for matrix in matrices:
        teams_data = matrix.get("teams_data") or []

        for team in teams_data:
            name = team.get("team_name")

            if name and name not in names:
                names.append(name)

    return sorted(names)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    variables = {
        "seasonId": [202501],
    }

    response_data = post_graphql_query(QUERY, variables)

    with OUTPUT_RAW_PATH.open("w", encoding="utf-8") as file:
        json.dump(response_data, file, indent=2, ensure_ascii=False)

    names = extract_team_names(response_data)

    with OUTPUT_NAMES_PATH.open("w", encoding="utf-8") as file:
        json.dump(names, file, indent=2, ensure_ascii=False)

    print(f"Saved raw GraphQL response to: {OUTPUT_RAW_PATH}")
    print(f"Saved official URC team names to: {OUTPUT_NAMES_PATH}")

    print(f"\nOfficial URC team names found: {len(names)}")
    for name in names:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
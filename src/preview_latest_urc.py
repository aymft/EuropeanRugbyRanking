"""
Preview latest/current URC matches from the official URC GraphQL endpoint.

This script does not modify any file.
It only prints recent and upcoming URC matches so we can inspect:
- match statuses;
- team names;
- score structure;
- season identifiers.
"""

import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from src.team_registry import (
    get_display_name,
    normalize_team_name,
)


URC_GRAPHQL_URL = "https://www.unitedrugby.com/graphql"

QUERY = """
query GetMatchesData(
  $season_id: [Int!]
  $limit: Int
  $orderBy: String
  $order: String
  $matchStatus: String
) {
  matches(
    season_id: $season_id
    limit: $limit
    orderBy: $orderBy
    order: $order
    matchStatus: $matchStatus
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


def safe_display_name(source_name: str) -> str:
    try:
        club_id = normalize_team_name("urc", source_name)
        return get_display_name(club_id)
    except ValueError:
        return source_name


def get_final_score(team: dict) -> str | None:
    score = team.get("score") or {}
    final_score = score.get("finalScore")

    if final_score is None:
        return None

    return str(final_score)


def format_match(row: dict) -> str:
    match_data = row.get("match_data") or {}

    home_team = match_data.get("homeTeam") or {}
    away_team = match_data.get("awayTeam") or {}

    home_name = safe_display_name(home_team.get("name", ""))
    away_name = safe_display_name(away_team.get("name", ""))

    home_score = get_final_score(home_team)
    away_score = get_final_score(away_team)

    if home_score is not None and away_score is not None:
        score_text = f"{home_score} - {away_score}"
    else:
        score_text = "vs"

    return (
        f"{match_data.get('dateTime')} | "
        f"season={row.get('season_id')} | "
        f"{match_data.get('matchStatus')} | "
        f"id={row.get('id')} | "
        f"{home_name} {score_text} {away_name}"
    )


def main() -> None:
    variables = {
        "season_id": [202501],
        "limit": 80,
        "orderBy": "dateTime",
        "order": "DESC",
    }

    response = post_graphql_query(QUERY, variables)

    if "errors" in response:
        print("GraphQL errors:")
        print(json.dumps(response["errors"], indent=2, ensure_ascii=False))
        return

    matches = response.get("data", {}).get("matches") or []

    print("=" * 80)
    print("URC matches preview")
    print("=" * 80)
    print(f"Matches returned: {len(matches)}")

    statuses = sorted(
        {
            (row.get("match_data") or {}).get("matchStatus", "unknown")
            for row in matches
        }
    )

    seasons = sorted({row.get("season_id") for row in matches})

    print(f"Statuses found: {statuses}")
    print(f"Seasons found: {seasons}")

    finished = [
        row for row in matches
        if (row.get("match_data") or {}).get("matchStatus") in {
            "result",
            "Result",
            "finished",
            "Finished",
        }
    ]

    not_finished = [
        row for row in matches
        if row not in finished
    ]

    print("\n" + "=" * 80)
    print("Latest returned matches")
    print("=" * 80)

    for row in matches[:20]:
        print(format_match(row))

    print("\n" + "=" * 80)
    print("Finished-like matches")
    print("=" * 80)

    for row in finished[:20]:
        print(format_match(row))

    print("\n" + "=" * 80)
    print("Not finished / upcoming-like matches")
    print("=" * 80)

    for row in not_finished[:20]:
        print(format_match(row))


if __name__ == "__main__":
    main()
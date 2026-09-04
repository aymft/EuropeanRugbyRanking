"""
Preview latest/upcoming Premiership Rugby matches.

This script does not modify any file.
It only displays upcoming and latest Premiership matches from the official
Premiership Rugby / rugbyviz feed.
"""

import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from src.season_config import PREMIERSHIP_FEED_URL, PREMIERSHIP_FIXTURES_URL
from src.team_registry import (
    get_display_name,
    normalize_team_name,
)


def fetch_premiership_matches() -> list[dict]:
    request = Request(
        PREMIERSHIP_FEED_URL,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://premiershiprugby.com",
            "Referer": PREMIERSHIP_FIXTURES_URL,
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("status") != "success":
        raise RuntimeError(f"Unexpected feed status: {data.get('status')}")

    return data.get("data") or []


def safe_display_name(source_name: str | None) -> str:
    if not source_name:
        return "TBC"

    try:
        club_id = normalize_team_name("premiership", source_name)
        return get_display_name(club_id)
    except ValueError:
        return source_name


def parse_datetime_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def format_score(match: dict) -> str:
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}

    home_score = home_team.get("score")
    away_score = away_team.get("score")

    if home_score is not None and away_score is not None:
        return f"{home_score} - {away_score}"

    return "vs"


def format_match(match: dict) -> str:
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}

    home = safe_display_name(home_team.get("name"))
    away = safe_display_name(away_team.get("name"))

    return (
        f"{match.get('date')} | "
        f"round={match.get('round')} | "
        f"status={match.get('status')} | "
        f"id={match.get('id')} | "
        f"{home} {format_score(match)} {away}"
    )


def main() -> None:
    matches = fetch_premiership_matches()

    now = datetime.now(timezone.utc)

    statuses = sorted({match.get("status", "unknown") for match in matches})
    rounds = sorted(
        {
            match.get("round")
            for match in matches
            if match.get("round") is not None
        }
    )

    upcoming = []

    for match in matches:
        if match.get("status") == "result":
            continue

        date_raw = match.get("date")
        if not date_raw:
            continue

        match_date = parse_datetime_utc(date_raw)

        if match_date >= now:
            upcoming.append(match)

    upcoming = sorted(upcoming, key=lambda match: match.get("date", ""))

    latest_results = [
        match
        for match in matches
        if match.get("status") == "result"
    ]

    latest_results = sorted(
        latest_results,
        key=lambda match: match.get("date", ""),
        reverse=True,
    )

    print("=" * 100)
    print("Premiership Rugby preview")
    print("=" * 100)
    print(f"Matches returned: {len(matches)}")
    print(f"Statuses found: {statuses}")
    print(f"Rounds found: {rounds}")

    print("\n" + "=" * 100)
    print("Upcoming Premiership matches")
    print("=" * 100)
    print(f"Upcoming matches found: {len(upcoming)}")

    if upcoming:
        for match in upcoming[:20]:
            print(format_match(match))
    else:
        print("No upcoming Premiership match found.")

    print("\n" + "=" * 100)
    print("Latest Premiership results")
    print("=" * 100)

    for match in latest_results[:10]:
        print(format_match(match))


if __name__ == "__main__":
    main()

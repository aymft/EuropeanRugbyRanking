"""
Generate live/upcoming/recent rugby results for the website.

Output:
    docs/data/live_results.json

This file is independent from the Elo ranking pipeline.
It does not modify matches_history.csv.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from src.season_config import (
    PREMIERSHIP_FEED_URL,
    PREMIERSHIP_FIXTURES_URL,
    URC_GRAPHQL_URL,
    URC_SEASON_ID,
)
from src.team_registry import get_display_name, normalize_team_name


ROOT_DIR = Path(__file__).resolve().parents[1]
LIVE_RESULTS_PATH = ROOT_DIR / "docs" / "data" / "live_results.json"
MAX_UPCOMING_MATCHES = 10


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def normalize_status(raw_status: str | None) -> str:
    value = (raw_status or "").lower()

    if value in {"result", "finished", "complete", "completed", "full-time", "ft"}:
        return "finished"

    if value in {"live", "in-progress", "in_progress", "playing"}:
        return "live"

    if value in {"fixture", "not-started", "not_started", "scheduled", "upcoming"}:
        return "scheduled"

    return value or "unknown"


def make_match(
    *,
    competition: str,
    source: str,
    match_id: str | int | None,
    raw_status: str | None,
    home_team: str | None,
    away_team: str | None,
    home_score: int | None = None,
    away_score: int | None = None,
    kickoff_utc: str | None = None,
    kickoff_display: str | None = None,
    round_label: str | int | None = None,
    minute: int | None = None,
    venue: str | None = None,
) -> dict:
    return {
        "competition": competition,
        "source": source,
        "id": str(match_id) if match_id is not None else "",
        "status": normalize_status(raw_status),
        "raw_status": raw_status or "",
        "round": str(round_label) if round_label is not None else "",
        "kickoff_utc": kickoff_utc or "",
        "kickoff_display": kickoff_display or "",
        "minute": minute,
        "venue": venue or "",
        "home_team": home_team or "TBC",
        "away_team": away_team or "TBC",
        "home_score": home_score,
        "away_score": away_score,
    }


def normalize_display_name(source: str, raw_name: str | None) -> str:
    """Return the project display name while allowing future TBC placeholders."""

    if not raw_name:
        return "TBC"

    try:
        club_id = normalize_team_name(source, raw_name)
        return get_display_name(club_id)
    except ValueError:
        return raw_name


def limit_live_page_matches(matches: list[dict]) -> list[dict]:
    """Keep all live/recent results and only the next scheduled fixtures."""

    live = [match for match in matches if match["status"] == "live"]
    finished = [match for match in matches if match["status"] == "finished"]
    scheduled = sorted(
        (match for match in matches if match["status"] == "scheduled"),
        key=lambda match: match.get("kickoff_utc") or match.get("kickoff_display") or "",
    )[:MAX_UPCOMING_MATCHES]

    return sort_matches(live + scheduled + finished)


def sort_matches(matches: list[dict]) -> list[dict]:
    def key(match: dict) -> tuple[int, str]:
        status_order = {
            "live": 0,
            "scheduled": 1,
            "finished": 2,
            "unknown": 3,
        }

        return (
            status_order.get(match.get("status", "unknown"), 9),
            match.get("kickoff_utc") or match.get("kickoff_display") or "",
        )

    return sorted(matches, key=key)


# ---------------------------------------------------------------------------
# Premiership
# ---------------------------------------------------------------------------

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
        raise RuntimeError(f"Unexpected Premiership feed status: {data.get('status')}")

    return data.get("data") or []


def build_premiership_live_results() -> list[dict]:
    raw_matches = fetch_premiership_matches()
    now = datetime.now(timezone.utc)

    selected = []

    for match in raw_matches:
        kickoff = parse_iso_datetime(match.get("date"))
        raw_status = match.get("status")
        status = normalize_status(raw_status)

        # Keep live matches, upcoming matches, and recent finished matches.
        keep = status in {"live", "scheduled"}

        if status == "finished" and kickoff is not None:
            age_hours = (now - kickoff).total_seconds() / 3600
            keep = age_hours <= 72

        if not keep:
            continue

        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        venue = match.get("venue") or {}

        selected.append(
            make_match(
                competition="PREMIERSHIP",
                source="premiership_rugbyviz",
                match_id=match.get("id"),
                raw_status=raw_status,
                round_label=match.get("round"),
                kickoff_utc=kickoff.isoformat(timespec="seconds") if kickoff else match.get("date", ""),
                home_team=normalize_display_name("premiership", home.get("name")),
                away_team=normalize_display_name("premiership", away.get("name")),
                home_score=home.get("score"),
                away_score=away.get("score"),
                minute=match.get("minute"),
                venue=venue.get("name"),
            )
        )

    return limit_live_page_matches(selected)


# ---------------------------------------------------------------------------
# URC
# ---------------------------------------------------------------------------

def fetch_urc_matches() -> list[dict]:
    query = """
    query Matches($season_id: [Int!]) {
      matches(
        season_id: $season_id
        limit: 200
        orderBy: "dateTime"
        order: "ASC"
      ) {
        id
        season_id
        match_data {
          dateTime
          matchStatus
          round
          venue {
            name
          }
          homeTeam {
            name
            score {
              finalScore
            }
          }
          awayTeam {
            name
            score {
              finalScore
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "season_id": [URC_SEASON_ID],
        },
    }

    request = Request(
        URC_GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://stats.unitedrugby.com",
            "Referer": "https://stats.unitedrugby.com/",
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("errors"):
        raise RuntimeError(f"URC GraphQL errors: {data['errors']}")

    return data.get("data", {}).get("matches") or []


def get_urc_score(team: dict) -> int | None:
    score = team.get("score") or {}
    value = score.get("finalScore")

    if value is None:
        return None

    return int(value)


def build_urc_live_results() -> list[dict]:
    raw_matches = fetch_urc_matches()
    now = datetime.now(timezone.utc)

    selected = []

    for row in raw_matches:
        match = row.get("match_data") or {}
        kickoff = parse_iso_datetime(match.get("dateTime"))
        raw_status = match.get("matchStatus")
        status = normalize_status(raw_status)

        keep = status in {"live", "scheduled"}

        if status == "finished" and kickoff is not None:
            age_hours = (now - kickoff).total_seconds() / 3600
            keep = age_hours <= 72

        if not keep:
            continue

        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        venue = match.get("venue") or {}

        selected.append(
            make_match(
                competition="URC",
                source="urc_graphql",
                match_id=row.get("id"),
                raw_status=raw_status,
                round_label=match.get("round"),
                kickoff_utc=kickoff.isoformat(timespec="seconds") if kickoff else match.get("dateTime", ""),
                home_team=normalize_display_name("urc", home.get("name")),
                away_team=normalize_display_name("urc", away.get("name")),
                home_score=get_urc_score(home),
                away_score=get_urc_score(away),
                venue=venue.get("name"),
            )
        )

    return limit_live_page_matches(selected)


# ---------------------------------------------------------------------------
# TOP 14
# ---------------------------------------------------------------------------

def build_top14_live_results() -> list[dict]:
    """
    Temporary TOP 14 adapter.

    It reuses the existing local preview script and parses its printed output.
    This avoids duplicating the TOP 14 score-slider parser for now.

    Expected line format:
        06/06 21h05 | not-started | 11488 | Union Bordeaux-Bègles 0 - 0 ASM Clermont
    """

    command = [sys.executable, "-m", "src.preview_latest_top14"]

    try:
        completed = subprocess.run(
            command,
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
            timeout=40,
        )
    except Exception as error:
        print(f"[TOP14] Could not run preview_latest_top14: {error}")
        return []

    matches = []
    seen_match_ids = set()

    pattern = re.compile(
        r"^(?P<kickoff>[^|]+)\s*\|\s*"
        r"(?P<status>[^|]+)\s*\|\s*"
        r"(?P<id>[^|]+)\s*\|\s*"
        r"(?P<home>.+?)\s+"
        r"(?P<home_score>\d+)\s*-\s*"
        r"(?P<away_score>\d+)\s+"
        r"(?P<away>.+)$"
    )

    for line in completed.stdout.splitlines():
        line = line.strip()
        match = pattern.match(line)

        if not match:
            continue

        groups = match.groupdict()
        match_id = groups["id"].strip()

        if match_id in seen_match_ids:
            continue

        seen_match_ids.add(match_id)

        matches.append(
            make_match(
                competition="TOP14",
                source="lnr_top14_preview",
                match_id=match_id,
                raw_status=groups["status"].strip(),
                kickoff_display=groups["kickoff"].strip(),
                home_team=groups["home"].strip(),
                away_team=groups["away"].strip(),
                home_score=int(groups["home_score"]),
                away_score=int(groups["away_score"]),
            )
        )

    return sort_matches(matches)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    competitions = []

    builders = [
        ("TOP14", "TOP 14", build_top14_live_results),
        ("URC", "United Rugby Championship", build_urc_live_results),
        ("PREMIERSHIP", "Premiership Rugby", build_premiership_live_results),
    ]

    for code, name, builder in builders:
        try:
            matches = builder()
            error = ""
        except Exception as exc:
            matches = []
            error = str(exc)
            print(f"[{code}] Error: {error}")

        competitions.append(
            {
                "code": code,
                "name": name,
                "matches": matches,
                "error": error,
            }
        )

    output = {
        "generated_at": now_utc_iso(),
        "refresh_seconds": 120,
        "competitions": competitions,
    }

    LIVE_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LIVE_RESULTS_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(output, json_file, indent=2, ensure_ascii=False)

    print(f"Live results written to: {LIVE_RESULTS_PATH}")

    for competition in competitions:
        print(
            f"{competition['code']}: "
            f"{len(competition['matches'])} matches"
            + (f" | error: {competition['error']}" if competition["error"] else "")
        )


if __name__ == "__main__":
    main()

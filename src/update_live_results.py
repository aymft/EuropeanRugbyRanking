"""
Generate live/upcoming/recent rugby results for the website.

Output:
    docs/data/live_results.json

This file is independent from the Elo ranking pipeline.
It does not modify matches_history.csv.
"""

import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from src.preview_latest_top14 import (
    extract_current_week,
    extract_matches,
    fetch_top14_page,
)
from src.season_config import (
    EPCR_CHALLENGE_CUP_FEED_URL,
    EPCR_CHALLENGE_CUP_FIXTURES_URL,
    EPCR_CHAMPIONS_CUP_FEED_URL,
    EPCR_CHAMPIONS_CUP_FIXTURES_URL,
    PREMIERSHIP_FEED_URL,
    PREMIERSHIP_FIXTURES_URL,
    URC_GRAPHQL_URL,
    URC_SEASON_ID,
)
from src.team_registry import get_display_name, normalize_team_name


ROOT_DIR = Path(__file__).resolve().parents[1]
LIVE_RESULTS_PATH = ROOT_DIR / "docs" / "data" / "live_results.json"
SITE_TIMEZONE_NAME = "Europe/Paris"
SITE_TIMEZONE = ZoneInfo(SITE_TIMEZONE_NAME)
PAGE_REFRESH_SECONDS = 120


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def preserve_generated_at_if_unchanged(output: dict) -> dict:
    """Avoid rewriting the live file when no fixture, status, or score changed."""

    if not LIVE_RESULTS_PATH.is_file():
        return output

    try:
        existing = json.loads(LIVE_RESULTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return output

    current_payload = {key: value for key, value in output.items() if key != "generated_at"}
    existing_payload = {
        key: value for key, value in existing.items() if key != "generated_at"
    }

    if current_payload == existing_payload and existing.get("generated_at"):
        output["generated_at"] = existing["generated_at"]

    return output


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

    if value in {
        "live",
        "in-progress",
        "in_progress",
        "playing",
        "first-half",
        "first_half",
        "half-time",
        "halftime",
        "second-half",
        "second_half",
    }:
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
    home_club_id: str = "",
    away_club_id: str = "",
    home_score: int | None = None,
    away_score: int | None = None,
    kickoff_utc: str | None = None,
    kickoff_display: str | None = None,
    round_label: str | int | None = None,
    minute: int | None = None,
    venue: str | None = None,
    match_url: str | None = None,
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
        "match_url": match_url or "",
        "home_club_id": home_club_id,
        "away_club_id": away_club_id,
        "home_team": home_team or "TBC",
        "away_team": away_team or "TBC",
        "home_score": home_score,
        "away_score": away_score,
    }


def normalize_team(source: str, raw_name: str | None) -> tuple[str, str]:
    """Return ``(club_id, display_name)`` while allowing future placeholders."""

    if not raw_name:
        return "", "TBC"

    try:
        club_id = normalize_team_name(source, raw_name)
        return club_id, get_display_name(club_id)
    except ValueError:
        return "", raw_name


def get_weekend_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Return the current or next Friday-to-Monday window in Paris time."""

    reference = now or datetime.now(timezone.utc)
    local_reference = reference.astimezone(SITE_TIMEZONE)
    weekday = local_reference.weekday()

    if weekday < 4:
        friday_date = local_reference.date() + timedelta(days=4 - weekday)
    else:
        friday_date = local_reference.date() - timedelta(days=weekday - 4)

    start_local = datetime.combine(friday_date, time.min, tzinfo=SITE_TIMEZONE)
    end_local = start_local + timedelta(days=3)

    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def select_weekend_matches(
    matches: list[dict],
    weekend_start: datetime | None = None,
    weekend_end: datetime | None = None,
) -> list[dict]:
    """Keep matches whose kickoff falls in the current/upcoming weekend."""

    if weekend_start is None or weekend_end is None:
        weekend_start, weekend_end = get_weekend_window()

    selected = []

    for match in matches:
        kickoff = parse_iso_datetime(match.get("kickoff_utc"))

        if kickoff is not None and weekend_start <= kickoff < weekend_end:
            selected.append(match)

    return sort_matches(selected)


def sort_matches(matches: list[dict]) -> list[dict]:
    def key(match: dict) -> tuple[str, str]:
        return (
            match.get("kickoff_utc") or match.get("kickoff_display") or "",
            match.get("id") or "",
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
    selected = []

    for match in raw_matches:
        kickoff = parse_iso_datetime(match.get("date"))
        raw_status = match.get("status")
        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        venue = match.get("venue") or {}
        home_club_id, home_name = normalize_team("premiership", home.get("name"))
        away_club_id, away_name = normalize_team("premiership", away.get("name"))

        selected.append(
            make_match(
                competition="PREMIERSHIP",
                source="premiership_rugbyviz",
                match_id=match.get("id"),
                raw_status=raw_status,
                round_label=match.get("round"),
                kickoff_utc=kickoff.isoformat(timespec="seconds") if kickoff else match.get("date", ""),
                home_team=home_name,
                away_team=away_name,
                home_club_id=home_club_id,
                away_club_id=away_club_id,
                home_score=home.get("score"),
                away_score=away.get("score"),
                minute=match.get("minute"),
                venue=venue.get("name"),
            )
        )

    return select_weekend_matches(selected)


# ---------------------------------------------------------------------------
# EPCR
# ---------------------------------------------------------------------------

def fetch_epcr_matches(feed_url: str, fixtures_url: str) -> list[dict]:
    request = Request(
        feed_url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "Mozilla/5.0 EuropeanRugbyRanking/0.1",
            "Origin": "https://www.epcrugby.com",
            "Referer": fixtures_url,
        },
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    if data.get("status") != "success":
        raise RuntimeError(f"Unexpected EPCR feed status: {data.get('status')}")

    return data.get("data") or []


def build_epcr_live_results(
    *,
    competition: str,
    feed_url: str,
    fixtures_url: str,
) -> list[dict]:
    raw_matches = fetch_epcr_matches(feed_url, fixtures_url)
    selected = []

    for match in raw_matches:
        kickoff = parse_iso_datetime(match.get("date"))
        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        venue = match.get("venue") or {}
        home_club_id, home_name = normalize_team("epcr", home.get("name"))
        away_club_id, away_name = normalize_team("epcr", away.get("name"))

        selected.append(
            make_match(
                competition=competition,
                source="epcr_rugbyviz",
                match_id=match.get("id"),
                raw_status=match.get("status"),
                round_label=match.get("round"),
                kickoff_utc=(
                    kickoff.isoformat(timespec="seconds")
                    if kickoff
                    else match.get("date", "")
                ),
                home_team=home_name,
                away_team=away_name,
                home_club_id=home_club_id,
                away_club_id=away_club_id,
                home_score=home.get("score"),
                away_score=away.get("score"),
                minute=match.get("minute"),
                venue=venue.get("name"),
            )
        )

    return select_weekend_matches(selected)


def build_champions_cup_live_results() -> list[dict]:
    return build_epcr_live_results(
        competition="CHAMPIONS_CUP",
        feed_url=EPCR_CHAMPIONS_CUP_FEED_URL,
        fixtures_url=EPCR_CHAMPIONS_CUP_FIXTURES_URL,
    )


def build_challenge_cup_live_results() -> list[dict]:
    return build_epcr_live_results(
        competition="CHALLENGE_CUP",
        feed_url=EPCR_CHALLENGE_CUP_FEED_URL,
        fixtures_url=EPCR_CHALLENGE_CUP_FIXTURES_URL,
    )


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
    selected = []

    for row in raw_matches:
        match = row.get("match_data") or {}
        kickoff = parse_iso_datetime(match.get("dateTime"))
        raw_status = match.get("matchStatus")
        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        venue = match.get("venue") or {}
        home_club_id, home_name = normalize_team("urc", home.get("name"))
        away_club_id, away_name = normalize_team("urc", away.get("name"))

        selected.append(
            make_match(
                competition="URC",
                source="urc_graphql",
                match_id=row.get("id"),
                raw_status=raw_status,
                round_label=match.get("round"),
                kickoff_utc=kickoff.isoformat(timespec="seconds") if kickoff else match.get("dateTime", ""),
                home_team=home_name,
                away_team=away_name,
                home_club_id=home_club_id,
                away_club_id=away_club_id,
                home_score=get_urc_score(home),
                away_score=get_urc_score(away),
                venue=venue.get("name"),
            )
        )

    return select_weekend_matches(selected)


# ---------------------------------------------------------------------------
# TOP 14
# ---------------------------------------------------------------------------

def build_top14_live_results() -> list[dict]:
    """Build the live page data directly from the LNR score slider."""

    raw_html = fetch_top14_page()
    current_week = extract_current_week(raw_html)
    raw_matches = extract_matches(raw_html)
    matches = []

    for match in raw_matches:
        home = match.get("hosting_club") or {}
        away = match.get("visiting_club") or {}
        score = match.get("score") or []
        timer = match.get("timer") or {}
        kickoff_raw = timer.get("firstPeriodStartDate")
        kickoff = parse_iso_datetime(kickoff_raw)
        home_club_id, home_name = normalize_team("lnr_top14", home.get("name"))
        away_club_id, away_name = normalize_team("lnr_top14", away.get("name"))

        matches.append(
            make_match(
                competition="TOP14",
                source="lnr_top14",
                match_id=match.get("id"),
                raw_status=match.get("status"),
                round_label=current_week.get("name"),
                kickoff_utc=(
                    kickoff.isoformat(timespec="seconds")
                    if kickoff
                    else kickoff_raw or ""
                ),
                kickoff_display=f"{match.get('date', '')} {match.get('time', '')}".strip(),
                home_team=home_name,
                away_team=away_name,
                home_club_id=home_club_id,
                away_club_id=away_club_id,
                home_score=int(score[0]) if len(score) == 2 else None,
                away_score=int(score[1]) if len(score) == 2 else None,
                match_url=match.get("link"),
            )
        )

    return select_weekend_matches(matches)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    competitions = []
    weekend_start, weekend_end = get_weekend_window()

    builders = [
        ("TOP14", "TOP 14", build_top14_live_results),
        ("URC", "United Rugby Championship", build_urc_live_results),
        ("PREMIERSHIP", "Premiership Rugby", build_premiership_live_results),
        ("CHAMPIONS_CUP", "Investec Champions Cup", build_champions_cup_live_results),
        ("CHALLENGE_CUP", "EPCR Challenge Cup", build_challenge_cup_live_results),
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
        "refresh_seconds": PAGE_REFRESH_SECONDS,
        "source_refresh_seconds": 300,
        "timezone": SITE_TIMEZONE_NAME,
        "weekend_start": weekend_start.isoformat(timespec="seconds"),
        "weekend_end": weekend_end.isoformat(timespec="seconds"),
        "competitions": competitions,
    }
    output = preserve_generated_at_if_unchanged(output)

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

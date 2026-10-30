"""Client and parsers for the official TOP 14 fixtures page.

The LNR page renders the current round server-side and exposes its data as
JSON attributes on the ``score-slider`` component. Keeping all extraction
logic here prevents the ranking updater, preview command and website feed from
silently drifting apart when the component changes.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from src.season_config import SEASON_LABEL, TOP14_RESULTS_URL


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
LNR_TIMEZONE = ZoneInfo("Europe/Paris")

REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
    "User-Agent": (
        "Mozilla/5.0 (compatible; EuropeanRugbyRanking/1.0; "
        "+https://github.com/aymft/EuropeanRugbyRanking)"
    ),
}


def fetch_top14_page(url: str = TOP14_RESULTS_URL) -> str:
    """Download the official LNR fixtures/results page."""

    request = Request(url, headers=REQUEST_HEADERS)

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_score_slider_attribute(raw_html: str, attribute: str):
    """Decode one JSON-bound attribute from the LNR ``score-slider``."""

    pattern = re.compile(
        rf"<score-slider\b[^>]*:{re.escape(attribute)}=(['\"])(.*?)\1",
        flags=re.DOTALL,
    )
    match = pattern.search(raw_html)

    if not match:
        raise RuntimeError(
            f"Could not find score-slider :{attribute} data on the LNR page."
        )

    try:
        return json.loads(html.unescape(match.group(2)))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in score-slider :{attribute} data."
        ) from exc


def extract_weeks(raw_html: str) -> list[dict]:
    weeks = extract_score_slider_attribute(raw_html, "weeks")

    if not isinstance(weeks, list) or not weeks:
        raise RuntimeError("The LNR score-slider weeks list is empty or invalid.")

    return weeks


def extract_current_week(raw_html: str) -> dict:
    """Return the current round, supporting both old and current LNR markup."""

    try:
        current_week = extract_score_slider_attribute(raw_html, "current-week")
    except RuntimeError:
        current_week = extract_weeks(raw_html)[0]

    if not isinstance(current_week, dict) or not current_week.get("slug"):
        raise RuntimeError("The LNR current-week payload is invalid.")

    return current_week


def extract_matches(raw_html: str) -> list[dict]:
    """Return and validate the current round's raw LNR match objects."""

    matches = extract_score_slider_attribute(raw_html, "matches")

    if not isinstance(matches, list) or not matches:
        raise RuntimeError("The LNR score-slider matches list is empty or invalid.")

    required_fields = {"id", "hosting_club", "visiting_club", "status"}
    invalid_ids = [
        match.get("id") if isinstance(match, dict) else None
        for match in matches
        if not isinstance(match, dict) or not required_fields.issubset(match)
    ]

    if invalid_ids:
        raise RuntimeError(
            "The LNR match schema is missing required fields for match IDs: "
            f"{invalid_ids}"
        )

    return matches


def get_match_kickoff_iso(match: dict) -> str:
    """Return an ISO kickoff, with a fallback for reduced LNR payloads."""

    timer = match.get("timer") or {}
    kickoff = timer.get("firstPeriodStartDate")

    if kickoff:
        return kickoff

    date_value = match.get("date")
    time_value = match.get("time")

    if not date_value or not time_value:
        return ""

    try:
        day, month = (int(part) for part in date_value.split("/", maxsplit=1))
        hour, minute = (
            int(part) for part in time_value.lower().split("h", maxsplit=1)
        )
        season_start_year, season_end_year = (
            int(part) for part in SEASON_LABEL.split("-", maxsplit=1)
        )
        year = season_start_year if month >= 7 else season_end_year
        return datetime(
            year,
            month,
            day,
            hour,
            minute,
            tzinfo=LNR_TIMEZONE,
        ).isoformat()
    except (TypeError, ValueError):
        return ""


def save_html(raw_html: str) -> Path:
    """Save a diagnostic copy of the official page."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / "top14_official_page.html"
    output_path.write_text(raw_html, encoding="utf-8")
    return output_path


def main() -> None:
    raw_html = fetch_top14_page()
    current_week = extract_current_week(raw_html)
    matches = extract_matches(raw_html)
    output_path = save_html(raw_html)

    print(f"Saved HTML to: {output_path}")
    print(
        f"LNR round: {current_week.get('name')} ({current_week.get('slug')}) | "
        f"matches: {len(matches)}"
    )


if __name__ == "__main__":
    main()

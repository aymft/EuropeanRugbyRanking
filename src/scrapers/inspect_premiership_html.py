"""
Inspect the downloaded Premiership Rugby HTML page.

Goal:
- check whether match data are directly present in the HTML
- search for team names, fixtures, scores and possible internal API endpoints
"""

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT_DIR / "data" / "raw" / "premiership_official_page.html"


PATTERNS = [
    "Bath Rugby",
    "Bristol Bears",
    "Exeter Chiefs",
    "Gloucester",
    "Harlequins",
    "Leicester Tigers",
    "Newcastle",
    "Northampton Saints",
    "Sale Sharks",
    "Saracens",
    "fixtures",
    "Fixtures",
    "match",
    "Match",
    "score",
    "Score",
    "homeTeam",
    "awayTeam",
    "home",
    "away",
    "api",
    "/api/",
    "__NUXT__",
    "__NEXT_DATA__",
    "window.",
]


def clean_context(text: str) -> str:
    """
    Make an HTML context easier to read in the terminal.
    """

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def print_pattern_contexts(html: str) -> None:
    """
    Print short contexts around useful patterns.
    """

    for pattern in PATTERNS:
        print("\n" + "=" * 80)
        print(f"Pattern: {pattern!r}")

        matches = list(re.finditer(re.escape(pattern), html, flags=re.IGNORECASE))
        print(f"Occurrences: {len(matches)}")

        for match in matches[:3]:
            start = max(match.start() - 300, 0)
            end = min(match.end() + 300, len(html))
            context = clean_context(html[start:end])
            print(f"\n--- context around index {match.start()} ---")
            print(context)


def print_script_sources(html: str) -> None:
    """
    Print external JavaScript files loaded by the page.
    """

    script_sources = re.findall(r'<script[^>]+src="([^"]+)"', html)

    print("\n" + "=" * 80)
    print("Script sources")
    print("=" * 80)

    for src in script_sources:
        print(src)


def print_possible_urls(html: str) -> None:
    """
    Print URLs or paths that may correspond to internal APIs.
    """

    urls = sorted(
        set(
            re.findall(
                r'https?://[^"\']+|/[^"\']*(?:api|fixture|fixtures|match|matches|team|teams)[^"\']*',
                html,
                flags=re.IGNORECASE,
            )
        )
    )

    print("\n" + "=" * 80)
    print("Possible useful URLs")
    print("=" * 80)

    for url in urls[:150]:
        print(url)


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_PATH}. "
            "Run python -m src.scrapers.premiership_scraper first."
        )

    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    print(f"Loaded HTML: {HTML_PATH}")
    print(f"HTML length: {len(html)} characters")

    print_pattern_contexts(html)
    print_script_sources(html)
    print_possible_urls(html)


if __name__ == "__main__":
    main()
"""
Inspect the downloaded URC HTML page.

Goal:
- identify JavaScript assets loaded by the app
- search for possible API endpoints
- check whether team names appear directly in the initial HTML
"""

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT_DIR / "data" / "raw" / "urc_official_page.html"


PATTERNS = [
    "Leinster",
    "Munster",
    "Ulster",
    "Connacht",
    "Glasgow",
    "Edinburgh",
    "Cardiff",
    "Scarlets",
    "Ospreys",
    "Dragons",
    "Benetton",
    "Zebre",
    "Bulls",
    "Stormers",
    "Sharks",
    "Lions",
    "api",
    "graphql",
    "fixtures",
    "matches",
    "teams",
    "static",
    "assets",
    "window.",
]


def clean_context(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def print_pattern_contexts(html: str) -> None:
    for pattern in PATTERNS:
        print("\n" + "=" * 80)
        print(f"Pattern: {pattern!r}")

        matches = list(re.finditer(re.escape(pattern), html, flags=re.IGNORECASE))
        print(f"Occurrences: {len(matches)}")

        for match in matches[:3]:
            start = max(match.start() - 250, 0)
            end = min(match.end() + 250, len(html))
            context = clean_context(html[start:end])
            print(f"\n--- context around index {match.start()} ---")
            print(context)


def print_script_sources(html: str) -> None:
    script_sources = re.findall(r'<script[^>]+src="([^"]+)"', html)

    print("\n" + "=" * 80)
    print("Script sources")
    print("=" * 80)

    for src in script_sources:
        print(src)


def print_link_sources(html: str) -> None:
    link_sources = re.findall(r'<link[^>]+href="([^"]+)"', html)

    print("\n" + "=" * 80)
    print("Link sources")
    print("=" * 80)

    for href in link_sources:
        print(href)


def print_possible_urls(html: str) -> None:
    urls = sorted(
        set(
            re.findall(
                r'https?://[^"\']+|/[^"\']*(?:api|graphql|fixture|fixtures|match|matches|team|teams|static|assets)[^"\']*',
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
            "Run python -m src.scrapers.urc_scraper first."
        )

    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    print(f"Loaded HTML: {HTML_PATH}")
    print(f"HTML length: {len(html)} characters")

    print_pattern_contexts(html)
    print_script_sources(html)
    print_link_sources(html)
    print_possible_urls(html)


if __name__ == "__main__":
    main()
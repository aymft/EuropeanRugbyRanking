"""
Inspect URC JavaScript assets.

The URC website is a JavaScript application. The initial HTML does not contain
team or match data, so we inspect the main JS bundle to find API endpoints.
"""

import re
from pathlib import Path
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"

URC_JS_URL = "https://stats.unitedrugby.com/assets/js/index-CISs8jk3.js"
OUTPUT_PATH = RAW_DATA_DIR / "urc_main_index_js.txt"


PATTERNS = [
    "graphql",
    "GraphQL",
    "apollo",
    "query",
    "mutation",
    "fixture",
    "fixtures",
    "match",
    "matches",
    "team",
    "teams",
    "season",
    "2025",
    "2025-26",
    "United Rugby Championship",
    "Leinster",
    "Munster",
    "Ulster",
    "Bulls",
    "Stormers",
    "Sharks",
    "api",
    "https://",
]


def fetch_js() -> str:
    request = Request(
        URC_JS_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            )
        },
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_context(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def print_pattern_contexts(js: str) -> None:
    for pattern in PATTERNS:
        print("\n" + "=" * 80)
        print(f"Pattern: {pattern!r}")

        matches = list(re.finditer(re.escape(pattern), js, flags=re.IGNORECASE))
        print(f"Occurrences: {len(matches)}")

        for match in matches[:5]:
            start = max(match.start() - 300, 0)
            end = min(match.end() + 300, len(js))
            context = clean_context(js[start:end])
            print(f"\n--- context around index {match.start()} ---")
            print(context)


def print_urls(js: str) -> None:
    urls = sorted(set(re.findall(r"https?://[^\"'`\\)]+", js)))

    print("\n" + "=" * 80)
    print("URLs found in JS")
    print("=" * 80)

    for url in urls[:200]:
        print(url)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    js = fetch_js()

    OUTPUT_PATH.write_text(js, encoding="utf-8")

    print(f"Saved JS to: {OUTPUT_PATH}")
    print(f"JS length: {len(js)} characters")

    print_pattern_contexts(js)
    print_urls(js)


if __name__ == "__main__":
    main()
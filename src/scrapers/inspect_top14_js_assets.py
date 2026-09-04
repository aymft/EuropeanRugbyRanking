"""
Inspect TOP 14 JavaScript assets.

Goal:
- list JS files loaded by the official TOP 14 page
- download them locally
- search for API endpoints or functions related to calendar/results rounds
"""

import re
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"

HTML_PATH = RAW_DATA_DIR / "top14_official_page.html"
BASE_URL = "https://top14.lnr.fr"

OUTPUT_DIR = RAW_DATA_DIR / "top14_js_assets"


PATTERNS = [
    "api",
    "/api/",
    "calendrier",
    "resultats",
    "résultats",
    "journee",
    "journée",
    "week",
    "current-week",
    "score-slider",
    "matches",
    "match",
    "feuille-de-match",
    "2026-2027",
    "j1",
    "14522",
    "round",
    "competition",
]


def fetch_url(url: str) -> str:
    """
    Download a URL as text.
    """

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            )
        },
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_script_sources(html: str) -> list[str]:
    """
    Extract JS script URLs from HTML.
    """

    sources = re.findall(r'<script[^>]+src="([^"]+)"', html)

    full_urls = []

    for source in sources:
        full_urls.append(urljoin(BASE_URL, source))

    return full_urls


def safe_filename(url: str) -> str:
    """
    Convert a URL into a local filename.
    """

    filename = url.split("/")[-1].split("?")[0]

    if not filename:
        filename = "index.js"

    return filename


def clean_context(text: str) -> str:
    """
    Make JS context easier to read.
    """

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def inspect_js(url: str, content: str) -> None:
    """
    Search useful patterns in one JS asset.
    """

    print("\n" + "=" * 100)
    print(f"Inspecting: {url}")
    print(f"Length: {len(content)} characters")

    for pattern in PATTERNS:
        matches = list(re.finditer(re.escape(pattern), content, flags=re.IGNORECASE))

        if not matches:
            continue

        print("\n" + "-" * 80)
        print(f"Pattern {pattern!r}: {len(matches)} occurrences")

        for match in matches[:5]:
            start = max(match.start() - 250, 0)
            end = min(match.end() + 250, len(content))
            print(f"\n--- context around index {match.start()} ---")
            print(clean_context(content[start:end]))

    urls = sorted(set(re.findall(r"https?://[^\"'`\\)]+|/[^\"'`\\)]*(?:api|calendrier|resultat|match|journee|week|round)[^\"'`\\)]*", content, flags=re.IGNORECASE)))

    if urls:
        print("\n" + "-" * 80)
        print("Possible URLs/endpoints")
        for item in urls[:100]:
            print(item)


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_PATH}. "
            "Run python -m src.scrapers.top14_scraper first."
        )

    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    script_urls = extract_script_sources(html)

    print(f"Script assets found: {len(script_urls)}")

    for url in script_urls:
        print(f"  - {url}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for url in script_urls:
        print("\nDownloading:", url)

        try:
            content = fetch_url(url)
        except Exception as error:
            print(f"Failed to download {url}: {error}")
            continue

        output_path = OUTPUT_DIR / safe_filename(url)
        output_path.write_text(content, encoding="utf-8")

        inspect_js(url, content)


if __name__ == "__main__":
    main()

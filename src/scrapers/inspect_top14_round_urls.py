"""
Inspect TOP 14 official HTML to find round URLs.

Goal:
- identify links to TOP 14 rounds such as j1, j2, ..., j26
- prepare the next scraper that will fetch multiple rounds
"""

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT_DIR / "data" / "raw" / "top14_official_page.html"


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_PATH}. "
            "Run python -m src.scrapers.top14_scraper first."
        )

    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    patterns = [
        r'https://top14\.lnr\.fr/calendrier-et-resultats[^"\']*',
        r'/calendrier-et-resultats[^"\']*',
        r'https://top14\.lnr\.fr/feuille-de-match/2026-2027/j\d+[^"\']*',
        r'/feuille-de-match/2026-2027/j\d+[^"\']*',
    ]

    urls = set()

    for pattern in patterns:
        urls.update(re.findall(pattern, html))

    print(f"URLs found: {len(urls)}")

    for url in sorted(urls):
        print(url)


if __name__ == "__main__":
    main()

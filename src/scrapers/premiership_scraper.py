"""
Experimental Premiership Rugby scraper.

First step:
- download the official Premiership fixtures page
- save the raw HTML locally
- inspect whether match and team data are directly available in the HTML
"""

from pathlib import Path
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"

PREMIERSHIP_FIXTURES_URL = "https://premiershiprugby.com/content/202526-fixtures"


def fetch_premiership_page() -> str:
    """
    Download the official Premiership Rugby fixtures page.
    """

    request = Request(
        PREMIERSHIP_FIXTURES_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 EuropeanRugbyRanking/0.1 "
                "(compatible; research scraper)"
            )
        },
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def save_html(html: str) -> Path:
    """
    Save the downloaded HTML locally for inspection.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / "premiership_official_page.html"

    with output_path.open("w", encoding="utf-8") as file:
        file.write(html)

    return output_path


def main() -> None:
    html = fetch_premiership_page()
    output_path = save_html(html)

    print(f"Saved HTML to: {output_path}")
    print(f"HTML length: {len(html)} characters")

    print("\nPreview:")
    print(html[:1000])


if __name__ == "__main__":
    main()
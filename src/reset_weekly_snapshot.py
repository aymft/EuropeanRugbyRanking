"""
Reset the weekly comparison snapshot.

This script copies the currently published ranking into
data/processed/previous_rankings.json.

After this reset, the next generate_rankings.py run will show:
- points_change = 0
- rank_change = 0

until new matches are added to matches_history.csv.
"""

import shutil
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

CURRENT_RANKINGS_PATH = ROOT_DIR / "docs" / "data" / "rankings.json"
PREVIOUS_RANKINGS_PATH = ROOT_DIR / "data" / "processed" / "previous_rankings.json"


def main() -> None:
    if not CURRENT_RANKINGS_PATH.exists():
        raise FileNotFoundError(f"Could not find {CURRENT_RANKINGS_PATH}")

    PREVIOUS_RANKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CURRENT_RANKINGS_PATH, PREVIOUS_RANKINGS_PATH)

    print(f"Copied {CURRENT_RANKINGS_PATH}")
    print(f"to     {PREVIOUS_RANKINGS_PATH}")
    print("Weekly comparison snapshot has been reset.")


if __name__ == "__main__":
    main()
import html
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from src.generate_rankings import get_matches_for_ranking
from src.matches import Match
from src.rugbyviz_feed import parse_rugbyviz_config
from src.scrapers.top14_scraper import (
    extract_current_week,
    extract_matches,
    get_match_kickoff_iso,
)
from src.team_registry import normalize_team_name
from src.update_latest_top14 import parse_finished_matches


ROOT_DIR = Path(__file__).resolve().parents[1]


def build_lnr_html(matches, *, include_current_week=False):
    week = {"id": 1848, "name": "J8", "slug": "j8", "number": 8}
    attributes = [
        f":weeks='{html.escape(json.dumps([week]), quote=True)}'",
        f":matches='{html.escape(json.dumps(matches), quote=True)}'",
    ]

    if include_current_week:
        attributes.append(
            f":current-week='{html.escape(json.dumps(week), quote=True)}'"
        )

    return f"<html><score-slider {' '.join(attributes)}></score-slider></html>"


class Top14ParserTests(unittest.TestCase):
    def setUp(self):
        self.finished_match = {
            "id": 11869,
            "week_id": 1848,
            "hosting_club": {"name": "Union Bordeaux-Bègles"},
            "visiting_club": {"name": "Aviron Bayonnais"},
            "date": "31/10",
            "time": "16h35",
            "status": "finished",
            "score": [31, 24],
            "timer": {"firstPeriodStartDate": "2026-10-31T16:35:00+01:00"},
            "link": "https://top14.lnr.fr/feuille-de-match/example",
        }

    def test_current_lnr_markup_is_parsed_and_normalized(self):
        raw_html = build_lnr_html([self.finished_match])

        self.assertEqual(extract_current_week(raw_html)["slug"], "j8")
        self.assertEqual(extract_matches(raw_html)[0]["id"], 11869)

        parsed = parse_finished_matches(raw_html)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["team_a_id"], "union-bordeaux-begles")
        self.assertEqual(parsed[0]["team_b_id"], "aviron-bayonnais")
        self.assertEqual(parsed[0]["score_a"], 31)
        self.assertEqual(parsed[0]["score_b"], 24)

    def test_current_week_attribute_remains_supported(self):
        raw_html = build_lnr_html(
            [self.finished_match],
            include_current_week=True,
        )
        self.assertEqual(extract_current_week(raw_html)["number"], 8)

    def test_kickoff_falls_back_to_display_date_and_season(self):
        match = dict(self.finished_match)
        match["timer"] = {}
        self.assertEqual(
            get_match_kickoff_iso(match),
            "2026-10-31T16:35:00+01:00",
        )

    def test_invalid_empty_match_payload_fails_loudly(self):
        raw_html = build_lnr_html([])
        with self.assertRaisesRegex(RuntimeError, "matches list is empty"):
            extract_matches(raw_html)


class Top14RegistryAndLogoTests(unittest.TestCase):
    SOURCE_NAMES = (
        "ASM Clermont",
        "Aviron Bayonnais",
        "Castres Olympique",
        "LOU Rugby",
        "Montpellier Hérault Rugby",
        "Racing 92",
        "RC Toulon",
        "RC Vannes",
        "Section Paloise",
        "Stade Français Paris",
        "Stade Rochelais",
        "Stade Toulousain",
        "Union Bordeaux-Bègles",
        "USA Perpignan",
    )

    def test_all_current_top14_names_have_registry_entries_and_logos(self):
        for source_name in self.SOURCE_NAMES:
            with self.subTest(source_name=source_name):
                club_id = normalize_team_name("lnr_top14", source_name)
                svg = ROOT_DIR / "docs" / "assets" / "img" / "clubs" / f"{club_id}.svg"
                png = ROOT_DIR / "docs" / "assets" / "img" / "clubs" / f"{club_id}.png"
                self.assertTrue(svg.is_file() or png.is_file(), club_id)


class RugbyVizConfigTests(unittest.TestCase):
    def test_public_match_feed_config_ignores_tracking_credentials(self):
        raw_html = """
        <script>
        window.__NUXT__.config={public:{
          tracking:{apiKey:"tracking",realmId:"epcr",appId:"web"},
          dataProvider:"rugbyviz",apiKey:"matches-key",realmId:"epcr",
          appId:"web",clientId:"EPCR"
        }}
        </script>
        """
        config = parse_rugbyviz_config(
            raw_html,
            "https://www.epcrugby.com/champions-cup/matches",
        )
        self.assertEqual(config.api_key, "matches-key")
        self.assertEqual(config.realm, "epcr")
        self.assertEqual(config.app_id, "web")
        self.assertEqual(config.origin, "https://www.epcrugby.com")


class RankingPropagationTests(unittest.TestCase):
    def test_history_top14_match_replaces_manual_top14_source(self):
        manual_top14 = Match(
            "Stade Toulousain",
            "Racing Métro 92",
            "home",
            30,
            10,
            "TOP14",
        )
        manual_urc = Match("Leinster", "Munster", "home", 20, 15, "URC")
        scraped_top14 = Match(
            "Stade Toulousain",
            "Racing Métro 92",
            "home",
            31,
            10,
            "TOP14",
        )

        with patch(
            "src.generate_rankings.get_all_matches",
            return_value=[manual_top14, manual_urc],
        ), patch(
            "src.generate_rankings.load_history_matches",
            return_value=[scraped_top14],
        ):
            matches = get_matches_for_ranking()

        self.assertEqual(matches, [manual_urc, scraped_top14])


if __name__ == "__main__":
    unittest.main()

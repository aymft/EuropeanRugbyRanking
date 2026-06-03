"""
Central club registry for European Rugby Ranking.

This registry separates:
- stable internal club IDs;
- display names used on the website;
- current Elo model names;
- domestic competitions;
- source-specific aliases.

The goal is to avoid fragile string matching when scraping data from
different official sources.
"""


CLUB_REGISTRY = {
    # =====================
    # TOP 14
    # =====================
    "union-bordeaux-begles": {
        "display_name": "Union Bordeaux-Bègles",
        "model_name": "Union Bordeaux Bègles",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Union Bordeaux-Bègles"],
            "thesportsdb": ["Union Bordeaux Bègles"],
        },
    },
    "stade-toulousain": {
        "display_name": "Stade Toulousain",
        "model_name": "Stade Toulousain",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Stade Toulousain"],
            "thesportsdb": ["Stade Toulousain"],
        },
    },
    "montpellier-herault-rugby": {
        "display_name": "Montpellier Hérault Rugby",
        "model_name": "Montpellier Hérault Rugby",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Montpellier Hérault Rugby"],
            "thesportsdb": ["Montpellier Hérault Rugby"],
        },
    },
    "stade-rochelais": {
        "display_name": "Stade Rochelais",
        "model_name": "Stade Rochelais",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Stade Rochelais"],
            "thesportsdb": ["Stade Rochelais"],
        },
    },
    "stade-francais-paris": {
        "display_name": "Stade Français Paris",
        "model_name": "Stade Français Paris",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Stade Français Paris"],
            "thesportsdb": ["Stade Français Paris"],
        },
    },
    "section-paloise": {
        "display_name": "Section Paloise",
        "model_name": "Section Paloise",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Section Paloise"],
            "thesportsdb": ["Section Paloise"],
        },
    },
    "rc-toulonnais": {
        "display_name": "RC Toulon",
        "model_name": "RC Toulonnais",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["RC Toulon"],
            "thesportsdb": ["RC Toulonnais"],
        },
    },
    "asm-clermont-auvergne": {
        "display_name": "ASM Clermont",
        "model_name": "ASM Clermont Auvergne",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["ASM Clermont"],
            "thesportsdb": ["ASM Clermont Auvergne"],
        },
    },
    "racing-metro-92": {
        "display_name": "Racing 92",
        "model_name": "Racing Métro 92",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Racing 92"],
            "thesportsdb": ["Racing Métro 92"],
        },
    },
    "castres-olympique": {
        "display_name": "Castres Olympique",
        "model_name": "Castres Olympique",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Castres Olympique"],
            "thesportsdb": ["Castres Olympique"],
        },
    },
    "lyon-ou": {
        "display_name": "LOU Rugby",
        "model_name": "Lyon OU",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["LOU Rugby"],
            "thesportsdb": ["Lyon OU"],
        },
    },
    "aviron-bayonnais": {
        "display_name": "Aviron Bayonnais",
        "model_name": "Aviron Bayonnais",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["Aviron Bayonnais"],
            "thesportsdb": ["Aviron Bayonnais"],
        },
    },
    "usa-perpignan": {
        "display_name": "USA Perpignan",
        "model_name": "USA Perpignan",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["USA Perpignan"],
            "thesportsdb": ["USA Perpignan"],
        },
    },
    "us-montauban": {
        "display_name": "US Montauban",
        "model_name": "US Montauban",
        "domestic_competition": "TOP14",
        "aliases": {
            "lnr_top14": ["US Montauban"],
            "thesportsdb": ["US Montauban"],
        },
    },

    # =====================
    # Premiership
    # =====================
    "northampton-saints": {
        "display_name": "Northampton Saints",
        "model_name": "Northampton Saints",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Northampton Saints"],
            "thesportsdb": ["Northampton Saints"],
        },
    },
    "bath-rugby": {
        "display_name": "Bath Rugby",
        "model_name": "Bath Rugby",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Bath Rugby"],
            "thesportsdb": ["Bath Rugby"],
        },
    },
    "leicester-tigers": {
        "display_name": "Leicester Tigers",
        "model_name": "Leicester Tigers",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Leicester Tigers"],
            "thesportsdb": ["Leicester Tigers"],
        },
    },
    "saracens": {
        "display_name": "Saracens",
        "model_name": "Saracens",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Saracens"],
            "thesportsdb": ["Saracens"],
        },
    },
    "exeter-chiefs": {
        "display_name": "Exeter Chiefs",
        "model_name": "Exeter Chiefs",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Exeter Chiefs"],
            "thesportsdb": ["Exeter Chiefs"],
        },
    },
    "bristol-bears": {
        "display_name": "Bristol Bears",
        "model_name": "Bristol Bears",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Bristol Bears"],
            "thesportsdb": ["Bristol Bears"],
        },
    },
    "sale-sharks": {
        "display_name": "Sale Sharks",
        "model_name": "Sale Sharks",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Sale Sharks"],
            "thesportsdb": ["Sale Sharks"],
        },
    },
    "harlequins": {
        "display_name": "Harlequins",
        "model_name": "Harlequins",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Harlequins"],
            "thesportsdb": ["Harlequins"],
        },
    },
    "gloucester": {
        "display_name": "Gloucester Rugby",
        "model_name": "Gloucester",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Gloucester Rugby"],
            "thesportsdb": ["Gloucester"],
        },
    },
    "newcastle-red-bulls": {
        "display_name": "Newcastle Red Bulls",
        "model_name": "Newcastle Red Bulls",
        "domestic_competition": "PREMIERSHIP",
        "aliases": {
            "premiership": ["Newcastle Red Bulls"],
            "thesportsdb": ["Newcastle Red Bulls"],
        },
    },

    # =====================
    # URC
    # =====================
    "leinster": {
        "display_name": "Leinster Rugby",
        "model_name": "Leinster",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Leinster Rugby"],
            "thesportsdb": ["Leinster"],
        },
    },
    "glasgow": {
        "display_name": "Glasgow Warriors",
        "model_name": "Glasgow",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Glasgow Warriors"],
            "thesportsdb": ["Glasgow"],
        },
    },
    "bulls": {
        "display_name": "Bulls",
        "model_name": "Bulls",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Vodacom Bulls"],
            "thesportsdb": ["Bulls"],
        },
    },
    "stormers": {
        "display_name": "Stormers",
        "model_name": "Stormers",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["DHL Stormers"],
            "thesportsdb": ["Stormers"],
        },
    },
    "munster": {
        "display_name": "Munster Rugby",
        "model_name": "Munster",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Munster Rugby"],
            "thesportsdb": ["Munster"],
        },
    },
    "ulster": {
        "display_name": "Ulster Rugby",
        "model_name": "Ulster",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Ulster Rugby"],
            "thesportsdb": ["Ulster"],
        },
    },
    "connacht": {
        "display_name": "Connacht Rugby",
        "model_name": "Connacht",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Connacht Rugby"],
            "thesportsdb": ["Connacht"],
        },
    },
    "the-sharks": {
        "display_name": "Sharks",
        "model_name": "The Sharks",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Hollywoodbets Sharks"],
            "thesportsdb": ["The Sharks"],
        },
    },
    "lions": {
        "display_name": "Lions",
        "model_name": "Lions",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Fidelity SecureDrive Lions"],
            "thesportsdb": ["Lions"],
        },
    },
    "benetton": {
        "display_name": "Benetton Rugby",
        "model_name": "Benetton",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Benetton Rugby"],
            "thesportsdb": ["Benetton"],
        },
    },
    "cardiff-rugby": {
        "display_name": "Cardiff Rugby",
        "model_name": "Cardiff Rugby",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Cardiff Rugby"],
            "thesportsdb": ["Cardiff Rugby"],
        },
    },
    "edinburgh": {
        "display_name": "Edinburgh Rugby",
        "model_name": "Edinburgh",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Edinburgh Rugby"],
            "thesportsdb": ["Edinburgh"],
        },
    },
    "scarlets": {
        "display_name": "Scarlets",
        "model_name": "Scarlets",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Scarlets"],
            "thesportsdb": ["Scarlets"],
        },
    },
    "ospreys": {
        "display_name": "Ospreys",
        "model_name": "Ospreys",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Ospreys"],
            "thesportsdb": ["Ospreys"],
        },
    },
    "dragons": {
        "display_name": "Dragons RFC",
        "model_name": "Dragons",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Dragons RFC"],
            "thesportsdb": ["Dragons"],
        },
    },
    "zebre": {
        "display_name": "Zebre Parma",
        "model_name": "Zebre",
        "domestic_competition": "URC",
        "aliases": {
            "urc": ["Zebre Parma"],
            "thesportsdb": ["Zebre"],
        },
    },

    # =====================
    # Invited / non-domestic EPCR teams
    # =====================
    "cheetahs": {
        "display_name": "Cheetahs",
        "model_name": "Cheetahs",
        "domestic_competition": "INVITED",
        "aliases": {
            "thesportsdb": ["Cheetahs"],
        },
    },
    "black-lion": {
        "display_name": "Black Lion",
        "model_name": "Black Lion",
        "domestic_competition": "INVITED",
        "aliases": {
            "thesportsdb": ["Black Lion"],
        },
    },
}


def build_alias_lookup() -> dict[str, dict[str, str]]:
    """
    Build a nested source -> raw name -> club_id lookup table.
    """

    lookup: dict[str, dict[str, str]] = {
        "elo_model": {},
    }

    for club_id, club_data in CLUB_REGISTRY.items():
        model_name = club_data["model_name"]

        if model_name in lookup["elo_model"]:
            raise ValueError(f"Duplicate Elo model name: {model_name}")

        lookup["elo_model"][model_name] = club_id

        for source, aliases in club_data["aliases"].items():
            lookup.setdefault(source, {})

            for alias in aliases:
                if alias in lookup[source]:
                    existing_club_id = lookup[source][alias]
                    raise ValueError(
                        f"Duplicate alias {alias!r} for source {source!r}: "
                        f"{existing_club_id!r} and {club_id!r}"
                    )

                lookup[source][alias] = club_id

    return lookup


SOURCE_ALIAS_LOOKUP = build_alias_lookup()


def normalize_team_name(source: str, raw_team_name: str) -> str:
    """
    Convert a raw team name from a given source into a stable club_id.

    Examples
    --------
    normalize_team_name("lnr_top14", "LOU Rugby") -> "lyon-ou"
    normalize_team_name("premiership", "Gloucester Rugby") -> "gloucester"
    normalize_team_name("urc", "Glasgow Warriors") -> "glasgow"
    """

    if source not in SOURCE_ALIAS_LOOKUP:
        raise ValueError(
            f"Unknown source: {source!r}. "
            f"Available sources: {sorted(SOURCE_ALIAS_LOOKUP)}"
        )

    source_lookup = SOURCE_ALIAS_LOOKUP[source]

    if raw_team_name not in source_lookup:
        raise ValueError(
            f"Unknown team name {raw_team_name!r} for source {source!r}. "
            "Add it to CLUB_REGISTRY aliases."
        )

    return source_lookup[raw_team_name]


def get_club_data(club_id: str) -> dict:
    """
    Return registry data for one club_id.
    """

    if club_id not in CLUB_REGISTRY:
        raise ValueError(f"Unknown club_id: {club_id!r}")

    return CLUB_REGISTRY[club_id]


def get_display_name(club_id: str) -> str:
    """
    Return the website display name for one club.
    """

    return get_club_data(club_id)["display_name"]


def get_model_name(club_id: str) -> str:
    """
    Return the current Elo model name for one club.
    """

    return get_club_data(club_id)["model_name"]


def get_domestic_competition(club_id: str) -> str:
    """
    Return the domestic competition associated with one club.
    """

    return get_club_data(club_id)["domestic_competition"]


def get_club_id_from_model_name(model_name: str) -> str:
    """
    Convert the current Elo model name into a stable club_id.
    """

    return normalize_team_name("elo_model", model_name)


def validate_registry_against_current_teams() -> None:
    """
    Check that every team currently used by the Elo model exists in the registry.
    """

    from src.teams import get_initial_teams

    model_team_names = set(get_initial_teams())
    registry_model_names = {
        club_data["model_name"]
        for club_data in CLUB_REGISTRY.values()
    }

    missing_from_registry = sorted(model_team_names - registry_model_names)
    extra_in_registry = sorted(registry_model_names - model_team_names)

    if missing_from_registry:
        raise ValueError(
            "Teams present in src/teams.py but missing from CLUB_REGISTRY: "
            f"{missing_from_registry}"
        )

    if extra_in_registry:
        raise ValueError(
            "Teams present in CLUB_REGISTRY but missing from src/teams.py: "
            f"{extra_in_registry}"
        )


def main() -> None:
    """
    Run registry validation and print a compact summary.
    """

    validate_registry_against_current_teams()

    print("Registry validation successful.")
    print(f"Number of clubs: {len(CLUB_REGISTRY)}")

    print("\nSample normalizations:")
    samples = [
        ("lnr_top14", "LOU Rugby"),
        ("lnr_top14", "RC Toulon"),
        ("premiership", "Gloucester Rugby"),
        ("urc", "Glasgow Warriors"),
        ("urc", "Hollywoodbets Sharks"),
        ("urc", "Zebre Parma"),
    ]

    for source, raw_name in samples:
        club_id = normalize_team_name(source, raw_name)
        print(f"{source:12s} | {raw_name:25s} -> {club_id}")


if __name__ == "__main__":
    main()
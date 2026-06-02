"""
Initial Elo ratings for European rugby clubs.

This file stores the starting ratings used before applying new match results.
"""


INITIAL_TEAMS_ELO = {
    "Union Bordeaux Bègles": 1789,
    "Stade Toulousain": 1752,
    "Leinster": 1709,
    "Northampton Saints": 1701,
    "Bath Rugby": 1693,
    "Montpellier Hérault Rugby": 1677,
    "Leicester Tigers": 1668,
    "Glasgow": 1658,
    "Bulls": 1625,
    "Stade Rochelais": 1574,
    "Stade Français Paris": 1565,
    "Saracens": 1565,
    "Stormers": 1561,
    "Section Paloise": 1557,
    "Exeter Chiefs": 1552,
    "RC Toulonnais": 1542,
    "ASM Clermont Auvergne": 1540,
    "Racing Métro 92": 1533,
    "Bristol Bears": 1531,
    "Munster": 1527,
    "Ulster": 1498,
    "Connacht": 1487,
    "Sale Sharks": 1479,
    "The Sharks": 1479,
    "Castres Olympique": 1478,
    "Harlequins": 1475,
    "Lions": 1462,
    "Benetton": 1453,
    "Cardiff Rugby": 1452,
    "Gloucester": 1442,
    "Lyon OU": 1440,
    "Aviron Bayonnais": 1431,
    "Edinburgh": 1430,
    "Scarlets": 1369,
    "Ospreys": 1366,
    "USA Perpignan": 1348,
    "Dragons": 1242,
    "Cheetahs": 1238,
    "Zebre": 1216,
    "Black Lion": 1211,
    "US Montauban": 1154,
    "Newcastle Red Bulls": 1144,
}


def get_initial_teams() -> dict[str, int]:
    """
    Return a copy of the initial Elo ratings.

    Returns
    -------
    dict[str, int]
        Dictionary where keys are team names and values are Elo ratings.
    """

    return INITIAL_TEAMS_ELO.copy()
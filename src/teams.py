"""
Initial Elo ratings for European rugby clubs.

This file stores the starting ratings used before applying new match results.
"""


INITIAL_TEAMS_ELO = {
    "Bordeaux-Begles": 1789,
    "Toulouse": 1752,
    "Leinster": 1709,
    "Northampton": 1701,
    "Bath": 1693,
    "Montpellier": 1677,
    "Leicester": 1668,
    "Glasgow": 1658,
    "Bulls": 1625,
    "La Rochelle": 1574,
    "Stade Francais": 1565,
    "Saracens": 1565,
    "Stormers": 1561,
    "Pau": 1557,
    "Exeter": 1552,
    "Toulon": 1542,
    "Clermont": 1540,
    "Racing 92": 1533,
    "Bristol": 1531,
    "Munster": 1527,
    "Ulster": 1498,
    "Connacht": 1487,
    "Sale": 1479,
    "Sharks": 1479,
    "Castres": 1478,
    "Harlequins": 1475,
    "Lions": 1462,
    "Trevise": 1453,
    "Cardiff": 1452,
    "Gloucester": 1442,
    "Lyon": 1440,
    "Bayonne": 1431,
    "Edimbourg": 1430,
    "Scarlets": 1369,
    "Ospreys": 1366,
    "Perpignan": 1348,
    "Dragons": 1242,
    "Cheetahs": 1238,
    "Zebre": 1216,
    "Black Lion": 1211,
    "Montauban": 1154,
    "Newcastle": 1144,
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
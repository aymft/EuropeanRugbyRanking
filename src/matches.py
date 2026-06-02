"""
Match data for European rugby competitions.

For now, matches are entered manually.
Later, this file will be replaced or completed by automatic match fetching.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    """
    Representation of a rugby match.

    Attributes
    ----------
    team_a : str
        First team, usually the home team.
    team_b : str
        Second team, usually the away team.
    location : str
        Match location from the perspective of team_a.
        Accepted values: "home", "away", "neutral".
    score_a : int
        Score of team_a.
    score_b : int
        Score of team_b.
    competition : str
        Competition name.
    """

    team_a: str
    team_b: str
    location: str
    score_a: int
    score_b: int
    competition: str


TOP14_MATCHES = [
    Match("Montauban", "La Rochelle", "home", 15, 71, "TOP14"),
    Match("Toulouse", "Lyon", "home", 39, 31, "TOP14"),
    Match("Perpignan", "Castres", "home", 29, 27, "TOP14"),
    Match("Stade Francais", "Bayonne", "home", 38, 21, "TOP14"),
    Match("Montpellier", "Pau", "home", 26, 18, "TOP14"),
    Match("Toulon", "Bordeaux-Begles", "home", 27, 22, "TOP14"),
    Match("Clermont", "Racing 92", "home", 13, 41, "TOP14"),
]


PREMIERSHIP_MATCHES = [
    Match("Bristol", "Bath", "home", 21, 19, "Premiership"),
    Match("Saracens", "Harlequins", "home", 26, 12, "Premiership"),
    Match("Northampton", "Gloucester", "home", 36, 32, "Premiership"),
    Match("Newcastle", "Sale", "home", 45, 42, "Premiership"),
    Match("Leicester", "Exeter", "home", 26, 35, "Premiership"),
]


URC_MATCHES = [
    Match("Glasgow", "Connacht", "home", 33, 21, "URC"),
    Match("Bulls", "Munster", "home", 45, 14, "URC"),
    Match("Stormers", "Cardiff", "home", 44, 21, "URC"),
    Match("Leinster", "Lions", "home", 59, 10, "URC"),
]


CHAMPIONS_CUP_MATCHES = []


CHALLENGE_CUP_MATCHES = []


def get_all_matches() -> list[Match]:
    """
    Return all matches in chronological processing order.

    Returns
    -------
    list[Match]
        List of all matches to process.
    """

    return (
        TOP14_MATCHES
        + PREMIERSHIP_MATCHES
        + URC_MATCHES
        + CHAMPIONS_CUP_MATCHES
        + CHALLENGE_CUP_MATCHES
    )
"""
Elo rating utilities for European rugby clubs.

This module contains the core Elo update rule used to update club ratings
after each match.
"""


EUROPEAN_COMPETITIONS = {"ChampionsCup", "ChallengeCup"}


def elo_update(
    team_elo: float,
    opponent_elo: float,
    location: str,
    score_a: int,
    score_b: int,
    competition: str,
    k_base: float = 25,
) -> tuple[int, int]:
    """
    Update the Elo ratings of two teams after one match.

    Parameters
    ----------
    team_elo : float
        Current Elo rating of team A.
    opponent_elo : float
        Current Elo rating of team B.
    location : str
        Location from the perspective of team A.
        Accepted values are "home", "away", or "neutral".
    score_a : int
        Score of team A.
    score_b : int
        Score of team B.
    competition : str
        Competition name, for example "TOP14", "Premiership",
        "URC", "ChampionsCup", or "ChallengeCup".
    k_base : float, optional
        Base K-factor controlling the strength of the update.

    Returns
    -------
    tuple[int, int]
        Updated Elo ratings for team A and team B.
    """

    score_a = int(score_a)
    score_b = int(score_b)

    # Match result from the perspective of team A
    if score_a > score_b:
        result = 1.0
    elif score_a < score_b:
        result = 0.0
    else:
        result = 0.5

    # Home advantage from the perspective of team A
    if location == "home":
        home_advantage = 60
    elif location == "away":
        home_advantage = -60
    elif location == "neutral":
        home_advantage = 0
    else:
        raise ValueError(
            f"Unknown location '{location}'. "
            "Expected 'home', 'away', or 'neutral'."
        )

    # Expected result for team A
    expected_result = 1 / (
        1 + 10 ** ((opponent_elo - team_elo - home_advantage) / 400)
    )

    # Margin of victory
    score_difference = abs(score_a - score_b)

    # Competition-dependent K-factor
    if competition in EUROPEAN_COMPETITIONS:
        k_factor = k_base * (1.8 if score_difference > 15 else 1.2)
    else:
        k_factor = k_base * (1.5 if score_difference > 15 else 1.0)

    # Elo update
    delta = k_factor * (result - expected_result)

    new_team_elo = round(team_elo + delta)
    new_opponent_elo = round(opponent_elo - delta)

    return new_team_elo, new_opponent_elo
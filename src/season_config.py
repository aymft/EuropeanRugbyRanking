"""Official source configuration for the active 2026-2027 season."""


SEASON_LABEL = "2026-2027"

# Ligue Nationale de Rugby (TOP 14)
TOP14_SEASON_ID = 14522
TOP14_RESULTS_URL = (
    "https://top14.lnr.fr/calendrier-et-resultats"
    f"?day=all&season={TOP14_SEASON_ID}"
)

# United Rugby Championship
URC_SEASON_ID = 202601
URC_GRAPHQL_URL = "https://www.unitedrugby.com/graphql"
URC_MATCH_CENTRE_URL = "https://stats.unitedrugby.com/match-centre/2026-27/R1"

# Gallagher PREM
PREMIERSHIP_SEASON_ID = 202601
PREMIERSHIP_COMPETITION_ID = 1011
PREMIERSHIP_FIXTURES_URL = (
    "https://www.premiershiprugby.com/content/"
    "202627-fixtures-and-club-tickets"
)
PREMIERSHIP_FEED_URL = (
    "https://rugby-union-feeds.incrowdsports.com/v1/matches"
    f"?compId={PREMIERSHIP_COMPETITION_ID}"
    f"&season={PREMIERSHIP_SEASON_ID}"
    "&provider=rugbyviz"
)

# European Professional Club Rugby
EPCR_SEASON_ID = 202601
EPCR_CHAMPIONS_CUP_COMPETITION_ID = 1008
EPCR_CHALLENGE_CUP_COMPETITION_ID = 1026
EPCR_CHAMPIONS_CUP_FIXTURES_URL = "https://www.epcrugby.com/champions-cup/matches"
EPCR_CHALLENGE_CUP_FIXTURES_URL = "https://www.epcrugby.com/challenge-cup/matches"
EPCR_CHAMPIONS_CUP_FEED_URL = (
    "https://rugby-union-feeds.incrowdsports.com/v1/matches"
    f"?compId={EPCR_CHAMPIONS_CUP_COMPETITION_ID}"
    f"&season={EPCR_SEASON_ID}"
    "&provider=rugbyviz"
)
EPCR_CHALLENGE_CUP_FEED_URL = (
    "https://rugby-union-feeds.incrowdsports.com/v1/matches"
    f"?compId={EPCR_CHALLENGE_CUP_COMPETITION_ID}"
    f"&season={EPCR_SEASON_ID}"
    "&provider=rugbyviz"
)

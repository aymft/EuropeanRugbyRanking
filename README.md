# European Rugby Ranking

European Rugby Ranking is a data-driven ranking system for European rugby clubs, based on an Elo rating model.

The project aims to provide a clear and regularly updated ranking of clubs from the main European rugby competitions, including:

- TOP 14
- Premiership Rugby
- United Rugby Championship
- European Champions Cup
- European Challenge Cup

The website is hosted with GitHub Pages:

https://aymft.github.io/EuropeanRugbyRanking/

## Project overview

The ranking is computed in Python and displayed through a static website built with HTML, CSS and JavaScript.

The current pipeline is:
- match results
- Elo computation
- rankings.csv / rankings.json
- dynamic ranking table on the website

The website displays:

- current Elo ranking
- club logos
- domestic league logos
- Elo point variation
- rank movement compared to the previous ranking


## Method

Each club starts with an initial Elo rating. After every match, the ratings of both teams are updated according to:

- the match result
- the Elo difference between the two teams
- home advantage
- score margin
- competition type

European competitions can use a different update factor from domestic competitions, allowing high-stakes cross-league matches to have a stronger impact on the ranking.

## Repository structure 

EuropeanRugbyRanking/
│
├── src/
│   ├── elo.py
│   ├── teams.py
│   ├── matches.py
│   ├── competitions.py
│   ├── generate_rankings.py
│   └── fetch_logos.py
│
├── data/
│   └── processed/
│       └── rankings.csv
│
├── docs/
│   ├── index.html
│   ├── data/
│   │   ├── rankings.csv
│   │   └── rankings.json
│   └── assets/
│       ├── css/
│       ├── js/
│       └── img/
│
└── README.md



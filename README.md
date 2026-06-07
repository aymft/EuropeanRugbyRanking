# European Rugby Ranking

A data-driven ranking system for European professional rugby clubs, based on an Elo-style model and updated automatically from official competition data sources.

The project aims to provide a simple and transparent way to follow the relative strength, form, and ranking dynamics of clubs competing across the main European rugby competitions.

Live website: https://aymft.github.io/EuropeanRugbyRanking/

---

## Overview

European Rugby Ranking is a personal project that ranks professional rugby clubs from:

* TOP 14
* Premiership Rugby
* United Rugby Championship
* Champions Cup
* Challenge Cup

The ranking is based on match results and updated through an automated pipeline. Each club has an Elo rating, a current rank, a previous rank, a ranking movement indicator, and an Elo points difference compared with the latest weekly reference snapshot.

The website is still under active development and will improve progressively over time.

---

## Main Features

* Elo-based ranking of European rugby clubs
* Club logos displayed next to team names
* Domestic league logos for TOP 14, Premiership and URC clubs
* Elo points difference after the latest update
* Rank movement indicators
* Automated result fetching
* Automated ranking generation
* GitHub Pages deployment
* Weekly reset of ranking movement and Elo difference indicators

---

## Ranking Method

The model uses an Elo-style system. Each team starts from a reference rating, then gains or loses points after each match depending on:

* the match result
* the opponent strength
* the competition
* the home/away context
* the score margin

The goal is not to reproduce an official ranking, but to provide a dynamic estimate of current club strength across domestic and European competitions.

The ranking is cumulative: previous results remain part of the Elo history. However, the displayed Elo difference and rank movement are computed relative to a weekly snapshot, so that users can clearly see which teams have moved since the latest update window.

---

## Automation

The ranking update is automated with GitHub Actions.

The update workflow runs every 10 minutes and performs the following steps:

1. Fetch latest TOP 14 results
2. Fetch latest URC results
3. Fetch latest Premiership results
4. Append new finished matches to the match history
5. Recompute Elo ratings
6. Update the website data files
7. Commit and push changes if the ranking has changed

A second workflow resets the weekly comparison snapshot after Tuesday, so that Elo differences and rank movements are cleared before the next weekend of matches.

---

## Data Sources

The project currently uses official or competition-related data feeds:

* TOP 14: official LNR website
* United Rugby Championship: official URC GraphQL endpoint
* Premiership Rugby: Incrowd / rugbyviz match feed used by the official Premiership Rugby website

Some European competition results may still rely on manually maintained or transitional sources while the full scraping pipeline is being improved.

---

## Project Structure

```text
EuropeanRugbyRanking/
├── data/
│   └── processed/
│       ├── matches_history.csv
│       ├── previous_rankings.json
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
├── src/
│   ├── generate_rankings.py
│   ├── update_latest_top14.py
│   ├── update_latest_urc.py
│   ├── update_latest_premiership.py
│   ├── reset_weekly_snapshot.py
│   ├── team_registry.py
│   └── scrapers/
│
└── .github/
    └── workflows/
        ├── update-rankings.yml
        └── reset-ranking-snapshot.yml
```

---

## Local Usage

Clone the repository:

```bash
git clone https://github.com/aymft/EuropeanRugbyRanking.git
cd EuropeanRugbyRanking
```

Run the update pipeline manually:

```bash
python -m src.update_latest_top14
python -m src.update_latest_urc
python -m src.update_latest_premiership
python -m src.generate_rankings
```

Serve the website locally:

```bash
python -m http.server 8000 --directory docs
```

Then open:

```text
http://localhost:8000
```

---

## Weekly Snapshot Logic

The Elo rating is cumulative, but the displayed movement indicators are relative to a weekly reference file:

```text
data/processed/previous_rankings.json
```

This file stores the ranking state before the next update cycle. The weekly reset copies the current ranking into this snapshot, which makes:

```text
points_change = 0
rank_change = 0
```

until new matches are added.

---

## Status

This project is under active development.

Current priorities include:

* improving the live results page
* extending the automated scraping pipeline
* refining competition weighting
* improving ranking explanations on the website
* adding more transparency about recent matches affecting each club

---

## Disclaimer

This is an independent personal project and is not affiliated with TOP 14, Premiership Rugby, United Rugby Championship, EPCR, or any rugby club.

All logos and competition names belong to their respective owners and are used for identification and informational purposes only.

---

## Author

Created by Aymeric Ferec.

GitHub: https://github.com/aymft
Website: https://aymft.github.io/EuropeanRugbyRanking/

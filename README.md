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

```text
match results
→ Elo computation
→ rankings.csv / rankings.json
→ dynamic ranking table on the website

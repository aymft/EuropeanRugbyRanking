import csv
import pandas as pd
import numpy as np

def calculate_points(team_points, opponent_points, location, score_a, score_b, competition):
    # Calculate D
    D = team_points - opponent_points + (3 if location == "home" else (0 if location == "neutral" else -3))
    D = max(min(D, 10), -10)

    # Calculate P
    if int(score_a) > int(score_b):
        P = 1 - D / 10
    elif int(score_a) < int(score_b):
        P = -(1 + D / 10)
    else:
        P = -D / 10

    # Calculate C

    if competition == "ChampionsCup" :
        if np.abs(int(score_a) - int(score_b)) <= 15:
            C = 1.5
        else:
            C = 2
    elif competition == "ChallengeCup" :
        if np.abs(int(score_a) - int(score_b)) <= 15:
            C = 1.5
        else:
            C = 2
    else:
        if np.abs(int(score_a) - int(score_b)) <= 15:
            C = 1
        else:
            C = 1.5



    # Calculate points
    points = C * P

    # Update the points of the teams
    team_points += points
    opponent_points -= points

    return team_points, opponent_points

teams = {
    # TOP14
   "Stade Francais": 82.48,
        "Toulon": 83.71,
        "Perpignan": 79.05,
        "Toulouse": 88.35,
        "Racing 92": 80.48,
        "La Rochelle": 84.20,
        "Bordeaux-Begles": 83.59,
        "Pau": 81.19,
        "Lyon": 84.34,
        "Montpellier": 80.53,
        "Castres": 81.72,
        "Bayonne": 78.97,
        "Clermont": 82.79,
        "Montauban": 76.60}

TOP14 = [        
        ("Montpellier","Toulouse","home",11,20),
        ("Clermont","Bayonne","home",26,10),
        ("Castres","Perpignan","home",27,12),
        ("Montauban","Lyon","home",30,20),
        ("La Rochelle","Pau","home",49,25),
        ("Bordeaux-Begles","Racing 92","home",52,34),
        ("Stade Francais","Toulon","home",10,14),
        ("Perpignan","Clermont","home",33,3),
        ("Lyon","Castres","home",40,38),
        ("Toulon","Montauban","home",54,19),
        ("Bayonne","Montpellier","home",28,27),
        ("Racing 92","La Rochelle","home",16,17),
        ("Pau","Stade Francais","home",30,16),
        ("Toulouse","Bordeaux-Begles","home",12,16), 
        ("Montauban", "Racing 92","home",24,27),
        ("Stade Francais","Montpellier","home",29,20),
        ("La Rochelle","Lyon","home",43,22),
        ("Bordeaux-Begles","Bayonne","home",30,27),
        ("Perpignan","Pau","home",11,10),
        ("Castres","Toulouse","home",28,23),
        ("Clermont","Toulon","home",19,18),
        ("Racing 92","Toulon","home",22,6),
        ("Montpellier","Montauban","home",26,24),
        ("Bordeaux-Begles","Perpignan","home",59,12),
        ("Bayonne","La Rochelle","home",30,7),
        ("Pau","Castres","home",33,26),
        ("Toulouse","Clermont","home",48,14),
        ("Lyon","Stade Francais","home",35,3),
        ("Bayonne","Racing 92","home",32,15),
        ("Clermont","Montauban","home",55,33),
        ("Castres","Stade Francais","home",35,13),
        ("Toulon","Montpellier","home",30,17),
        ("Perpignan","Lyon","home",29,26),
        ("La Rochelle","Bordeaux-Begles","home",32,22),
        ("Bordeaux-Begles", "Pau","home",19,6),
        ("Lyon","Bayonne","home",38,49),
        ("Montpellier","La Rochelle","home",16,0),
        ("Racing 92","Perpignan","home",30,23),
        ("Montauban","Castres","home",34,28),
        ("Stade Francais","Clermont","home",36,6),
        ("Toulouse","Toulon","home",57,5),
        ("Clermont","Bordeaux-Begles","home",32,27),
        ("Castres","Montpellier","home",30,26),
        ("Toulon","Lyon","home",21,10),
        ("Pau","Racing 92","home",22,33),
        ("Perpignan","Montauban","home",32,13),
        ("La Rochelle","Stade Francais","home",35,18),
        ("Bayonne","Toulouse","home",12,8),
        ("Toulon","Bayonne","home",39,19),
        ("Castres","La Rochelle","home",28,24),
        ("Montpellier","Pau","home",30,3),
        ("Toulouse","Perpignan","home",41,9),
        ("Lyon","Clermont","home",22,30),
        ("Montauban","Bordeaux-Begles","home",29,37),
        ("Stade Francais","Racing 92","home",40,26),
        ("Racing 92","Toulouse","home",17,21),
        ("Clermont","Castres","home",54,10),
        ("Pau","Lyon","home",29,15),
        ("La Rochelle","Montauban","home",14,23),
        ("Bordeaux-Begles","Montpellier","home",9,6),
        ("Perpignan","Toulon","home",13,22),
        ("Bayonne","Stade Francais","home",21,13),
        ("La Rochelle","Clermont","home",20,15),
        ("Montpellier","Racing 92","home",21,17),
        ("Toulon","Pau","home",56,25),
        ("Montauban","Bayonne","home",21,27),
        ("Stade Francais","Perpignan","home",24,7),
        ("Castres","Bordeaux-Begles","home",3,13),
        ("Lyon","Toulouse","home",17,17),
        ("Pau","Montauban","home",48,24),
        ("Bayonne","Castres","home",33,12),
        ("Clermont","Montpellier","home",18,22),
        ("Bordeaux-Begles","Toulon","home",8,0),
        ("Racing 92","Lyon","home",25,25),
        ("Perpignan","La Rochelle","home",21,13),
        ("Toulouse","Stade Francais","home",38,23),
        ("Toulon","Racing 92","home",36,24),
        ("Montpellier","Bayonne","home",42,10),
        ("Castres","Pau","home",24,17),
        ("Stade Francais","Bordeaux-Begles","home",19,46),
        ("Lyon","Perpignan","home",17,12),
        ("La Rochelle","Toulouse","home",22,19),
        ("Montauban","Clermont","home",19,20),
        ("Toulouse","Montpellier","home",27,17),
        ("Racing 92","Castres","home",20,27),
        ("Montauban","Stade Francais","home",33,28),
        ("Pau","Clermont","home",20,14),
        ("Perpignan","Bayonne","home",16,11),
        ("Bordeaux-Begles","Lyon","home",20,22),
        ("Bayonne","Bordeaux-Begles","home",36,32),
        ("Perpignan","Castres","home",20,20),
        ("Stade Francais","Pau","home",39,37),
        ("Racing 92","Montauban","home",25,30),
        ("Lyon","La Rochelle","home",53,17),
        ("Montpellier","Toulon","home",30,38),
        ("Clermont","Toulouse","home",18,35),
        ("Castres","Lyon","home",24,22),
        ("Toulon","Stade Francais","home",24,6),
        ("Pau","Perpignan","home",23,6),
        ("Montauban","Montpellier","home",37,24),
        ("La Rochelle","Racing 92","home",21,26),
        ("Stade Francais","La Rochelle","home",22,17),
        ("Montpellier","Castres","home",21,17),
        ("Toulouse","Montauban","home",63,21),
        ("Racing 92", "Pau","home",24,47),
        ("Lyon","Toulon","home",27,20),
        ("Perpignan","Bordeaux-Begles","home",17,29),
        ("Bayonne","Clermont","home",31,18),
        ("La Rochelle","Castres","home",12,12),
        ("Clermont","Racing 92","home",21,23),
        ("Pau","Montpellier","home",40,38),
        ("Lyon","Montauban","home",36,21),
        ("Stade Francais","Bayonne","home",31,27),
        ("Toulon","Perpignan","home",40,19),
        ("Bordeaux-Begles","Toulouse","home",32,24),
        ("Toulouse","Pau","home",55,10),
        ("Montauban","Perpignan","home",20,20),
        ("Bayonne","Lyon","home",28,14),
        ("Clermont","La Rochelle","home",33,19),
        ("Montpellier","Stade Francais","home",38,32),
        ("Castres","Toulon","home",28,26),
        ("Racing 92","Bordeaux-Begles","home",36,31),
        ("Pau","Bordeaux-Begles","home",22,26),
        ("Castres","Montauban","home",32,13),
        ("Lyon","Montpellier","home",32,23),
        ("La Rochelle","Bayonne","home",29,28),
        ("Perpignan","Racing 92","home",28,24),
        ("Toulon","Clermont","home",31,24),

        ("Stade Francais","Montauban","home",47,24),
        ("Perpignan","Bayonne","home",19,26),
        ("Lyon","Racing 92","home",32,7),
        ("Castres","Pau","home",15,17),
        ("Montpellier","Toulon","home",17,27),
        ("Bordeaux-Begles","La Rochelle","home",23,18),
        ("Clermont","Toulouse","home",24,34),
        ("Montauban","Lyon","home",18,25),
("Bayonne","Montpellier","home",26,23),
("Pau","Stade Francais","home",34,10),
("La Rochelle","Clermont","home",34,16),
("Toulouse","Perpignan","home",31,13),
("Toulon","Castres","home",16,12),
("Racing 92","Bordeaux-Begles","home",44,32),
("Clermont","Pau","home",50,27),
("Castres","Bayonne","home",48,17),
("Perpignan","Racing 92","home",15,28),
("Lyon","Stade Francais","home",42,37),
("Bordeaux-Begles","Montauban","home",71,24),
("Montpellier","Toulouse","home",44,14),
("Stade Francais","Bordeaux-Begles","home",28,7),
("Racing 92","Clermont","home",43,31),
("Montauban","Montpellier","home",22,22),
("Pau","Lyon","home",40,15),
("La Rochelle","Perpignan","home",31,8),
("Toulouse","Castres","home",59,12),
("Bayonne","Toulon","home",35,32),
("Montpellier","La Rochelle","home",37,13),
("Toulon","Pau","home",33,17),
("Perpignan","Stade Francais","home",11,28),
("Castres","Racing 92","home",20,16),
("Clermont","Montauban","home",84,31),
("Bordeaux-Begles","Lyon","home",32,20),
("Bayonne","Toulouse","home",40,26),

("Pau","Bayonne","home",47,24),
("Racing 92","Montpellier","home",32,25),
("Montauban","Castres","home",28,32),
("Stade Francais","La Rochelle","home",26,24),
("Lyon","Perpignan","home",44,19),
("Clermont","Toulon","home",27,10),
("Toulouse","Bordeaux-Begles","home",56,13),

("Bayonne","Clermont","home",44,17),
("La Rochelle","Montauban","home",54,19),
("Montpellier","Lyon","home",35,13),
("Perpignan","Bordeaux-Begles","home",12,27),
("Castres","Stade Francais","home",29,24),
("Pau",'Toulouse',"home",30,26),
("Toulon","Racing 92","home",45,21),

("Lyon","La Rochelle","home",19,36),
("Clermont","Castres","home",63,14),
("Racing 92","Pau","home",15,10),
("Stade Francais","Montpellier","home",35,12),
("Montauban","Perpignan","home",29,22),
("Bordeaux-Begles","Bayonne","home",41,12),
("Toulouse","Toulon","home",59,24),

("Toulon","Lyon","home",35,9),
("Montpellier","Clermont","home",7,9),
("Pau","Perpignan","home",27,23),
("Bayonne","Montauban","home",49,7),
("Castres","Bordeaux-Begles","home",26,28),
("Toulouse","Stade Francais","home",29,17),
("La Rochelle","Racing 92","home",33,6),

("Toulon","La Rochelle","home",39,14),

("Bordeaux-Begles","Pau","home",33,34),
("Lyon","Clermont","home",43,24),
("La Rochelle","Castres","home",17,19),
("Racing 92","Bayonne","home",47,27),
("Perpignan","Montpellier","home",0,28),
("Montauban","Toulouse","home",7,49),
("Stade Francais","Toulon","home",51,24),

("Montpellier","Bordeaux-Begles","home",28,24),
("Clermont","Stade Francais","home",36,32),
("Bayonne","Lyon","home",22,20),
("Toulon","Montauban","home",54,28),
("Castres","Perpignan","home",23,7),
("Toulouse","Racing 92","home",48,24),
("Pau","La Rochelle","home",53,33),

("Stade Francais","Racing 92","home",20,20),
("Montpellier","Castres","home",33,31),
("Montauban","Pau","home",17,53),
("La Rochelle","Bayonne","home",49,17),
("Perpignan","Clermont","home",26,20),
("Lyon","Toulouse","home",19,41),
("Bordeaux-Begles","Toulon","home",46,7),

("Racing 92","Montauban","home",61,14),
("Castres","Lyon","home",36,22),
("Bayonne","Stade Francais","home",35,34),
("Clermont","Bordeaux-Begles","home",34,19),
("Pau","Montpellier","home",35,33),
("Toulon","Perpignan","home",31,16),
("Toulouse","La Rochelle","home",60,14),

("Perpignan","Toulouse","home",30,27),
("Stade Francais","Castres","home",33,15),
("Montauban","Clermont","home",19,34),
("Lyon","Pau","home",22,17),
("Montpellier","Bayonne","home",62,22),
("Bordeaux-Begles","Racing 92","home",62,20),
("La Rochelle","Toulon","home",66,0),

("Bordeaux-Begles","Stade Francais","home",28,33),
("Perpignan","Montauban","home",31,8),
("Racing 92","Lyon","home",35,34),
("Bayonne","Castres","home",10,13),
("Toulouse","Pau","home",59,22),
("Toulon","Montpellier","home",30,27),
("Clermont","La Rochelle","home",32,27),

("Montpellier","Stade Francais","home",44,7),
("Montauban","Bordeaux-Begles","home",16,31),
("Castres","Clermont","home",28,23),
("La Rochelle","Lyon","home",24,44),
("Racing 92","Perpignan","home",37,31),
("Toulouse","Bayonne","home",31,10),
("Pau","Toulon","home",32,12),

("Bordeaux-Begles","Castres","home",57,23),
("La Rochelle","Montpellier","home",33,43),
("Bayonne","Racing 92","home",36,41),
("Lyon","Montauban","home",73,12),
("Toulon","Clermont","home",14,34),
("Stade Francais","Toulouse","home",9,13),
("Perpignan","Pau","home",40,24),

("Clermont","Bayonne","home",38,15),
("Toulouse","Montauban","home",68,13),
("Montpellier","Racing 92","home",41,17),
("Stade Francais","Perpignan","home",42,21),
("Lyon","Toulon","home",13,13),
("Castres","La Rochelle","home",26,31),
("Pau","Bordeaux-Begles","home",39,17),

("Clermont","Montpellier","home",17,20),
("Montauban","Bayonne","home",26,60),
("Racing 92","Castres","home",52,21),
("Perpignan","Lyon","home",28,32),
("Toulon","Stade Francais","home",27,46),
("La Rochelle","Pau","home",20,6),
("Bordeaux-Begles","Toulouse","home",44,20),

("Toulouse","Montpellier","home",45,29),
("Pau","Racing 92","home",27,17),
("Lyon","Bordeaux-Begles","home",17,21),
("Perpignan","Toulon","home",36,20),
("Castres","Montauban","home",49,17),
("Bayonne","La Rochelle","home",26,15),
("Stade Francais","Clermont","home",64,20),

("La Rochelle","Bordeaux-Begles","home",45,15),
("Clermont","Lyon","home",41,23),
("Bayonne","Pau","home",22,54),
("Montpellier","Perpignan","home",42,31),
("Montauban","Toulon","home",22,47),
("Castres","Toulouse","home",25,42),
("Racing 92","Stade Francais","home",47,20),

("Stade Francais","Pau","home",34,32),
("Perpignan","La Rochelle","home",29,31),
("Lyon","Castres","home",26,21),
("Montauban","Racing 92","home",10,59),
("Toulon","Bayonne","home",52,26),
("Bordeaux-Begles","Montpellier","home",21,23),
("Toulouse","Clermont","home",24,27),

("Pau","Castres","home",27,15),
("Montpellier","Montauban","home",59,7),
("Stade Francais","Lyon","home",59,17),
("Bayonne","Bordeaux-Begles","home",38,40),
("Clermont","Perpignan","home",45,14),
("Toulon","Toulouse","home",27,51),
("Racing 92","La Rochelle","home",24,26),

("Pau","Clermont","home",24,19),
("Bordeaux-Begles","Perpignan","home",37,32),
("Castres","Montpellier","home",33,36),
("Montauban","Stade Francais","home",25,73),
("Lyon","Bayonne","home",42,35),
("Racing 92","Toulon","home",43,28),
("La Rochelle","Toulouse","home",38,10),

("Montauban","La Rochelle","home",15,71),
("Toulouse","Lyon","home",39,31),
("Perpignan","Castres","home",29,27),
("Stade Francais","Bayonne","home",38,21),
("Montpellier","Pau","home",26,18),
("Toulon","Bordeaux-Begles","home",27,22),
("Clermont","Racing 92","home",13,41),

               ]

# Calculate the points for each match
for match in TOP14:
        team_a, team_b, location, score_a, score_b = match
        team_points, opponent_points = calculate_points(teams[team_a], teams[team_b], location, score_a, score_b, "TOP14")
        teams[team_a] = team_points
        teams[team_b] = opponent_points



    # Write the rankings to a CSV file
with open("TOP14.csv", "w", newline="") as csvfile:
        fieldnames = ["Team", "Points"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for team in sorted(teams, key=teams.get, reverse=True):
            writer.writerow({"Team": team, "Points": round(teams[team],2)})

df = pd.read_csv('TOP14.csv')
print(df)
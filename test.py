import json
import math

players = {}
games = {}
elo = {}
played = {}
umaoka = {
    1: 45000,
    2: 5000,
    3: -15000,
    4: -35000,
}

f = open('Users.json', 'r')
a = json.loads(f.read())
for p in a:
    uid = int(p['UserID'])
    players[uid] = p['Name']
    elo[uid] = 2000
    played[uid] = 0

f = open('Games.json', 'r')
a = json.loads(f.read())
for g in a:
    gid = g['GameID']
    uid = g['UserID']
    sc = g['Score']
    pl = g['Place']
    if gid not in games:
        games[gid] = {}
    games[gid][uid] = (pl,sc)
    

def volatility_coef(games_played):
    # makes the first PL games more volatile
    # eventually slowing down to multiplier M
    M = 1.3
    PL = 10
    res = M / (math.sqrt(games_played/PL))
    return max(M, res)
    

def countEloAdj(player_elo, avg_tbl_elo, place, abs_score):
    # expected place is  3 / (1 + math.pow(10, (TR-PR)/GR)) in [0-3]
    # where 
    # TR is Table Rating 
    # PR is Player Rating
    # GR is Growth Rate of Logistic function
    # lands between 0 - unlikely to win and 3 - guaranteed to win
    # we compare it to inverse of place to judge the performance
    GR = 400
    K = 23
    ex_place = 3 / (1 + math.pow(10, (avg_tbl_elo-player_elo)/GR))
    real_place = 4-place
    placement_adj = K * (real_place - ex_place)

    # score gives a flat elo multiplier
    SF = 0.0009
    score_adj = SF * (abs_score + umaoka[place])

    return placement_adj + score_adj

for g in games:
    game = games[g]
    #print('analysing ', game)
    
    # sum up elo for avg
    elo_sum = 0
    for player in game:
        elo_sum += elo[player]
    
    # adjust everyone's elo rating
    for player in game:
        played[player] += 1
        rank = game[player][0]
        score = game[player][1]-25000
        #print('player', player, ':elo=', elo[player], ', rank=', rank, ', score=', score, ', table_elo=', elo_sum/4)
        diff = countEloAdj(elo[player], elo_sum / 4, rank, score)
        float_adj = diff * volatility_coef(played[player])
        elo[player] += int(float_adj + 0.5)
        #print('elo_diff=', diff, 'volatility=', volatility_coef(played[player]), ' ,new_elo=', elo[player])

for p in dict(sorted(elo.items(), key=lambda item: item[1])):
    if played[p] != 0:
        print(players[p], elo[p])

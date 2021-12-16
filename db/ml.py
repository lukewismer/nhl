import numpy as np
from sklearn.linear_model import LinearRegression 
from sklearn.preprocessing import PolynomialFeatures
from pymongo import MongoClient
import os

try:
    conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

except:
    print("Could not connect to MongoDB")

db = conn['NHL']
collection = db['skaters']


def find_ml(player_id):
    results = find_career_trend(player_id)
    career_trend = {'career_trend': results}
    return career_trend

def find_career_trend(player_id):
    player = collection.find_one({'_id': player_id}, {'nhl_stats': 1})

    keys = ['goals', 'assists', 'shots', 'power_play_points']
    slopes = []
    for key in keys:
        c_avg, num_szn = findData(player, key)
    
        slopes.append(find_slope(c_avg, num_szn)[0])

    final_slope = sum(slopes)
    return final_slope

def find_slope(career_avg, num_szn):
    
    if career_avg:
        x = np.array(num_szn).reshape((-1, 1))
        y = np.array(career_avg)

        transformer = PolynomialFeatures(degree=2, include_bias=False)

        transformer.fit(x)

        model = LinearRegression().fit(x, y)

        return model.coef_
    else:
        return [0]

def findData(player, key):
    career_avg = []
    szn_counter = []
    szn_count = 0
    if len(player['nhl_stats']) >= 4:
        for szn in player['nhl_stats'][-4:]:
            career_avg.append(szn['stats'][key]/szn['stats']['games_played'])
            szn_counter.append(szn_count)
            szn_count += 1
    else:
        for szn in player['nhl_stats']:
            career_avg.append(szn['stats'][key]/szn['stats']['games_played'])
            szn_counter.append(szn_count)
            szn_count += 1
    return career_avg, szn_counter

find_ml()
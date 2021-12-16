from pymongo import MongoClient
import os

try:
    conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    print('Succesfull connection')

except:
    print("Could not connect to MongoDB")

db = conn['NHL']
collection_skaters = db['skaters']
collection_teams = db['teams']


def update_mongo_skaters(nhl_stats, info, home_away_splits, win_loss_splits, monthly_splits, divisional_splits, 
                                team_splits, game_log_splits, goals_by_game_situation_splits, on_pace_for_splits, machine_learning, player_id, player_data):
    player = collection_skaters.find_one({'_id': player_id})

    if player != None:
        keys = {'nhl_stats': nhl_stats, 'info': info, 'home_away_splits': home_away_splits, 'win_loss_splits': win_loss_splits, 'monthly_splits': monthly_splits,
        'divisional_splits': divisional_splits, 'team_splits': team_splits, 'game_log_splits': game_log_splits, 'goals_by_game_situation_splits': goals_by_game_situation_splits,
        'on_pace_for_splits': on_pace_for_splits, 'machine_learning': machine_learning}

        for count, (key,value) in enumerate(keys.items()):
            if key in player:
                if player[key] != value:
                    collection_skaters.update_one({"_id": player_id}, {"$set": {key: value}})
            else:
                collection_skaters.update_one({"_id": player_id}, {"$set": {key: value}})
    else:
        collection_skaters.insert_one(player_data)


def update_mongo_teams(team_id, team_data):
    team = collection_teams.find_one({'_id': team_id})

    if team != None:
        keys = {'info': team_data['info'], 'roster': team_data['roster'], 'stats': team_data['stats'],
                'schedule': team_data['schedule'], 'upcoming_game': team_data['upcoming_game']}

        for count, (key,value) in enumerate(keys.items()):
            if key in team:
                if team[key] != value:
                    collection_teams.update_one({"_id": team_id}, {"$set": {key: value}})
            else:
                collection_teams.update_one({"_id": team_id}, {"$set": {key: value}})
    else:
        collection_teams.insert_one(team_data)


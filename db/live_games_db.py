from games_db import fill_plays, fill_roster
from mongoDB import update_mongo_live_games
from pymongo import MongoClient
import requests
import time
    
def run():
        # Function to be threaded to update all Live Game Data
        db = connect_to_db()
        while True:
            # Infinite Loop Thread

            current_games_data = requests.get('https://statsapi.web.nhl.com/api/v1/schedule').json()
            # Api call to get all current games for today

            for game in current_games_data['dates'][0]['games']:
                # Loop through each game for current day
                if game['status']['detailedState'] != "Postponed":
                    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game["gamePk"]}/feed/live').json()

                    game_data = {
                        '_id': data['gamePk'],
                        'date': data['gameData']['datetime']['dateTime'],
                        'status': {
                            'state': data['gameData']['status']['detailedState']
                        },
                        'teams': {
                            'home': {
                                'id': data['gameData']['teams']['home']['id'],
                                'name': data['gameData']['teams']['home']['name'],
                                'abbreviation': data['gameData']['teams']['home']['abbreviation'],
                                'roster': {}, 
                                'team_stats': {
                                    'overall': {
                                        'goals': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals'],
                                        'shots': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['shots'],
                                        'pims': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['pim'],
                                        'hits': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['hits'],
                                        'power_play_percent': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['powerPlayPercentage'],
                                        'power_play_goals': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['powerPlayGoals'],
                                        'face_off_win_percent': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['faceOffWinPercentage']
                                    },
                                }
                            },
                            'away': {
                                'id': data['gameData']['teams']['away']['id'],
                                'name': data['gameData']['teams']['away']['name'],
                                'abbreviation': data['gameData']['teams']['away']['abbreviation'],
                                'roster': {}, 
                                'team_stats': {
                                    'overall': {
                                        'goals': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals'],
                                        'shots': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['shots'],
                                        'pims': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['pim'],
                                        'hits': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['hits'],
                                        'power_play_percent': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['powerPlayPercentage'],
                                        'power_play_goals': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['powerPlayGoals'],
                                        'face_off_win_percent': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['faceOffWinPercentage']
                                    },
                                }
                            }
                        }, 
                        'game_state': {
                            'current_period': data['liveData']['linescore']['currentPeriod'],
                            'period_time_remaining': "20:00",
                        },
                        'game_plays': {
                            'plays': []
                        },
                    }
                        

                    if "currentPeriodTimeRemaining" in data['liveData']['linescore'] and 'game_state' in game_data:
                        # If a period is in play, fill that time with respective dict key 
                        game_data['game_state']['period_time_remaining'] = data['liveData']['linescore']['currentPeriodTimeRemaining']

                    # Fill in roster/play data and then update it in mongodb database
                    fill_roster(game_data, data)
                    fill_plays(game_data, data)
                    update_mongo_live_games(game_data['_id'], game_data, db)
                    print("updated")
            
            # Pause the thread for 15 seconds   
            time.sleep(15)

def connect_to_db():
    # Connects to MongoDB
    try:
        #conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
        conn = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    except:
        print("Could not connect to MongoDB")
    
    return conn['NHL']['games']


run()
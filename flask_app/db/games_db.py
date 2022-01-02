import requests, time, threading, datetime
from mongoDB import update_mongo_games, update_mongo_live_games
from pymongo import MongoClient

def update_games():
    # Handles Game updates to DB
    update_all_games(connect_to_db())

def connect_to_db():
    # Connects to MongoDB
    try:
        #conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
        conn = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    except:
        print("Could not connect to MongoDB")

    return conn['NHL']['games']
    
def update_all_games(collection_games):
    # Updates all games into MongoDB database

    data_schedule = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?season=20212022').json()
    # API Call to get Schedule for 20212022 Season

    for date in data_schedule['dates']:
        # Loops through each Date
        
        for game in date['games']:
            # Loop through each game in each date

            game_data = {}
            data = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game["gamePk"]}/feed/live').json()
            # New request for respective game

            if data['gameData']['status']['detailedState'] != "Postponed":
                # If Game is not postponed fill out game_data dict

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
            
            else:
                # If game is postponed, fill game_data dict with limited info
                game_data = {
                    '_id': data['gamePk'],
                    'date': data['gameData']['datetime']['dateTime'],
                    'status': {
                        'code': data['gameData']['status']['statusCode'],
                        'state': data['gameData']['status']['detailedState']
                    },
                    'teams': {
                        'home': {
                            'id': data['gameData']['teams']['home']['id'],
                            'name': data['gameData']['teams']['home']['name'],
                            'abbreviation': data['gameData']['teams']['home']['abbreviation'],
                            'id': data['gameData']['teams']['home']['id'],
                            'roster': {}
                        },
                        'away': {
                            'id': data['gameData']['teams']['away']['id'],
                            'name': data['gameData']['teams']['away']['name'],
                            'abbreviation': data['gameData']['teams']['away']['abbreviation'],
                            'id': data['gameData']['teams']['away']['id'],
                            'roster': {},
                        }
                    }
                }
            
            if "currentPeriodTimeRemaining" in data['liveData']['linescore'] and 'game_state' in game_data:
                # If a period is in play, fill that time with respective dict key

                game_data['game_state']['period_time_remaining'] = data['liveData']['linescore']['currentPeriodTimeRemaining']

            # Fills Roster/Plays then updates game in DB
            fill_roster(game_data, data)
            fill_plays(game_data, data)
            update_mongo_games(game_data['_id'], game_data, collection_games)

def check_if_exists(data, key):
    # Checks if a key exists in data
    if key in data:
        return data[key]
    else:
        return 0

def fill_roster(game_data, data):
    # Fills the roster for each team from respective game

    sides = ['away', 'home']
    for side in sides:
        # Loops through twice for each side

        roster = []
        for count, (key, value) in enumerate(data['liveData']['boxscore']['teams'][side]['players'].items()):
            # Gets the keys from api (which are player ID's) to create individual dicts

            player = {
                'id': data['liveData']['boxscore']['teams'][side]['players'][key]['person']['id'],
                'name': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key]['person'], 'fullName'),
                'roster_status': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key]['person'], 'rosterStatus'),
                'position': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key]['position'], 'abbreviation'),
                'number': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key], 'jerseyNumber')
            }

            if 'skaterStats' in data['liveData']['boxscore']['teams'][side]['players'][key]['stats']:
                # Creates 'stats' dict for player if they have stats in respective game

                player['stats'] = {
                    'goals': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['goals'],
                    'assists': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['assists'],
                    'shots': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['shots'],
                    'hits': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['hits'],
                    'power_play_goals': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['powerPlayGoals'],
                    'power_play_assists': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['powerPlayAssists'],
                    'short_handed_goals': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['shortHandedGoals'],
                    'short_handed_assists': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['shortHandedAssists'],
                    'pims': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats'], 'penaltyMinutes'),
                    'blocks': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['blocked'],
                    'plus_minus': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['plusMinus'],
                    'face_off_wins': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['faceOffWins'],
                    'face_offs_taken': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['faceoffTaken'],
                    'face_off_percent': check_if_exists(data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats'], 'faceOffPct'),
                    'time_on_ice': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['timeOnIce'],
                    'power_play_time_on_ice': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['powerPlayTimeOnIce'],
                    'short_handed_time_on_ice': data['liveData']['boxscore']['teams'][side]['players'][key]['stats']['skaterStats']['shortHandedTimeOnIce'],
                }

            roster.append(player)

        game_data['teams'][side]['roster'] = roster

def fill_plays(game_data, data):
    # Fill all plays into game_data dict

    plays = []
    for play in data['liveData']['plays']['allPlays']:
        # Loops through all plays and creates individual dict

        current_play = {}
        current_play['name'] = play['result']['event']
        current_play['description'] = play['result']['description']
        current_play['id'] = play['about']['eventIdx']
        current_play['code'] = play['about']['eventId']
        current_play['time'] = {}
        current_play['time']['period'] = play['about']['period']
        current_play['time']['time_remaining'] = play['about']['periodTimeRemaining']
        current_play['current_score'] = {}
        current_play['current_score']['home'] = play['about']['goals']['home']
        current_play['current_score']['away'] = play['about']['goals']['away']
        current_play['result'] = {}
        current_play['players'] = []
        current_play['team'] = {}
        

        if 'players' in play:
            for player in play['players']:
                current_play['players'].append({
                    'id': player['player']['id'],
                    'name': player['player']['fullName'],
                    'type': player['playerType']
                }) 

        if 'team' in play:
            current_play['team']['id'] = play['team']['id']
            current_play['team']['name'] = play['team']['name']
            current_play['team']['abbreviation'] = play['team']['triCode']

        plays.append(play)

    if 'game_plays' in game_data:
        game_data['game_plays']['plays'] = plays

import requests, time, threading
from games_db import fill_plays, fill_roster
from mongoDB import update_mongo_live_games

class Update_Live_Games:
    # Class to control start and stop functionality for thread

    def __init__(self):
        self.running = True
      
    def terminate(self):
        # Stops thread
        self.running = False
      
    def run(self):
        # Function to be threaded to update all Live Game Data

        while self.running:
            # Infinite Loop Thread

            current_games_data = requests.get('https://statsapi.web.nhl.com/api/v1/schedule').json()
            # Api call to get all current games for today

            for game in current_games_data['dates'][0]['games']:
                # Loop through each game for current day

                data = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game["gamePk"]}/feed/live').json()

                game_data = {
                    '_id': data['gamePk'],
                    'date': data['gameData']['datetime']['dateTime'],
                    'status': {
                        'state': data['gameData']['status']['detailedState']
                    },
                    'teams': {}, 
                    'game_state': {
                        'current_period': data['liveData']['linescore']['currentPeriod'],
                        'period_time_remaining': "20:00",
                    },
                    'game_plays': {
                        'plays': []
                    },
                }

                for team in ['home', 'away']:
                    # Adds each team to the game data

                    game_data['teams'][team] = {
                        team: {
                            'id': data['gameData']['teams'][team]['id'],
                            'name': data['gameData']['teams'][team]['name'],
                            'abbreviation': data['gameData']['teams'][team]['abbreviation'],
                            'roster': {}, 
                            'team_stats': {
                                'overall': {
                                    'goals': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['goals'],
                                    'shots': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['shots'],
                                    'pims': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['pim'],
                                    'hits': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['hits'],
                                    'power_play_percent': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['powerPlayPercentage'],
                                    'power_play_goals': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['powerPlayGoals'],
                                    'face_off_win_percent': data['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']['faceOffWinPercentage']
                                },
                            }
                        }, 
                    }

                if "currentPeriodTimeRemaining" in data['liveData']['linescore'] and 'game_state' in game_data:
                    # If a period is in play, fill that time with respective dict key 
                    game_data['game_state']['period_time_remaining'] = data['liveData']['linescore']['currentPeriodTimeRemaining']

                # Fill in roster/play data and then update it in mongodb database
                fill_roster(game_data, data)
                fill_plays(game_data, data)
                update_mongo_live_games(game_data['_id'], game_data)
            
            # Pause the thread for 15 seconds
            time.sleep(15)

def update_live_games_thread():
    update_games = Update_Live_Games()
    thread = threading.Thread(target= update_games.run).start()


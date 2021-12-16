import requests

res = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?season=20212022')

data_schedule = res.json()
num = 0
for date in data_schedule['dates']:
    for game in date['games']:
        game_data = {}
        res = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game["gamePk"]}/feed/live')
        data = res.json()

        print(data['gamePk'])
        if data['gameData']['status']['detailedState'] != "Postponed":
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
                        'roster': {}, 
                        'team_stats': {
                            'overall': {
                                'goals': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals'],
                                'shots': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['shots'],
                                'pims': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['pim'],
                                'hits': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['hits'],
                                'blocks': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['blocked'],
                                'power_play_percent': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['powerPlayPercentage'],
                                'power_play_goals': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['powerPlayGoals'],
                                'power_play_opportunities': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['powerPlayOpportunities'],
                                'face_off_win_percent': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['faceOffWinPercentage'],
                                'takeaways': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['takeaways'],
                                'giveaways': data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['giveaways'],
                            }, 
                            'period_data': {},
                        }, 
                        'live_data' : {
                            'on_ice': data['liveData']['boxscore']['teams']['home']['onIce'],
                            'in_penalty_box': data['liveData']['boxscore']['teams']['home']['penaltyBox']
                        }
                    }, 
                    'away': {
                        'id': data['gameData']['teams']['away']['id'],
                        'name': data['gameData']['teams']['away']['name'],
                        'abbreviation': data['gameData']['teams']['away']['abbreviation'],
                        'id': data['gameData']['teams']['away']['id'],
                        'roster': {},
                        'team_stats': {
                            'overall': {
                                'goals': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals'],
                                'shots': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['shots'],
                                'pims': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['pim'],
                                'hits': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['hits'],
                                'blocks': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['blocked'],
                                'power_play_percent': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['powerPlayPercentage'],
                                'power_play_goals': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['powerPlayGoals'],
                                'power_play_opportunities': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['powerPlayOpportunities'],
                                'face_off_win_percent': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['faceOffWinPercentage'],
                                'takeaways': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['takeaways'],
                                'giveaways': data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['giveaways'],
                            }, 
                            'period_data': {},
                        }, 
                        'live_data' : {
                            'on_ice': data['liveData']['boxscore']['teams']['away']['onIce'],
                            'in_penalty_box': data['liveData']['boxscore']['teams']['away']['penaltyBox']
                        } 
                    }  
                }, 
                'game_state': {
                    'current_period': data['liveData']['linescore']['currentPeriod'],
                    'period_time_remaining': data['liveData']['linescore']['currentPeriod'],
                    'is_on_power_play': data['liveData']['linescore']['powerPlayStrength'],
                    'power_play_info': {}
                },
                'game_plays': {
                    'plays': [],
                    'scoring_plays': data['liveData']['plays']['scoringPlays'], 
                    'penalty_plays': data['liveData']['plays']['penaltyPlays'], 
                    'period_plays': {},
                    'current_play': {}
                },
            }
        num +=1 
        print(num)

    

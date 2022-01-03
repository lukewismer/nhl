import requests
from mongoDB import update_mongo_teams
from pymongo import MongoClient

def update_teams():
    collection_teams = connect_to_db()
    get_team_data(collection_teams)

def connect_to_db():
    # Connects to MongoDB
    try:
        #conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
        conn = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    except:
        print("Could not connect to MongoDB")

    return conn['NHL']['teams']

def get_team_ids():
    # Gets all team Ids and returns a list

    data = requests.get('https://statsapi.web.nhl.com/api/v1/teams').json()

    # Parse through each team and return list of Ids
    return [team['id'] for team in data['teams']]

def get_team_data(collection_teams):
    # Sends team data to mongoDB 

    for team_id in get_team_ids():
        data = {}
        data['_id'] = team_id
        data['info'] = get_team_info(team_id)
        data['roster'] = get_team_roster(team_id)
        data['stats'] = get_team_stats(team_id)
        data['schedule'] = get_team_schedule(team_id)
        data['upcoming_game'] = get_team_next_game(team_id)

        update_mongo_teams(team_id, data, collection_teams)

def get_team_info(team_id):
    # Returns team's info

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/').json()

    return  {
        'name': data['teams'][0]['name'],
        'abbreviation': data['teams'][0]['abbreviation'],
        'division': {
            'id': data['teams'][0]['division']['id'],
            'name': data['teams'][0]['division']['name']
        },
        'conference': {
            'id': data['teams'][0]['conference']['id'],
            'name': data['teams'][0]['conference']['name']
        }
    }

def get_team_roster(team_id):
    # Returns team roster (excludes goalies)

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/?expand=team.roster').json()

    roster = {}
    roster['roster'] = []

    for player in data['teams'][0]['roster']['roster']:

        if player['position']['name'] != 'Goalie':
            # Excludes Goalies

            roster['roster'].append(
                {
                    'id': player['person']['id'],
                    'name': player['person']['fullName'],
                    'position': player['position']['name']
                }
            )

    return roster

def get_team_stats(team_id):
    # Returns team stats

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/stats').json()

    stats_data = data['stats'][0]['splits'][0]['stat']

    return {
        'games_played': stats_data['gamesPlayed'],
        'wins': stats_data['wins'],
        'losses': stats_data['losses'],
        'ot_losses': stats_data['ot'],
        'points': stats_data['pts'],
        'point_percent': stats_data['ptPctg'],
        'goals_per_game': stats_data['goalsPerGame'],
        'goals_against_per_game': stats_data['goalsAgainstPerGame'],
        'power_play_percent': stats_data['powerPlayPercentage'],
        'power_play_goals': stats_data['powerPlayGoals'],
        'power_play_opportunities': stats_data['powerPlayOpportunities'],
        'penalty_kill_goals_against': stats_data['powerPlayGoalsAgainst'],
        'penalty_kill_percentage': stats_data['penaltyKillPercentage'],
        'shots_per_game': stats_data['shotsPerGame'],
        'shots_against_per_game': stats_data['shotsAllowed'],
        'shooting_percent': stats_data['shootingPctg'],
        'save_percent': stats_data['savePctg'],
        'face_offs_taken': stats_data['faceOffsTaken'],
        'face_offs_won': stats_data['faceOffsWon'],
        'face_offs_lost': stats_data['faceOffsLost'],
        'face_off_percentage': stats_data['faceOffWinPercentage'],
        'win_percents': {
            'win_score_first': stats_data['winScoreFirst'],
            'win_score_last': stats_data['winOppScoreFirst'],
            'win_lead_first_period': stats_data['winLeadFirstPer'],
            'win_lead_second_period': stats_data['winLeadSecondPer'],
            'win_outshoot_opponent': stats_data['winOutshootOpp'],
            'win_outshot_by_opponent': stats_data['winOutshotByOpp'],
        }
    }

def get_team_schedule(team_id):
    # Returns teams schedule for season

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?season=20212022&teamId={team_id}').json()

    schedule = {}
    schedule['schedule'] = []
    for game in data['dates']:
        game_data = {
            'id': game['games'][0]['gamePk'],
            'game_type': game['games'][0]['gameType'],
            'date': game['date'],
            'game_state': game['games'][0]['status']['detailedState'],
            'teams': {
                'home': {
                    'id': game['games'][0]['teams']['home']['team']['id'],
                    'name': game['games'][0]['teams']['home']['team']['name'],
                    'score': game['games'][0]['teams']['home']['score']
                },
                'away': {
                    'id': game['games'][0]['teams']['away']['team']['id'],
                    'name': game['games'][0]['teams']['away']['team']['name'],
                    'score': game['games'][0]['teams']['away']['score']
                }
            }
        }

        schedule['schedule'].append(game_data)
    
    return schedule

def get_team_next_game(team_id):
    # Returns the teams next game

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/?expand=team.schedule.next').json()

    game = data['teams'][0]['nextGameSchedule']['dates'][0]

    return {
        'id': game['games'][0]['gamePk'],
        'date': game['date'],
        'status_code': game['games'][0]['status']['statusCode'],
        'game_type': game['games'][0]['gameType'],
        'teams': {
            'home': {
                'id': game['games'][0]['teams']['home']['team']['id'],
                'name': game['games'][0]['teams']['home']['team']['name']
            },
            'away': {
                'id': game['games'][0]['teams']['away']['team']['id'],
                'name': game['games'][0]['teams']['away']['team']['name']
            }
        }
    }

import requests
from mongoDB import update_mongo_skaters
from pymongo import MongoClient

def update_players():
    player_ids = get_all_teams_rosters(get_team_ids())
    collection_skaters = connect_to_db()
    send_all_players_data(player_ids, collection_skaters)

def connect_to_db():
    # Connects to MongoDB
    try:
        #conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
        conn = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    except:
        print("Could not connect to MongoDB")

    return conn['NHL']['skaters']

def get_team_ids():
    # Gets all team Ids and returns a list
    data = requests.get('https://statsapi.web.nhl.com/api/v1/teams').json()

    # Parse through each team to get ID's
    return [team['id'] for team in data['teams']]
  
def get_all_teams_rosters(team_ids):
    # Returns a list of lists with all teams rosters

    return [get_team_roster(team_id) for team_id in team_ids]

def get_team_roster(id):
    # Takes a team ID and returns all skaters ids
    player_ids = []

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{str(id)}/?expand=team.roster').json()

    # Return a list of all the teams players ids
    for player in data['teams'][0]['roster']['roster']:
        if player['position']['code'] != "G":
            player_ids.append(player['person']['id'])
            
    return player_ids

def send_all_players_data(teams_player_ids, collection_skaters):
    # Handles getting all players data into a dict

    # Ordered Lists of stats categories used as parameters
    api_keys = ['goals', 'assists', 'points', 'penaltyMinutes', 'shots', 'hits', 'powerPlayGoals', 'powerPlayPoints', 'powerPlayTimeOnIce', 'evenTimeOnIce',
                'shortHandedTimeOnIce', 'shortHandedGoals', 'shortHandedPoints', 'gameWinningGoals', 'blocked', 'shotPct', 'plusMinus', 'shifts', 'games'] 

    dict_keys = ['goals', 'assists', 'points', 'pims', 'shots', 'hits', 'power_play_goals', 'power_play_points', 'power_play_toi', 'even_toi', 'short_handed_toi',
                    'short_handed_goals', 'short_handed_points', 'game_winning_goals', 'blocks', 'shot_percent', 'plus_minus', 'shifts', 'games_played']

    for team in teams_player_ids:
        for player_id in team:
            print(player_id)
            # API Call to retrieve player info
            info_data = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}').json()

            stats_data = get_stats_request('yearByYear', player_id)
            home_away_data = get_stats_request('homeAndAway', player_id)
            win_losses_data = get_stats_request('winLoss', player_id)
            monthly_data = get_stats_request('byMonth', player_id)
            division_data = get_stats_request('vsDivision', player_id)
            team_data = get_stats_request('vsTeam', player_id)
            game_log_data = get_stats_request('gameLog', player_id)
            goal_situation_data = get_stats_request('goalsByGameSituation', player_id)
            on_pace_data = get_stats_request('onPaceRegularSeason&season', player_id)

            player_data = {}

            # Gets all of our data for each player
            player_data['_id'] = get_player_info(info_data)['id']
            player_data['info'] = get_player_info(info_data)
            player_data['team'] = get_player_team_info(info_data)
            player_data['position'] = get_player_position(info_data)
            player_data['minor_leagues_stats'] = get_minor_hockey_stats(stats_data)
            player_data['nhl_stats'] = get_nhl_hockey_stats(stats_data, api_keys, dict_keys)
            player_data['home_away_splits'] = get_home_away_splits(home_away_data, api_keys, dict_keys)
            player_data['win_loss_splits'] = get_win_loss_splits(win_losses_data, api_keys, dict_keys)
            player_data['monthly_splits'] = get_monthly_splits(monthly_data, api_keys, dict_keys)
            player_data['divisional_splits'] = get_division_splits(division_data, api_keys, dict_keys)
            player_data['team_splits'] = get_team_splits(team_data, api_keys, dict_keys)
            player_data['game_log_splits'] = get_game_log_splits(game_log_data, api_keys, dict_keys)
            player_data['goals_by_game_situation_splits'] = get_goals_by_game_situation(goal_situation_data)
            player_data['on_pace_for_splits'] = get_on_pace_splits(on_pace_data, api_keys, dict_keys)\
            
            update_mongo_skaters(player_id, player_data, collection_skaters)
        
def get_player_info(data):
    # Gets an individual players info
    info = {}

    player_info = data['people'][0]

    info['id'] = player_info['id']
    info['name'] = player_info['fullName']
    info['date_of_birth'] = player_info['birthDate']
    info['birth_country'] = player_info['birthCountry']
    info['birth_city'] = check_string(player_info, 'birthCity')
    info['nationality'] = player_info['nationality']
    info['age'] = player_info['currentAge']
    info['height'] = player_info['height']
    info['weight'] = player_info['weight']
    info['active'] = player_info['active']
    info['captain'] = player_info['captain']
    info['assistant_captain'] = player_info['alternateCaptain']
    info['rookie'] = player_info['rookie']
    info['shoots_catches'] = player_info['shootsCatches']
    info['roster_status'] = player_info['rosterStatus']
    info['number'] = player_info['primaryNumber']

    return info

def get_player_team_info(data):
    # Returns the team dictionary for the individual player
    info = {}

    team_info = data['people'][0]['currentTeam']

    info['id'] = team_info['id']
    info['name'] = team_info['name']

    return info

def get_player_position(data):
    # Returns players position info
    info = {}

    position_data = data['people'][0]['primaryPosition']

    info['code'] = position_data['code']
    info['name'] = position_data['name']

    return info

def get_minor_hockey_stats(data):
    # Returns dict of minor hockey stats

    minor_stats = []

    seasons_data = data['stats'][0]['splits']

    for season in seasons_data:
        if season['league']['name'] != "National Hockey League":
            season_stats = {}
            season_stats['stats'] = {}
            season_stats['league'] = season['league']['name']
            season_stats['team_name'] = season['team']['name']
            season_stats['year'] = season['season']
            season_stats['stats'] = {}
            season_stats['stats']['goals'] = check_stats(season['stat'], 'goals')
            season_stats['stats']['assists'] = check_stats(season['stat'], 'assists')
            season_stats['stats']['points'] = check_stats(season['stat'], 'points')
            season_stats['stats']['games_played'] = check_stats(season['stat'], 'games')
        
            minor_stats.append(season_stats)

    return minor_stats

def get_nhl_hockey_stats(data, api_keys, dict_keys):
    # Retrieves all nhl stats for given player in formatted dict

    pro_stats = []

    seasons_data= data['stats'][0]['splits']

    for season in seasons_data:
        if season['league']['name'] == "National Hockey League":
            # Only NHL stats

            season_stats = {}
            season_stats['stats'] = {}

            season_stats['league'] = season['league']['name']
            season_stats['team_name'] = season['team']['name']
            season_stats['team_id'] = season['team']['id']
            season_stats['year'] = season['season']

            for index, item in enumerate(api_keys):
                # Creates new dict item with api data
                season_stats['stats'][dict_keys[index]] = check_stats(season['stat'], item)

            pro_stats.append(season_stats)

    return pro_stats

def get_home_away_splits(data, api_keys, dict_keys):
    # Returns a list for given players stats when home vs away

    final_data = []

    if data['stats'][0]['splits']: 
        for split in data['stats'][0]['splits']:
            temp_data = {}
            temp_data['stats'] = {}

            if split['isHome'] == True:
                # Creates filter to organize data
                temp_data['filter'] = 'Home'
            else:
                temp_data['filter'] = 'Away'

            for index, item in enumerate(api_keys):
                # Loops to add the correct split to the dict
                temp_data['stats'][dict_keys[index]] = check_stats(split['stat'], item)
    
            final_data.append(temp_data)

    return final_data
    
def get_win_loss_splits(data, api_keys, dict_keys):
    # Returns a list for given players stats when home vs away

    final_data = []

    if data['stats'][0]['splits']: 
        for split in data['stats'][0]['splits']:
            temp_data = {}
            temp_data['stats'] = {}
            # Check for each scenario
            if split['isWin'] == True and split['isOT'] == False:
                temp_data['filter'] = 'W'
            elif split['isWin'] == True and split['isOT'] == True:
                temp_data['filter'] = 'OTW'
            elif split['isWin'] == False and split['isOT'] == False:
                temp_data['filter'] = 'L'
            elif split['isWin'] == False and split['isOT'] == True:
                temp_data['filter'] = 'OTL'

            for index, item in enumerate(api_keys):
                temp_data['stats'][dict_keys[index]] = check_stats(split['stat'], item)
    
            final_data.append(temp_data)

    return final_data

def get_monthly_splits(data, api_keys, dict_keys):
    # Returns a list of given players stats in each month
    final_data = []

    if data['stats'][0]['splits']:
        for month in data['stats'][0]['splits']:
            month_data = {}
            month_data['stats'] = {}
            month_data['filter'] = month['month']
            for index, item in enumerate(api_keys):
                month_data['stats'][dict_keys[index]] = check_stats(month['stat'], item)
        
            final_data.append(month_data)

    return final_data

def get_division_splits(data, api_keys, dict_keys):
    # Returns a list of player stats vs each division
    final_data = []

    if data['stats'][0]['splits']:
        for division in data['stats'][0]['splits']:
            division_splits = {}
            division_splits['stats'] = {}
            division_splits['filter'] = division['opponentDivision']['name']
            division_splits['division_id'] = division['opponentDivision']['id']

            for index, item in enumerate(api_keys):
                division_splits['stats'][dict_keys[index]] = check_stats(division['stat'], item)
        
            final_data.append(division_splits)

    return final_data

def get_team_splits(data, api_keys, dict_keys):
    # Returns a list of player stats vs each division
    final_data = []

    if data['stats'][0]['splits']:
        for team in data['stats'][0]['splits']:
            team_data = {}
            team_data['stats'] = {}
            team_data['filter'] = team['opponent']['name']
            team_data['team_id'] = team['opponent']['id']

            for index, item in enumerate(api_keys):
                team_data['stats'][dict_keys[index]] = check_stats(team['stat'], item)
        
            final_data.append(team_data)

    return final_data

def get_game_log_splits(data, api_keys, dict_keys):
    # Returns a list of player stats vs each division
    final_data = []

    if data['stats'][0]['splits']:
        for game in data['stats'][0]['splits']:
            game_data = {}
            game_data['stats'] = {}
            game_data['filter'] = game['opponent']['name']
            game_data['date'] = game['date']
            game_data['opponent_id'] = game['opponent']['id']

            for index, item in enumerate(api_keys):
                game_data['stats'][dict_keys[index]] = check_stats(game['stat'], item)
        
            final_data.append(game_data)

    return final_data

def get_goals_by_game_situation(data):
    # Returns a dict with goals by game situations for each player
    situations = {}
    
    if data['stats'][0]['splits']:
        stats = data['stats'][0]['splits'][0]['stat']

        # List of all of the API keys to test
        api_key = ['goalsInFirstPeriod', 'goalsInSecondPeriod', 'goalsInThirdPeriod', 'goalsInOvertime', 'emptyNetGoals', 'goalsTrailingByOne', 'goalsTrailingByTwo',
                        'goalsTrailingByThreePlus', 'goalsWhenTied', 'goalsLeadingByOne', 'goalsLeadingByTwo', 'goalsLeadingByThreePlus']

        # Keys to use for my dict
        dict_key = ['goals_in_first_period', 'goals_in_second_period', 'goals_in_third_period', 'goals_in_overtime', 'empty_net_goals', 'goals_trailing_by_one', 'goals_trailing_by_two',
                    'goals_trailing_by_three_plus', 'goals_when_tied', 'goals_leading_by_one', 'goals_leading_by_two', 'goals_leading_by_three_plus']

        for index, check  in enumerate(api_key):
            # Sets the situation dict key = to the api data
            situations[dict_key[index]] = check_stats(stats, check)
        
    return situations

def get_on_pace_splits(data, api_keys, dict_keys):
    # Returns a list of player stats vs each division
    final_data = []

    if data['stats'][0]['splits']:
        for pace in data['stats'][0]['splits']:
            pace_data = {}
            pace_data['stats'] = {}

            for index, item in enumerate(api_keys):
                pace_data['stats'][dict_keys[index]] = check_stats(pace['stat'], item)
        
        final_data.append(pace_data)
        
    return final_data

def check_stats(stats, name):
    # Helper method to check that the stat exists
    if name in stats:
        return stats[name]
    else:
        return 0

def check_string(data, string):
    # Helper method to check that the string exists
    if string in data:
        return data[string]
    else:
        return ''

def get_stats_request(query, player_id):
    # Takes query and player_id and adds it to stats api call
    return  requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats={query}').json()


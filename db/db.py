from typing import final
import requests
#from webscraper import web_scrape_advanced_stats

YEAR = '20212022'


def main():
    player_ids = get_all_teams_rosters(get_team_ids())
    get_all_players_data(player_ids)

def get_team_ids():
    # Gets all team Ids and returns a list
    team_ids = []

    # API Call
    res = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
    data = res.json()

    # Parse through each team to get ID's
    for team in data['teams']:
        team_ids.append(team['id'])

    return team_ids
    
def get_all_teams_rosters(team_ids):
    # Returns a list of lists with all teams rosters
    rosters = []

    # Get roster from each team
    for team_id in team_ids:
        rosters.append(get_team_roster(team_id))

    return rosters

def get_team_roster(id):
    # Takes a team ID and returns all skaters ids
    player_ids = []
    
    #API Call
    res = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{str(id)}/?expand=team.roster')
    data = res.json()

    # Return a list of all the teams players ids
    for player in data['teams'][0]['roster']['roster']:
        if player['position']['code'] != "G":
            player_ids.append(player['person']['id'])

    return player_ids

def get_all_players_data(teams_player_ids):
    # Handles getting all players data into a dict

    for team in teams_player_ids:
        for player_id in team:
            print(player_id)
            # API Call to retrieve player info
            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}')
            info_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=yearByYear')
            stats_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=homeAndAway')
            home_away_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=winLoss&season')
            win_losses_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=byMonth')
            monthly_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=vsDivision')
            division_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=vsTeam')
            team_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats/?stats=gameLog')
            game_log_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=goalsByGameSituation')
            goal_situation_data = res.json()

            res = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=onPaceRegularSeason&season')
            on_pace_data = res.json()

            player_data = {}

            player_data['info'] = get_player_info(info_data)
            player_data['team'] = get_player_team_info(info_data)
            player_data['position'] = get_player_position(info_data)
            player_data['minor_leagues_stats'] = get_minor_hockey_stats(stats_data)
            player_data['nhl_stats'] = get_nhl_hockey_stats(stats_data)
            player_data['home_away_splits'] = get_home_away_splits(home_away_data)
            player_data['win_loss_splits'] = get_win_loss_splits(win_losses_data)
            player_data['monthly_splits'] = get_monthly_splits(monthly_data)
            player_data['divisional_splits'] = get_division_splits(division_data)
            player_data['team_splits'] = get_team_splits(team_data)
            player_data['game_log_splits'] = get_game_log_splits(game_log_data)
            player_data['goals_by_game_situation_splits'] = get_goals_by_game_situation(goal_situation_data)
            player_data['on_pace_for_splits'] = get_on_pace_splits(on_pace_data)
            #player_data['advanced_stats'] = web_scrape_advanced_stats(player_id)

            print(player_data)
        
def get_player_info(data):
    # Gets an individual players info
    info = {}

    player_info = data['people'][0]

    info['id'] = player_info['id']
    info['name'] = player_info['fullName']
    info['date_of_birth'] = player_info['birthDate']
    info['birth_country'] = player_info['birthCountry']
    if 'birthCity' in player_info:
        info['birth_city'] = player_info['birthCity']
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
            season_stats['league'] = season['league']['name']
            season_stats['team'] = season['team']['name']
            season_stats['year'] = season['season']
            season_stats['stats'] = {}
            season_stats['stats']['goals'] = check_stats(season['stat'], 'goals')
            season_stats['stats']['assists'] = check_stats(season['stat'], 'assists')
            season_stats['stats']['points'] = check_stats(season['stat'], 'points')
            season_stats['stats']['games_played'] = check_stats(season['stat'], 'games')
        
            minor_stats.append(season_stats)

    return minor_stats

def get_nhl_hockey_stats(data):
    # Retrieves all nhl stats for given player in formatted dict

    pro_stats = []

    seasons_data= data['stats'][0]['splits']

    for season in seasons_data:
        if season['league']['name'] == "National Hockey League":
            season_stats = {}

            season_stats['league'] = season['league']['name']
            season_stats['team_name'] = season['team']['name']
            season_stats['team_id'] = season['team']['id']
            season_stats['year'] = season['season']
            season_stats['stats'] = {}
            season_stats['stats']['goals'] = season['stat']['goals']
            season_stats['stats']['assists'] = season['stat']['assists']
            season_stats['stats']['points'] = season['stat']['points']
            season_stats['stats']['pims'] = season['stat']['pim']
            season_stats['stats']['shots'] = season['stat']['shots']
            season_stats['stats']['hits'] = season['stat']['hits']
            season_stats['stats']['power_play_goals'] = season['stat']['powerPlayGoals']
            season_stats['stats']['power_play_points'] = season['stat']['powerPlayPoints']
            season_stats['stats']['power_play_toi'] = season['stat']['powerPlayTimeOnIce']
            season_stats['stats']['even_toi'] = season['stat']['evenTimeOnIce']
            season_stats['stats']['short_handed_toi'] = season['stat']['shortHandedTimeOnIce']
            season_stats['stats']['short_handed_goals'] = season['stat']['shortHandedGoals']
            season_stats['stats']['short_handed_points'] = season['stat']['shortHandedPoints']
            season_stats['stats']['game_winning_goals'] = season['stat']['gameWinningGoals']
            season_stats['stats']['blocks'] = season['stat']['blocked']
            season_stats['stats']['shot_percent'] = season['stat']['shotPct']
            season_stats['stats']['face_off_percent'] = season['stat']['faceOffPct']
            season_stats['stats']['plus_minus'] = season['stat']['plusMinus']
            season_stats['stats']['shifts'] = season['stat']['shifts']
            season_stats['stats']['games_played'] = season['stat']['games']

            pro_stats.append(season_stats)

    return pro_stats

def get_home_away_splits(data):
    # Returns a list for given players stats when home vs away

    final_data = []

    home_data = {}
    away_data = {}

    if len(data['stats'][0]['splits']) == 2:

        home_parsed = data['stats'][0]['splits'][0]['stat']
        away_parsed = data['stats'][0]['splits'][1]['stat']

        home_data['home_away'] = 'home'
        home_data['goals'] = home_parsed['goals']
        home_data['assists'] = home_parsed['assists']
        home_data['points'] = home_parsed['points']
        home_data['pims'] = home_parsed['penaltyMinutes']
        home_data['shots'] = home_parsed['shots']
        home_data['hits'] = home_parsed['hits']
        home_data['power_play_goals'] = home_parsed['powerPlayGoals']
        home_data['power_play_points'] = home_parsed['powerPlayPoints']
        home_data['power_play_toi'] = home_parsed['powerPlayTimeOnIcePerGame']
        home_data['even_toi'] = home_parsed['evenTimeOnIcePerGame']
        home_data['short_handed_toi'] = home_parsed['shortHandedTimeOnIcePerGame']
        home_data['short_handed_goals'] = home_parsed['shortHandedGoals']
        home_data['short_handed_points'] = home_parsed['shortHandedPoints']
        home_data['game_winning_goals'] = home_parsed['gameWinningGoals']
        home_data['blocks'] = home_parsed['blocked']
        home_data['shot_percent'] = check_stats(home_parsed, 'shotPct')
        home_data['plus_minus'] = home_parsed['plusMinus']
        home_data['shifts'] = home_parsed['shifts']
        home_data['games_played'] = home_parsed['games']


        away_data['home_away'] = 'away'
        away_data['goals'] = away_parsed['goals']
        away_data['assists'] = away_parsed['assists']
        away_data['points'] = away_parsed['points']
        away_data['pims'] = away_parsed['penaltyMinutes']
        away_data['shots'] = away_parsed['shots']
        away_data['hits'] = away_parsed['hits']
        away_data['power_play_goals'] = away_parsed['powerPlayGoals']
        away_data['power_play_points'] = away_parsed['powerPlayPoints']
        away_data['power_play_toi'] = away_parsed['powerPlayTimeOnIcePerGame']
        away_data['even_toi'] = away_parsed['evenTimeOnIcePerGame']
        away_data['short_handed_toi'] = away_parsed['shortHandedTimeOnIcePerGame']
        away_data['short_handed_goals'] = away_parsed['shortHandedGoals']
        away_data['short_handed_points'] = away_parsed['shortHandedPoints']
        away_data['game_winning_goals'] = away_parsed['gameWinningGoals']
        away_data['blocks'] = away_parsed['blocked']
        away_data['shot_percent'] = check_stats(away_parsed, 'shotPct')
        away_data['plus_minus'] = away_parsed['plusMinus']
        away_data['shifts'] = away_parsed['shifts']
        away_data['games_played'] = away_parsed['games']

    final_data.append(home_data)
    final_data.append(away_data)

    return final_data
    
def get_win_loss_splits(data):
    # Returns a list for given players stats in wins vs losses

    final_data = []

    win_data = {}
    loss_data = {}

    if len(data['stats'][0]['splits']) == 2:

        win_parsed = data['stats'][0]['splits'][0]['stat']
        loss_parsed = data['stats'][0]['splits'][1]['stat']

        win_data['win_loss'] = 'win'
        win_data['goals'] = win_parsed['goals']
        win_data['assists'] = win_parsed['assists']
        win_data['points'] = win_parsed['points']
        win_data['pims'] = win_parsed['penaltyMinutes']
        win_data['shots'] = win_parsed['shots']
        win_data['hits'] = win_parsed['hits']
        win_data['power_play_goals'] = win_parsed['powerPlayGoals']
        win_data['power_play_points'] = win_parsed['powerPlayPoints']
        win_data['power_play_toi'] = win_parsed['powerPlayTimeOnIcePerGame']
        win_data['even_toi'] = win_parsed['evenTimeOnIcePerGame']
        win_data['short_handed_toi'] = win_parsed['shortHandedTimeOnIcePerGame']
        win_data['short_handed_goals'] = win_parsed['shortHandedGoals']
        win_data['short_handed_points'] = win_parsed['shortHandedPoints']
        win_data['game_winning_goals'] = win_parsed['gameWinningGoals']
        win_data['blocks'] = win_parsed['blocked']
        win_data['shot_percent'] = check_stats(win_parsed, 'shotPct')
        win_data['plus_minus'] = win_parsed['plusMinus']
        win_data['shifts'] = win_parsed['shifts']
        win_data['games_played'] = win_parsed['games']

        loss_data['win_loss'] = 'loss'
        loss_data['goals'] = loss_parsed['goals']
        loss_data['assists'] = loss_parsed['assists']
        loss_data['points'] = loss_parsed['points']
        loss_data['pims'] = loss_parsed['penaltyMinutes']
        loss_data['shots'] = loss_parsed['shots']
        loss_data['hits'] = loss_parsed['hits']
        loss_data['power_play_goals'] = loss_parsed['powerPlayGoals']
        loss_data['power_play_points'] = loss_parsed['powerPlayPoints']
        loss_data['power_play_toi'] = loss_parsed['powerPlayTimeOnIcePerGame']
        loss_data['even_toi'] = loss_parsed['evenTimeOnIcePerGame']
        loss_data['short_handed_toi'] = loss_parsed['shortHandedTimeOnIcePerGame']
        loss_data['short_handed_goals'] = loss_parsed['shortHandedGoals']
        loss_data['short_handed_points'] = loss_parsed['shortHandedPoints']
        loss_data['game_winning_goals'] = loss_parsed['gameWinningGoals']
        loss_data['blocks'] = loss_parsed['blocked']
        loss_data['shot_percent'] = check_stats(loss_parsed, 'shotPct')
        loss_data['plus_minus'] = loss_parsed['plusMinus']
        loss_data['shifts'] = loss_parsed['shifts']
        loss_data['games_played'] = loss_parsed['games']

    final_data.append(win_data)
    final_data.append(loss_data)

    return final_data

def get_monthly_splits(data):
    # Returns a list of given players stats in each month

    final_data = []
    for month in data['stats'][0]['splits']:
        if month:
            monthly_splits = {}
            monthly_splits['month'] = month['month']
            monthly_splits['goals'] = month['stat']['goals']
            monthly_splits['assists'] = month['stat']['assists']
            monthly_splits['points'] = month['stat']['points']
            monthly_splits['pims'] = month['stat']['penaltyMinutes']
            monthly_splits['shots'] = month['stat']['shots']
            monthly_splits['hits'] = month['stat']['hits']
            monthly_splits['power_play_goals'] = month['stat']['powerPlayGoals']
            monthly_splits['power_play_points'] = month['stat']['powerPlayPoints']
            monthly_splits['power_play_toi'] = check_stats(month['stat'], 'powerPlayTimeOnIcePerGame')
            monthly_splits['even_toi'] = month['stat']['evenTimeOnIcePerGame']
            monthly_splits['short_handed_toi'] = check_stats(month['stat'], 'shortHandedTimeOnIcePerGame')
            monthly_splits['short_handed_goals'] = month['stat']['shortHandedGoals']
            monthly_splits['short_handed_points'] = month['stat']['shortHandedPoints']
            monthly_splits['game_winning_goals'] = month['stat']['gameWinningGoals']
            monthly_splits['blocks'] = month['stat']['blocked']
            monthly_splits['shot_percent'] = check_stats(month['stat'], 'shotPct')
            monthly_splits['plus_minus'] = month['stat']['plusMinus']
            monthly_splits['shifts'] = month['stat']['shifts']
            monthly_splits['games_played'] = month['stat']['games']

            final_data.append(monthly_splits)

    return final_data

def get_division_splits(data):
    # Returns a list of player stats vs each division

    final_data = []

    division_splits_data = data['stats'][0]['splits']

    if len(division_splits_data) > 0:
        for division in division_splits_data:
            division_splits = {}

            division_splits['division_name'] = division['opponentDivision']['name']
            division_splits['division_id'] = division['opponentDivision']['id']
            division_splits['goals'] = division['stat']['goals']
            division_splits['assists'] = division['stat']['assists']
            division_splits['points'] = division['stat']['points']
            division_splits['pims'] = division['stat']['penaltyMinutes']
            division_splits['shots'] = division['stat']['shots']
            division_splits['hits'] = division['stat']['hits']
            division_splits['power_play_goals'] = division['stat']['powerPlayGoals']
            division_splits['power_play_points'] = division['stat']['powerPlayPoints']
            division_splits['power_play_toi'] = division['stat']['powerPlayTimeOnIcePerGame']
            division_splits['even_toi'] = division['stat']['evenTimeOnIcePerGame']
            division_splits['short_handed_toi'] = division['stat']['shortHandedTimeOnIcePerGame']
            division_splits['short_handed_goals'] = division['stat']['shortHandedGoals']
            division_splits['short_handed_points'] = division['stat']['shortHandedPoints']
            division_splits['game_winning_goals'] = division['stat']['gameWinningGoals']
            division_splits['blocks'] = division['stat']['blocked']
            division_splits['shot_percent'] = check_stats(division['stat'], 'shotPct')
            division_splits['plus_minus'] = division['stat']['plusMinus']
            division_splits['shifts'] = division['stat']['shifts']
            division_splits['games_played'] = division['stat']['games']

            final_data.append(division_splits)
    
    return final_data

def get_team_splits(data):
    # Returns a list of players stats vs specfic teams 

    final_data = []

    for team in data['stats'][0]['splits']:
        team_data = {}
        
        team_data['opponent_name'] = team['opponent']['name']
        team_data['opponent_id'] = team['opponent']['id']
        team_data['goals'] = team['stat']['goals']
        team_data['assists'] = team['stat']['assists']
        team_data['points'] = team['stat']['points']
        team_data['pims'] = team['stat']['penaltyMinutes']
        team_data['shots'] = team['stat']['shots']
        team_data['hits'] = team['stat']['hits']
        team_data['power_play_goals'] = team['stat']['powerPlayGoals']
        team_data['power_play_points'] = team['stat']['powerPlayPoints']
        team_data['power_play_toi'] = team['stat']['powerPlayTimeOnIcePerGame']
        team_data['even_toi'] = team['stat']['evenTimeOnIcePerGame']
        team_data['short_handed_toi'] = team['stat']['shortHandedTimeOnIcePerGame']
        team_data['short_handed_goals'] = team['stat']['shortHandedGoals']
        team_data['short_handed_points'] = team['stat']['shortHandedPoints']
        team_data['game_winning_goals'] = team['stat']['gameWinningGoals']
        team_data['blocks'] = team['stat']['blocked']
        team_data['shot_percent'] = check_stats(team['stat'], 'shotPct')
        team_data['plus_minus'] = team['stat']['plusMinus']
        team_data['shifts'] = team['stat']['shifts']
        team_data['games_played'] = team['stat']['games']

        final_data.append(team_data)

    return final_data

def get_game_log_splits(data):
    # Returns a list of game log for given player
    final_data = []

    for game in data['stats'][0]['splits']:
        game_data = {}

        game_data['opponent_name'] = game['opponent']['name']
        game_data['opponent_id'] = game['opponent']['id']
        game_data['date'] = game['opponent']['name']
        game_data['game_id'] = game['game']['gamePk']
        game_data['win_lose'] = game['isWin']
        game_data['home_away'] = game['isHome']
        game_data['overtime'] = game['isOT']
        game_data['goals'] = game['stat']['goals']
        game_data['assists'] = game['stat']['assists']
        game_data['points'] = game['stat']['points']
        game_data['pims'] = game['stat']['penaltyMinutes']
        game_data['shots'] = game['stat']['shots']
        game_data['hits'] = game['stat']['hits']
        game_data['power_play_goals'] = game['stat']['powerPlayGoals']
        game_data['power_play_points'] = game['stat']['powerPlayPoints']
        game_data['power_play_toi'] = game['stat']['powerPlayTimeOnIce']
        game_data['even_toi'] = game['stat']['evenTimeOnIce']
        game_data['short_handed_toi'] = game['stat']['shortHandedTimeOnIce']
        game_data['short_handed_goals'] = game['stat']['shortHandedGoals']
        game_data['short_handed_points'] = game['stat']['shortHandedPoints']
        game_data['game_winning_goals'] = game['stat']['gameWinningGoals']
        game_data['blocks'] = game['stat']['blocked']
        game_data['shot_percent'] = check_stats(game['stat'], 'shotPct')
        game_data['plus_minus'] = game['stat']['plusMinus']
        game_data['shifts'] = game['stat']['shifts']
        game_data['games_played'] = game['stat']['games']

        final_data.append(game_data)

    return final_data

def get_goals_by_game_situation(data):
    # Returns a dict with goals by game situations for each player
    situations = {}

    
    if len(data['stats'][0]['splits']) > 0:
        stats = data['stats'][0]['splits'][0]['stat']

        # List of all of the API keys to test
        check_list = ['goalsInFirstPeriod', 'goalsInSecondPeriod', 'goalsInThirdPeriod', 'goalsInOvertime', 'emptyNetGoals', 'goalsTrailingByOne', 'goalsTrailingByTwo',
                        'goalsTrailingByThreePlus', 'goalsWhenTied', 'goalsLeadingByOne', 'goalsLeadingByTwo', 'goalsLeadingByThreePlus']

        # Keys to use for my dict
        dict_key = ['goals_in_first_period', 'goals_in_second_period', 'goals_in_third_period', 'goals_in_overtime', 'empty_net_goals', 'goals_trailing_by_one', 'goals_trailing_by_two',
                    'goals_trailing_by_three_plus', 'goals_when_tied', 'goals_leading_by_one', 'goals_leading_by_two', 'goals_leading_by_three_plus']

        for index, check  in enumerate(check_list):
            # Sets the situation dict key = to the api data
            situations[dict_key[index]] = check_stats(stats, check)
        
    return situations

def get_on_pace_splits(data):
    final = {}

    for on_pace_data in data['stats'][0]['splits']:
        if on_pace_data:

            final['goals'] = on_pace_data['stat']['goals']
            final['assists'] = on_pace_data['stat']['assists']
            final['points'] = on_pace_data['stat']['points']
            final['pims'] = on_pace_data['stat']['penaltyMinutes']
            final['shots'] = on_pace_data['stat']['shots']
            final['hits'] = on_pace_data['stat']['hits']
            final['power_play_goals'] = on_pace_data['stat']['powerPlayGoals']
            final['power_play_points'] = on_pace_data['stat']['powerPlayPoints']
            final['power_play_toi'] = on_pace_data['stat']['powerPlayTimeOnIcePerGame']
            final['even_toi'] = on_pace_data['stat']['evenTimeOnIcePerGame']
            final['short_handed_toi'] = check_stats(on_pace_data['stat'], 'shortHandedTimeOnIcePerGame')
            final['short_handed_goals'] = on_pace_data['stat']['shortHandedGoals']
            final['short_handed_points'] = on_pace_data['stat']['shortHandedPoints']
            final['game_winning_goals'] = on_pace_data['stat']['gameWinningGoals']
            final['blocks'] = on_pace_data['stat']['blocked']
            final['shot_percent'] = check_stats(on_pace_data['stat'], 'shotPct')
            final['plus_minus'] = on_pace_data['stat']['plusMinus']
            final['shifts'] = on_pace_data['stat']['shifts']
            final['games_played'] = on_pace_data['stat']['games']
    
    return final

def check_stats(stats, name):
    # helper method to check that the stat eists
    if name in stats:
        return stats[name]
    else:
        return 0


main()
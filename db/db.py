from typing import final
import requests
from webscraper import web_scrape_advanced_stats

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

            player_data = {}

            player_data['info'] = get_player_info(info_data)
            player_data['team'] = get_player_team_info(info_data)
            player_data['position'] = get_player_position(info_data)
            player_data['minor_leagues_stats'] = get_minor_hockey_stats(stats_data)
            player_data['nhl_stats'] = get_nhl_hockey_stats(stats_data)
            player_data['home_away_splits'] = get_home_away_splits(home_away_data)
            #player_data['advanced_stats'] = web_scrape_advanced_stats(player_id)
        
def get_player_info(data):
    # Gets an individual players info
    info = {}

    player_info = data['people'][0]

    info['dob'] = player_info['birthDate']
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
    info['rostered'] = player_info['rosterStatus']
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
            season_stats['stats']['goals'] = season['stat']['goals']
            season_stats['stats']['assists'] = season['stat']['assists']
            season_stats['stats']['points'] = season['stat']['points']
            if 'games' in season['stat']:
                season_stats['stats']['games_played'] = season['stat']['games']
        
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
            season_stats['year'] = season['season']
            season_stats['stats'] = {}
            season_stats['stats']['goals'] = season['stat']['goals']
            season_stats['stats']['assists'] = season['stat']['assists']
            season_stats['stats']['points'] = season['stat']['points']
            season_stats['stats']['pims'] = season['stat']['pim']
            season_stats['stats']['shots'] = season['stat']['shots']
            season_stats['stats']['hits'] = season['stat']['hits']
            season_stats['stats']['power_play_goals'] = season['stat']['powerPlayGoals']
            season_stats['stats']['power_player_points'] = season['stat']['powerPlayPoints']
            season_stats['stats']['power_player_toi'] = season['stat']['powerPlayTimeOnIce']
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
    
    final_data = {}

    home_data = {}
    away_data = {}

    if len(data['stats'][0]['splits']) == 2:

        home_parsed = data['stats'][0]['splits'][0]['stat']
        away_parsed = data['stats'][0]['splits'][1]['stat']

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
        if 'shotPct' in home_parsed:
            home_data['shot_percent'] = home_parsed['shotPct']
        else:
            home_data['shot_percent'] = 0
        home_data['plus_minus'] = home_parsed['plusMinus']
        home_data['shifts'] = home_parsed['shifts']
        home_data['games_played'] = home_parsed['games']

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
        if 'shotPct' in away_parsed:
            away_data['shot_percent'] = away_parsed['shotPct']
        else:
            away_data['shot_percent'] = 0
        away_data['plus_minus'] = away_parsed['plusMinus']
        away_data['shifts'] = away_parsed['shifts']
        away_data['games_played'] = away_parsed['games']

    final_data['home_data'] = home_data
    final_data['away_data'] = away_data
    


main()
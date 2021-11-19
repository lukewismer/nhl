import requests, json, bs4

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

            player_data = {}

            player_data['info'] = get_player_info(info_data)
            player_data['team'] = get_player_team_info(info_data)
            player_data['position'] = get_player_position(info_data)
            player_data['minor_leagues_stats'] = get_minor_hockey_stats(stats_data)
            player_data['nhl_stats'] = get_nhl_hockey_stats(stats_data)
        
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

main()
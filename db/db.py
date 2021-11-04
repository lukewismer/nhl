import requests, json, bs4

def main():
    player_ids = get_all_teams_rosters(get_team_ids())
    


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


main()
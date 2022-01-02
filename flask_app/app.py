from warnings import filters
from flask import Flask, render_template, request
from pymongo import MongoClient
from collections import deque
from pymongo.message import update
import requests

app = Flask(__name__, static_folder='static')

#mongodb_client = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
mongodb_client = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

db = mongodb_client['NHL']
skaters_collection = db['skaters']
teams_collection = db['teams']
games_collecion = db['games']

@app.route('/')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/skaters')
def stats():
    # Gets all players and sends data to html

    players = skaters_collection.find({ '$and': [{'nhl_stats': { '$exists': 'true', '$ne': [] }}, {'nhl_stats.year': {'$eq': '20212022'}} ] }, {'info': 1, 'nhl_stats': 1})
    return render_template('datatable.html', title="NHL Stat Leaders", players=players)

@app.route('/individual/<player_id>/')
def individual_skater(player_id):
    # Handles individual skater page data

    # Handles the filter for stats table if applicable 
    stat_filter = request.args.get('filter')
    filter_title = get_filter_title_players(stat_filter)

    for p in skaters_collection.find({"_id": int(player_id)}):
        # Querys the db to get the player data
        player_stats = p[str(stat_filter)]
        player = p
    
    labels,ppg,apg,gpg,spg,hpg,pp_pg = [], [], [], [], [], [], []
    data_keys = ['goals', 'assists', 'points', 'pims', 'power_play_points', 'plus_minus']

    for szn in player['nhl_stats']:
        # Handles rounded average stats
        labels.append(szn['year'])
        ppg.append(round(szn['stats']['points']/szn['stats']['games_played'],2))
        gpg.append(round(szn['stats']['goals']/szn['stats']['games_played'],2))
        apg.append(round(szn['stats']['assists']/szn['stats']['games_played'],2))
        spg.append(round(szn['stats']['shots']/szn['stats']['games_played'],2))
        hpg.append(round(szn['stats']['hits']/szn['stats']['games_played'],2))
        pp_pg.append(round(szn['stats']['power_play_points']/szn['stats']['games_played'],2))

    tg,ta,tp,tpim,tppp,tpm,szn_num = 0,0,0,0,0,0,0
    for szn in player['nhl_stats']:
        # Handles stat totals
        if szn['year'] != '20212022':
            szn_num += 1
            tg += szn['stats']['goals']
            ta += szn['stats']['assists']
            tp += szn['stats']['points']
            tpim += int(szn['stats']['pims'])
            tppp += szn['stats']['power_play_points']
            tpm += szn['stats']['plus_minus']

    career_average_values = [tg/szn_num, ta/szn_num, tp/szn_num, tpim/szn_num, tppp/szn_num, tpm/szn_num]

    gl_labels, gl_p_values = [], []
    for szn in player['game_log_splits']:
        # Handles Game Log Splits
        gl_labels = deque(gl_labels)
        gl_p_values = deque(gl_p_values)

        gl_labels.appendleft(f"{szn['filter']} ({szn['date']})")
        gl_p_values.appendleft(szn['stats']['points'])

        gl_labels = list(gl_labels)
        gl_p_values = list(gl_p_values)

    t_labels, t_p_values = [], []
    for szn in player['team_splits']:
        # Handles team split stats
        t_labels.append(szn['filter'])
        t_p_values.append(szn['stats']['points'])

    gs_labels, gs_g_values = [], []
    for count, (key, value) in enumerate(player['goals_by_game_situation_splits'].items()):
        # Handles game split stats
        gs_labels.append(key.replace("_", " "))
        gs_g_values.append(value)

    op_labels, op_values = [], []
    for count, (key, value) in enumerate(player['on_pace_for_splits'][0]['stats'].items()):
        # Handles stats vs each opponents
        if key in data_keys:
            op_labels.append(key.replace("_", " "))
            op_values.append(int(value))

    return render_template('individual_stats.html', player=player_stats, title=player['info']['name'], filter=stat_filter, 
                            filter_title=filter_title, player_id=player_id, player_info=player['info'],  ppg_values=ppg, gpg_values=gpg, apg_values=apg, spg_values=spg, hpg_values=hpg, 
                            pp_pg_values=pp_pg, labels=labels, t_labels=t_labels, t_p_values=t_p_values, gl_labels=gl_labels, gl_p_values=gl_p_values, gs_g_values=gs_g_values, gs_labels=gs_labels,
                            op_labels=op_labels, op_values=op_values, ca_values=career_average_values, player_team=player['team'])

@app.route('/stats-leaders')
def leaders():
    # Advanced MongoDB Queries to get top 5 leaders in each category

    goal_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.goals', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])
    
    assist_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.assists', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    point_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.points', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    shots_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.shots', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    hits_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.hits', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    pim_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, {'$toInt': '$nhl_stats.stats.pims'}, 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    blocks_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.hits', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    pm_leaders = skaters_collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.plus_minus', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])
    
    leaders = [{'title': 'Goal Leaders', 'leaders': goal_leaders}, {'title': 'Assist Leaders', 'leaders': assist_leaders}, {'title': 'Point Leaders', 'leaders': point_leaders},
                 {'title': 'Shot Leaders', 'leaders': shots_leaders}, {'title': 'Hit Leaders', 'leaders': hits_leaders}, {'title': 'PIM Leaders', 'leaders': pim_leaders},
                 {'title': 'Block Leaders', 'leaders': blocks_leaders}, {'title': '+/- Leaders', 'leaders': pm_leaders}]

    return render_template('stats_leaders.html', leaders=leaders, title='Leaders')

@app.route('/team-standings')
def standings():
    # Handles filtering for teams standings

    stat_filter = request.args.get('filter')
    teams = get_filter_teams(stat_filter)

    return render_template('team_standings.html', title='Teams', teams=teams)

@app.route('/team-stats')
def team_stats():
    # Handles team stats page and data

    stat_filter = request.args.get('filter')
    teams = get_filter_teams(stat_filter)

    return render_template('team_stats.html', teams=teams, title='Teams')

@app.route('/team-win-percents')
def team_win_percents():
    # Handles team win percents page and data

    stat_filter = request.args.get('filter')
    teams = get_filter_teams(stat_filter)

    return render_template('team_win_percents.html', teams=teams, title='Teams')

@app.route('/team/<team_id>/')
def individual_team(team_id):
    # Handles individual team pages

    team_data = teams_collection.find({"_id": int(team_id)})
    temp_roster = []

    for player_id in team_data[0]['roster']['roster']:
        # Adds each player to team roster

        check = skaters_collection.count_documents({"_id": int(player_id['id'])})
        # MongoDB function to count how many documents are found

        if check != 0:
            player_data = skaters_collection.find_one({"_id": int(player_id['id'])}, 
                                            {"_id": 1, "nhl_stats": 1, "info": 1, "position": 1})
            if player_data['nhl_stats']:                    
                temp_roster.append(player_data)

    upcoming_games = []
    past_games = []

    for game in team_data[0]['schedule']['schedule']:
        # Adds games to either upcoming game list or past game list

        if game['game_state'] == 'Scheduled':
            upcoming_games.append(game)
        else:
            past_games.append(game)

    return render_template('individual_team.html', team_data=team_data[0], team_id=team_id, title=team_data[0]['info']['name'], roster=temp_roster, upcoming_schedule=upcoming_games,
                            past_schedule=past_games)

@app.route('/game-center/')
def game_center():
    # Handles Game Center Page and Data

    updated_game_data=display_current_game_updates(get_current_games()) # Gets all new game updates
    
    
    return render_template('game_center.html', title='Game Center', games=updated_game_data['games'], selected_game=updated_game_data['selected_game'][0], home_record=updated_game_data['home_team_record'],
                    away_record=updated_game_data['away_team_record'], current_period=updated_game_data['current_period'], recent_plays=updated_game_data['recent_plays'], 
                    home_players=updated_game_data['home_players'], away_players=updated_game_data['away_players'])

#------ Helper methods
def get_current_games():
    # Returns all current games for active day

    current_games_data = requests.get('https://statsapi.web.nhl.com/api/v1/schedule').json()

    return [games['gamePk'] for games in current_games_data['dates'][0]['games']]

def display_current_game_updates(current_games):
    # Returns all new updates in live games

    selected_game_id = request.args.get('game_id')
    selected_game, games = [], []

    for game_id in current_games:
        # Add all 
        game = games_collecion.find({"_id": game_id})[0]
        games.append(game)
        if str(game_id) == selected_game_id:
            # Find selected game
            selected_game.append(game)

    if not selected_game:
        selected_game.append(games[0])

    current_period = get_current_period(selected_game[0]['game_state']['current_period'])

    recent_plays = []
    if 'plays' in selected_game[0]['game_plays'] and not selected_game[0]['game_plays']['plays'] and len(selected_game[0]['game_plays']['plays']) > 4:
        # Creates a list with 5 most recent plays
        plays = [(selected_game[0]['game_plays']['plays'][-1]),(selected_game[0]['game_plays']['plays'][-2]),(selected_game[0]['game_plays']['plays'][-3]),
                                    (selected_game[0]['game_plays']['plays'][-4]),(selected_game[0]['game_plays']['plays'][-5])]

        for play in plays:
            # Format the plays

            p = f"{play['about']['periodTimeRemaining']} {play['about']['ordinalNum']} "
            if 'team' in play:
                p += f"{play['team']['triCode']} "
            p += f"{play['result']['description']}"
            recent_plays.append(p)
    else:
        # If there are not enough plays yet, display NA
        recent_plays = ['NA', 'NA', 'NA', 'NA', 'NA']

    home_team_record, home_players = get_live_game_data_teams(selected_game, 'home')
    away_team_record, away_players = get_live_game_data_teams(selected_game, 'away')

    return {'games': games, 'selected_game': selected_game, 'home_team_record': home_team_record, 'away_team_record': away_team_record, 
            'current_period': current_period, 'recent_plays': recent_plays, 'home_players': home_players, 'away_players': away_players}

def get_filter_title_players(stat_filter):
    # Helper method for individual skaters
    # Returns filter title given applied filter

    if stat_filter == 'home_away_splits':
        return 'Home Away Splits'
    elif stat_filter == 'win_loss_splits':
        return 'Win Loss Splits'
    elif stat_filter == 'monthly_splits':
        return 'Monthly Splits'
    elif stat_filter == 'divisional_splits':
        return 'Divisional Splits'
    elif stat_filter == 'team_splits':
        return 'Opponent Splits'
    elif stat_filter == 'minor_leagues_stats':
        return 'Minor League Stats'
    return 'NHL Stats'

def get_filter_teams(stat_filter):
    # Returns filtering for team stats

    if stat_filter == 'pacific':
        return teams_collection.find({"info.division.name": 'Pacific'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'central':
        return teams_collection.find({"info.division.name": 'Central'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'metropolitan':
        return teams_collection.find({"info.division.name": 'Metropolitan'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'atlantic':
        return teams_collection.find({"info.division.name": 'Atlantic'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'western':
        return teams_collection.find({"info.conference.name": 'Western'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'eastern':
        return teams_collection.find({"info.conference.name": 'Eastern'}, {'_id': 1, 'info': 1, 'stats': 1})
    else:
        return teams_collection.find({}, {'_id': 1, 'info': 1, 'stats': 1})

def get_current_period(period_code):
    # Converts period code to a string

    if period_code == 1:
        return "1st"
    elif period_code == 2:
        return "2nd"
    elif period_code == 3:
        return "3rd"
    elif period_code == 4:
        return "OT"
    else:
        return "1st"

def get_live_game_data_teams(selected_game, side):
    # Returns live game data for specified team

    players = []
    for player in selected_game[0]['teams'][side]['roster']:
        if 'stats' in player:
            players.append(player)

    team_id = selected_game[0]['teams'][side]['id']

    team = teams_collection.find({"_id": team_id}, {'roster': 1, 'stats': 1})[0]

    team_record = f"{team['stats']['wins']}-{team['stats']['losses']}-{team['stats']['ot_losses']}"

    return team_record, players

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
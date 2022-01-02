from warnings import filters
from flask import Flask, render_template, request
from pymongo import MongoClient
from collections import deque
from pymongo.message import update
import requests
import threading
import datetime

app = Flask(__name__, static_folder='static')


#mongodb_client = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
mongodb_client = MongoClient(f"mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

db = mongodb_client['NHL']
skaters_collection = db['skaters']
teams_collection = db['teams']
games_collecion = db['games']


@app.route('/skaters')
def stats():

    players = skaters_collection.find({ '$and': [{'nhl_stats': { '$exists': 'true', '$ne': [] }}, {'nhl_stats.year': {'$eq': '20212022'}} ] }, {'info': 1, 'nhl_stats': 1})

    return render_template('datatable.html', title="NHL Stat Leaders", players=players)

@app.route('/')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/individual/<player_id>/')
def individual_skater(player_id):

    print(player_id)

    query = {"_id": int(player_id)}

    stat_filter = request.args.get('filter')
    filter_title = 'NHL Stats'

    if stat_filter == 'home_away_splits':
        filter_title = 'Home Away Splits'
    elif stat_filter == 'win_loss_splits':
        filter_title = 'Win Loss Splits'
    elif stat_filter == 'monthly_splits':
        filter_title = 'Monthly Splits'
    elif stat_filter == 'divisional_splits':
        filter_title = 'Divisional Splits'
    elif stat_filter == 'team_splits':
        filter_title = 'Opponent Splits'
    elif stat_filter == 'minor_leagues_stats':
        filter_title = 'Minor League Stats'
    else:
        stat_filter = 'nhl_stats'

    player_data = skaters_collection.find(query)

    for p in player_data:
        player_stats = p[str(stat_filter)]
        player = p
    
    labels,ppg,apg,gpg,spg,hpg,pp_pg = [], [], [], [], [], [], []
    
    data_keys = ['goals', 'assists', 'points', 'pims', 'power_play_points', 'plus_minus']
    for szn in player['nhl_stats']:
        labels.append(szn['year'])
        ppg.append(round(szn['stats']['points']/szn['stats']['games_played'],2))
        gpg.append(round(szn['stats']['goals']/szn['stats']['games_played'],2))
        apg.append(round(szn['stats']['assists']/szn['stats']['games_played'],2))
        spg.append(round(szn['stats']['shots']/szn['stats']['games_played'],2))
        hpg.append(round(szn['stats']['hits']/szn['stats']['games_played'],2))
        pp_pg.append(round(szn['stats']['power_play_points']/szn['stats']['games_played'],2))


    tg,ta,tp,tpim,tppp,tpm,szn_num = 0,0,0,0,0,0,0
    for szn in player['nhl_stats']:
        if szn['year'] != '20212022':
            szn_num += 1
            tg += szn['stats']['goals']
            ta += szn['stats']['assists']
            tp += szn['stats']['points']
            tpim += int(szn['stats']['pims'])
            tppp += szn['stats']['power_play_points']
            tpm += szn['stats']['plus_minus']

    ca_values = [tg/szn_num, ta/szn_num, tp/szn_num, tpim/szn_num, tppp/szn_num, tpm/szn_num]

    gl_labels, gl_p_values = [], []
    for szn in player['game_log_splits']:
        gl_labels = deque(gl_labels)
        gl_p_values = deque(gl_p_values)

        gl_labels.appendleft(f"{szn['filter']} ({szn['date']})")
        gl_p_values.appendleft(szn['stats']['points'])

        gl_labels = list(gl_labels)
        gl_p_values = list(gl_p_values)

    
    t_labels, t_p_values = [], []
    for szn in player['team_splits']:
        t_labels.append(szn['filter'])
        t_p_values.append(szn['stats']['points'])

    gs_labels, gs_g_values = [], []
    for count, (key, value) in enumerate(player['goals_by_game_situation_splits'].items()):
        gs_labels.append(key.replace("_", " "))
        gs_g_values.append(value)

    
    op_labels, op_values = [], []
    
    for count, (key, value) in enumerate(player['on_pace_for_splits'][0]['stats'].items()):
        if key in data_keys:
            op_labels.append(key.replace("_", " "))
            op_values.append(int(value))


    return render_template('individual_stats.html', player=player_stats, title=player['info']['name'], filter=stat_filter, 
                            filter_title=filter_title, player_id=player_id, player_info=player['info'],  ppg_values=ppg, gpg_values=gpg, apg_values=apg, spg_values=spg, hpg_values=hpg, 
                            pp_pg_values=pp_pg, labels=labels, t_labels=t_labels, t_p_values=t_p_values, gl_labels=gl_labels, gl_p_values=gl_p_values, gs_g_values=gs_g_values, gs_labels=gs_labels,
                            op_labels=op_labels, op_values=op_values, ca_values=ca_values, player_team=player['team'])

@app.route('/stats-leaders')
def leaders():
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
    stat_filter = request.args.get('filter')

    if stat_filter == 'pacific':
        teams = teams_collection.find({"info.division.name": 'Pacific'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'central':
        teams = teams_collection.find({"info.division.name": 'Central'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'metropolitan':
        teams = teams_collection.find({"info.division.name": 'Metropolitan'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'atlantic':
        teams = teams_collection.find({"info.division.name": 'Atlantic'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'western':
        teams = teams_collection.find({"info.conference.name": 'Western'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'eastern':
        teams = teams_collection.find({"info.conference.name": 'Eastern'}, {'_id': 1, 'info': 1, 'stats': 1})
    else:
        teams = teams_collection.find({}, {'_id': 1, 'info': 1, 'stats': 1})

    return render_template('team_standings.html', title='Teams', teams=teams)

@app.route('/team-stats')
def team_stats():
    stat_filter = request.args.get('filter')

    if stat_filter == 'pacific':
        teams = teams_collection.find({"info.division.name": 'Pacific'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'central':
        teams = teams_collection.find({"info.division.name": 'Central'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'metropolitan':
        teams = teams_collection.find({"info.division.name": 'Metropolitan'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'atlantic':
        teams = teams_collection.find({"info.division.name": 'Atlantic'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'western':
        teams = teams_collection.find({"info.conference.name": 'Western'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'eastern':
        teams = teams_collection.find({"info.conference.name": 'Eastern'}, {'_id': 1, 'info': 1, 'stats': 1})
    else:
        teams = teams_collection.find({}, {'_id': 1, 'info': 1, 'stats': 1})

    return render_template('team_stats.html', teams=teams, title='Teams')

@app.route('/team-win-percents')
def team_win_percents():
    stat_filter = request.args.get('filter')

    if stat_filter == 'pacific':
        teams = teams_collection.find({"info.division.name": 'Pacific'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'central':
        teams = teams_collection.find({"info.division.name": 'Central'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'metropolitan':
        teams = teams_collection.find({"info.division.name": 'Metropolitan'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'atlantic':
        teams = teams_collection.find({"info.division.name": 'Atlantic'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'western':
        teams = teams_collection.find({"info.conference.name": 'Western'}, {'_id': 1, 'info': 1, 'stats': 1})
    elif stat_filter == 'eastern':
        teams = teams_collection.find({"info.conference.name": 'Eastern'}, {'_id': 1, 'info': 1, 'stats': 1})
    else:
        teams = teams_collection.find({}, {'_id': 1, 'info': 1, 'stats': 1})

    return render_template('team_win_percents.html', teams=teams, title='Teams')

@app.route('/team/<team_id>/')
def individual_team(team_id):
    query = {"_id": int(team_id)}

    team_data = teams_collection.find(query)

    temp_roster = []

    for player_id in team_data[0]['roster']['roster']:
        check = skaters_collection.count_documents({"_id": int(player_id['id'])})
        if check != 0:
            player_data = skaters_collection.find_one({"_id": int(player_id['id'])}, 
                                            {"_id": 1, "nhl_stats": 1, "info": 1, "position": 1})
            if player_data['nhl_stats']:                    
                temp_roster.append(player_data)

    upcoming_games = []
    past_games = []
    for game in team_data[0]['schedule']['schedule']:
        if game['game_state'] == 'Scheduled':
            upcoming_games.append(game)
        else:
            past_games.append(game)

    return render_template('individual_team.html', team_data=team_data[0], team_id=team_id, title=team_data[0]['info']['name'], roster=temp_roster, upcoming_schedule=upcoming_games,
                            past_schedule=past_games)

@app.route('/game-center/')
def game_center():

    games = []
    current_games = get_current_games()
    for game_id in current_games:
        game = games_collecion.find({"_id": game_id})[0]
        games.append(game)

    updated_game_data=display_current_game_updates()
    
    return render_template('game_center.html', title='Game Center', games=updated_game_data['games'], selected_game=updated_game_data['selected_game'][0], home_record=updated_game_data['home_team_record'],
                    away_record=updated_game_data['away_team_record'], current_period=updated_game_data['current_period'], recent_plays=updated_game_data['recent_plays'], 
                    home_players=updated_game_data['home_players'], away_players=updated_game_data['away_players'])


#------ Helper methods
def sort_leaders(cursor):
    leaders = []

def get_current_games():
    current_games_data = requests.get('https://statsapi.web.nhl.com/api/v1/schedule').json()
    current_games = []

    for games in current_games_data['dates'][0]['games']:
        current_games.append(games['gamePk'])

    return current_games

def display_current_game_updates():
    current_games = get_current_games()
    selected_game_id = request.args.get('game_id')
    selected_game = []
    games = []
    for game_id in current_games:
        game = games_collecion.find({"_id": game_id})[0]
        games.append(game)
        if str(game_id) == selected_game_id:
            selected_game.append(game)

    if selected_game == []:
        selected_game.append(games[0])

    current_period = "1st"
    if selected_game[0]['game_state']['current_period'] == 1:
        current_period = "1st"
    elif selected_game[0]['game_state']['current_period'] == 2:
        current_period = "2nd"
    elif selected_game[0]['game_state']['current_period'] == 3:
        current_period = "3rd"
    elif selected_game[0]['game_state']['current_period'] == 4:
        current_period = "OT"
    
    recent_plays = []
    if 'plays' in selected_game[0]['game_plays'] and selected_game[0]['game_plays']['plays'] != [] and len(selected_game[0]['game_plays']['plays']) > 4:
        plays = [(selected_game[0]['game_plays']['plays'][-1]),(selected_game[0]['game_plays']['plays'][-2]),(selected_game[0]['game_plays']['plays'][-3]),
                                    (selected_game[0]['game_plays']['plays'][-4]),(selected_game[0]['game_plays']['plays'][-5])]

        for play in plays:
            p = f"{play['about']['periodTimeRemaining']} {play['about']['ordinalNum']} "
            if 'team' in play:
                p += f"{play['team']['triCode']} "
            p += f"{play['result']['description']}"
            recent_plays.append(p)
    else:
        recent_plays = ['NA', 'NA', 'NA', 'NA', 'NA']

    home_players = []
    for player in selected_game[0]['teams']['home']['roster']:
        if 'stats' in player:
            home_players.append(player)
    
    away_players = []
    for player in selected_game[0]['teams']['away']['roster']:
        if 'stats' in player:
            away_players.append(player)

    home_team_id = selected_game[0]['teams']['home']['id']
    away_team_id = selected_game[0]['teams']['away']['id']   

    home_team = teams_collection.find({"_id": home_team_id}, {'roster': 1, 'stats': 1})[0]
    away_team = teams_collection.find({"_id": away_team_id}, {'roster': 1, 'stats': 1})[0]

    home_team_record = f"{home_team['stats']['wins']}-{home_team['stats']['losses']}-{home_team['stats']['ot_losses']}"
    away_team_record = f"{away_team['stats']['wins']}-{away_team['stats']['losses']}-{away_team['stats']['ot_losses']}"
    return {'games': games, 'selected_game': selected_game, 'home_team_record': home_team_record, 'away_team_record': away_team_record, 'current_period': current_period, 'recent_plays': recent_plays, 'home_players': home_players, 'away_players': away_players}

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
from warnings import filters
from flask import Flask, render_template, request
from pymongo import MongoClient
import os
from collections import deque

app = Flask(__name__, static_folder='static')


mongodb_client = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
db = mongodb_client['NHL']
collection = db['skaters']

@app.route('/skaters')
def stats():

    players = collection.find({ '$and': [{'nhl_stats': { '$exists': 'true', '$ne': [] }}, {'nhl_stats.year': {'$eq': '20212022'}} ] }, {'info': 1, 'nhl_stats': 1})

    return render_template('datatable.html', title="NHL Stat Leaders", players=players)

@app.route('/')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/individual/<player_id>/')
def individual_skater(player_id):

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

    player_data = collection.find(query)

    for p in player_data:
        player_stats = p[str(stat_filter)]
        player = p
    
    labels,ppg,apg,gpg,spg,hpg,pp_pg = [], [], [], [], [], [], []

    
    for szn in player['nhl_stats']:
        labels.append(szn['year'])
        ppg.append(round(szn['stats']['points']/szn['stats']['games_played'],2))
        gpg.append(round(szn['stats']['goals']/szn['stats']['games_played'],2))
        apg.append(round(szn['stats']['assists']/szn['stats']['games_played'],2))
        spg.append(round(szn['stats']['shots']/szn['stats']['games_played'],2))
        hpg.append(round(szn['stats']['hits']/szn['stats']['games_played'],2))
        pp_pg.append(round(szn['stats']['power_play_points']/szn['stats']['games_played'],2))

    p, a, g, s, h, pp = [], [], [], [], [], []
    for szn in player['nhl_stats']:
        p.append(szn['stats']['points'])
        g.append(szn['stats']['goals'])
        a.append(szn['stats']['assists'])
        s.append(szn['stats']['shots'])
        h.append(szn['stats']['hits'])
        pp.append(szn['stats']['power_play_points'])


    gl_labels,gl_p_values = [], []
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

    return render_template('individual_stats.html', player=player_stats, title=player['info']['name'], filter=stat_filter, 
                            filter_title=filter_title, player_id=player_id, player_info=player['info'],  ppg_values=ppg, gpg_values=gpg, apg_values=apg, spg_values=spg, hpg_values=hpg, 
                            pp_pg_values=pp_pg, labels=labels, gl_labels=gl_labels, gl_p_values=gl_p_values, t_labels=t_labels, t_p_values=t_p_values, p_values=p, g_values=g,
                            a_values=a, s_values=s, h_values=h, pp_values=pp)



@app.route('/stats-leaders')
def leaders():

    #goal_leaders = collection.find({'nhl_stats.year': '20202021'},{'_id': 1, 'info.name': 1, 'nhl_stats.stats.goals': 1})
    
    

    goal_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.goals', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])
    
    assist_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.assists', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    point_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.points', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    shots_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.shots', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    hits_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.hits', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    pim_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, {'$toInt': '$nhl_stats.stats.pims'}, 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    blocks_leaders = collection.aggregate([
        {'$unwind':"$nhl_stats"}, 
        {'$group': {
            '_id': '$_id',
            'name': {"$first": "$info.name"}, 
            "stats": {"$last": {"$cond": [{ '$eq': ["$nhl_stats.year", '20212022']}, '$nhl_stats.stats.hits', 0]}}
        }},
        {'$sort': {'stats': -1}},
        {'$limit': 5}
        ])

    pm_leaders = collection.aggregate([
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

    return render_template('stats_leaders.html', leaders=leaders)



#------ Helper methods
def sort_leaders(cursor):
    leaders = []

    

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
from warnings import filters
from flask import Flask, render_template, request
from pymongo import MongoClient
import os
import requests

app = Flask(__name__)


mongodb_client = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
db = mongodb_client['NHL']
collection = db['skaters']

@app.route('/skaters')
def stats():

    players = collection.find({ '$and': [{'nhl_stats': { '$exists': 'true', '$ne': [] }}, {'nhl_stats.year': {'$eq': '20212022'}} ] })

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

    return render_template('individual_stats.html', player=player_stats, title=player['info']['name'], filter=stat_filter, 
                            filter_title=filter_title, player_id=player_id, player_info=player['info'])

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
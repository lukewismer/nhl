from flask import Flask, render_template
from pymongo import MongoClient
import os
import requests

app = Flask(__name__)


mongodb_client = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")
db = mongodb_client['NHL']
collection = db['skaters']

@app.route('/')
def home():

    players = collection.find({ 'nhl_stats': { '$exists': 'true', '$ne': [] } })
    return render_template('datatable.html', title="NHL Stat Leaders", players=players)

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
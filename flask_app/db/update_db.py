from games_db import update_games
from live_games_db import update_live_games_thread
from player_db import update_players
from team_db import update_teams

def update_db():
    update_players()
    update_teams()
    update_games()
    update_live_games_thread()

update_db()
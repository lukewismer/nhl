def update_mongo_skaters(player_id, player_data, collection_skaters):
    # Updates one player to the mongodb

    if collection_skaters.find_one({'_id': player_id}):
        # If player already exists in DB

        keys = {'nhl_stats': player_data['nhl_stats'], 'info': player_data['info'], 'home_away_splits': player_data['home_away_splits'], 'win_loss_splits': player_data['win_loss_splits'], 'monthly_splits': player_data['monthly_splits'],
            'divisional_splits': player_data['divisional_splits'], 'team_splits': player_data['team_splits'], 'game_log_splits': player_data['game_log_splits'], 'goals_by_game_situation_splits': player_data['goals_by_game_situation_splits'],
            'on_pace_for_splits': player_data['on_pace_for_splits']}

        for count, (key,value) in enumerate(keys.items()):
            # Gets the key and the value from the keys dict

            collection_skaters.update_one({"_id": player_id}, {"$set": {key: value}})

    else:
        # If the player does not exists in DB, insert player

        collection_skaters.insert_one(player_data)

def update_mongo_teams(team_id, team_data, collection_teams):
    # Updates teams to mongoDB one at a time

    if collection_teams.find_one({'_id': team_id}):
        # If team already exist in DB

        keys = {'info': team_data['info'], 'roster': team_data['roster'], 'stats': team_data['stats'],
                'schedule': team_data['schedule'], 'upcoming_game': team_data['upcoming_game']}

        for count, (key,value) in enumerate(keys.items()):
            # Gets the key and value from keys dict then updates it

            collection_teams.update_one({"_id": team_id}, {"$set": {key: value}})

    else:
        # If team doesnt exist in db
        collection_teams.insert_one(team_data)

def update_mongo_games(game_id, game_data, collection_games):
    # Updates one game at a time to mongoDB

    if game_data['status']['state'] != "Final" and game_data['status']['state'] != "Postponed":
        # Only update if the game isn't already done

        if collection_games.find_one({'_id': game_id}):
            # If the game is already in the data base
            keys = {'status': game_data['status'], 'teams': game_data['teams'], 'game_state': game_data['game_state'],
                'game_plays': game_data['game_plays']}

            for count, (key,value) in enumerate(keys.items()):
                # Update the game in db
                collection_games.update_one({"_id": game_id}, {"$set": {key: value}})
        else:
            # If the game is not in the db, insert it
            collection_games.insert_one(game_data)

def update_mongo_live_games(game_id, game_data, collection_games):
    # Updates one live game at a time

    keys = {'status': game_data['status'], 'teams': game_data['teams'], 'game_state': game_data['game_state'],
        'game_plays': game_data['game_plays']}

    for count, (key,value) in enumerate(keys.items()):
        # Updates the game with new data
        collection_games.update_one({"_id": game_id}, {"$set": {key: value}})        
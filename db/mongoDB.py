from pymongo import MongoClient
import os

try:
    conn = MongoClient(f"mongodb+srv://{os.environ.get('mongoDBuser')}:{os.environ.get('mongoDBpwd')}@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    print('Succesfull connection')

except:
    print("Could not connect to MongoDB")

db = conn['NHL']
collection = db['skaters']

def send_data_to_mongo_skaters(data):

    collection.insert_one(data)


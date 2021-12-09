from pymongo import MongoClient

try:
    conn = MongoClient("mongodb+srv://lukeWismer:Luke4791@nhl.8x936.mongodb.net/NHL?retryWrites=true&w=majority")

    print('Succesfull connection')

except:
    print("Could not connect to MongoDB")

db = conn['NHL']
collection = db['skaters']

def send_data_to_mongo_skaters(data):

    collection.insert_one(data)


from pymongo.mongo_client import MongoClient
import certifi
import os


# Function to initialize the MongoDB connection
def get_mongo_client():
    # Store your MongoDB URI in an environment variable by running `export MONGODB_URI="your_mongodb_uri"`
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI environment variable is not set")
    
    # Initialize MongoDB client
    client = MongoClient(uri, tlsCAFile=certifi.where())
    return client

def get_db(database_name="database"):
    client = get_mongo_client()
    db = client[database_name]
    return db

def get_collection(collection_name):
    db = get_db()
    collection = db[collection_name]
    return collection

def close_connection():
    client = get_mongo_client()
    client.close()


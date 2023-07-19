from pymongo import MongoClient

username = "deepnote"
password = "Mn3xGCTLR3SFRb0T"


def mongo_tilt_db():
    client = MongoClient(
        f"mongodb+srv://{username}:{password}@frederickscluster.tyiku.mongodb.net/?retryWrites=true&w=majority"
    )
    db = client.tilt_test
    return db

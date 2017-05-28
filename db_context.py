import pymongo

class DbContext:
    def __init__(self, URI, db_name, collection_name):
        self.client = pymongo.MongoClient(URI)
        self.db = self.client[db_name]
        # print(db.collection_names(include_system_collections=False))
        # creates the collection if it does not exist
        self.collection = self.db[collection_name]
        count = self.collection.find().count()
        print('{0} entries in the collection'.format(count))

    def insert_feeds(self, data):
        print('inserting feeds into the database...')
        self.collection.insert_many(data)

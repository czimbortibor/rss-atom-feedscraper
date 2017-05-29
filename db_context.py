import pymongo


class DbContext:
    def __init__(self, URI, db_name, collection_name):
        print('connecting to the MongoDB...')
        try:
            self.client = pymongo.MongoClient(URI)
            self.db = self.client[db_name]
            # print(db.collection_names(include_system_collections=False))
            # creates the collection if it does not exist
            self.collection = self.db[collection_name]
            count = self.collection.find().count()
            print('{0} entries in the {1} collection'.format(count, collection_name))
        except Exception as ex:
            print(ex)

    def get_collection(self):
        return self.collection

    def change_collection(self, collection_name):
        self.collection = self.db[collection_name]
        count = self.collection.find().count()
        print('{0} entries in the {1} collection'.format(count, collection_name))
        return self.collection

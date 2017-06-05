import pymongo


class DbContext:
    def __init__(self, uri, db_name, feeds_name_collection, feeds_collection, image_collection):
        print('connecting to the MongoDB...')
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[db_name]
            # print(db.collection_names(include_system_collections=False))
            # creates the collection if it does not exist
            self.feeds_name_collection = self.db[feeds_name_collection]
            count = self.feeds_name_collection.find().count()
            print('{0} entries in the {1} collection'.format(count, feeds_name_collection))

            self.feeds_collection = self.db[feeds_collection]
            self.image_collection = self.db[image_collection]
        except Exception as ex:
            print(ex)

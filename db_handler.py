import pymongo


def db_init():
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client['local']
    collection = db['feeds']
    collection.insert_one({'url': 'https://www.theverge.com/rss/index.xml',
                           'tags': ''})
    print(db.collection_names(include_system_collections=False))

import os
from multiprocessing import Pool
import pymongo

from db_context import DbContext
from scraper import Scraper
from config_handler import ConfigHandler
from logger import Logger


def main():
    feeds_file_input = os.path.abspath('config/feed_list.json')
    db_config_file = os.path.abspath('config/db_config.json')
    config_handler = ConfigHandler(feeds_file_input, db_config_file)
    uri, db_name, feeds_name_collection, feeds_collection, image_collection = config_handler.get_db_config()
    db_context = DbContext(uri, db_name, feeds_name_collection, feeds_collection, image_collection)

    Logger.log('reading {0} ...'.format(feeds_file_input))
    feed_list, feed_list_jsondata = config_handler.load_feed_list()
    Logger.log('collecting from {0} feeds'.format(len(feed_list)))

    Logger.log('inserting the feed list into the database...')
    for feed in feed_list_jsondata:
        db_context.feeds_name_collection.update_one({'url': feed['url']}, {'$set': feed}, upsert=True)

    scraper = Scraper(feed_list)

    entries = scraper.get_entries()
    # get the metadata in interest and the images
    with Pool() as pool:
        metadata = pool.map(scraper.get_metadata, entries)

    Logger.log('inserting metadata into the database...')
    for feed_data in metadata:
        db_context.feeds_collection.update_one({'link': feed_data['link']}, {'$set': feed_data}, upsert=True)
    #db_context.feeds_collection.update_many(metadata, {'$set': metadata}, upsert=True)
    metadata_number = db_context.feeds_collection.find({}).count()
    Logger.log('{0} metadata inserted'.format(metadata_number))

    Logger.log('creating indexes...')
    # multiple indexes
    """index1 = pymongo.IndexModel([('title', pymongo.TEXT)], default_language='english', name='title_index')
    index2 = pymongo.IndexModel([('summary', pymongo.TEXT)], default_language='english', name='summary_index')
    db_context.feeds_collection.create_indexes([index1, index2])
    """
    # compound index
    db_context.feeds_collection.create_index([('title', pymongo.TEXT), ('summary', pymongo.TEXT)],
        default_language='english', name='title_summary_index')

    images_path_file = 'config/image_collection.json'
    images_path = config_handler.load_image_collection_path(images_path_file)
    Logger.log('downloading the images...')
    download_dir = scraper.download_images(metadata, images_path)

    Logger.log('inserting image collection path into the database...')
    full_img_path = os.path.abspath(download_dir)
    data = {'path': full_img_path}
    db_context.image_collection.update_one(data, {'$set': data}, upsert=True)

    Logger.log('all done.\n')

if __name__ == '__main__':
    main()

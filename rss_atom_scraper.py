import sys
from multiprocessing import Pool

from db_context import DbContext
from scraper import Scraper
import config_handler


def db_connect(URI, db_name, collection_name):
    ''' MongoDB connection'''
    db_context = DbContext(URI, db_name, collection_name)
    return db_context


def main(argv):
    if len(argv) == 1:
        feeds_file_input = 'feed_list.json'
    else:
        feeds_file_input = argv[1]
    feed_list, feed_data = config_handler.load_feed_list(feeds_file_input)
    print('feeds: {0}'.format(len(feed_list)))

    URI = 'mongodb://localhost:27017'
    db_name = 'local'
    collection_name = 'RSSFeeds'
    db_context = db_connect(URI, db_name, collection_name)
    db_collection = db_context.get_collection()

    scraper = Scraper(feed_list)

    entries = scraper.get_entries()
    # get the metadata in interest
    with Pool() as pool:
        metadata = pool.map(scraper.get_metadata, entries)

    if db_collection:
        print('inserting feeds into the database...')
        db_collection.insert_many(metadata)
    else:
        print('db connection was not set up!')

    # get the images
    with Pool() as pool:
        img_urls = pool.map(scraper.scrape_images, entries)

    scraper.download_images(img_urls)


if __name__ == '__main__':
    main(sys.argv)

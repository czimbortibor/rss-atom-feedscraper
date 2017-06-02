import sys
from multiprocessing import Pool

from db_context import DbContext
from scraper import Scraper

from config_handler import ConfigHandler


def main(argv=None):
    if len(argv) == 1:
        feeds_file_input = 'config/feed_list.json'
    else:
        feeds_file_input = argv[1]

    db_config_file = 'config/db_config.json'
    config_handler = ConfigHandler(feeds_file_input, db_config_file)
    URI, db_name, feeds_name_collection, feeds_collection, image_collection = config_handler.get_db_config()
    db_context = DbContext(URI, db_name, feeds_name_collection, feeds_collection, image_collection)

    print('reading {0} ...'.format(feeds_file_input))
    feed_list, feed_list_jsondata = config_handler.load_feed_list()
    print('feeds: {0}\n'.format(len(feed_list)))

    print('inserting the feed list into the database...\n')
    db_context.feeds_name_collection.insert_many(feed_list_jsondata)

    scraper = Scraper(feed_list)

    entries = scraper.get_entries()
    # get the metadata in interest and the images
    with Pool() as pool:
        metadata = pool.map(scraper.get_metadata, entries)

    print('inserting feeds into the database...\n')
    db_context.feeds_collection.insert_many(metadata)

    print('\ndownloading the images...\n')
    # download the images and return the directory name
    img_dir = scraper.download_images(metadata)

    print('inserting image collection path into the database...\n')
    import os
    full_img_path = os.path.abspath('../' + img_dir)
    data = {'path': full_img_path}
    db_context.image_collection.insert(data)


if __name__ == '__main__':
    main(sys.argv)

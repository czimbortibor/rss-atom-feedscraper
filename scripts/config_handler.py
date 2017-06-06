import json

import get_rss_feed
from logger import Logger


class ConfigHandler:
    def __init__(self, feeds_file, db_config_file):
        self.feeds_file = feeds_file
        self.db_config_file = db_config_file


    def get_db_config(self):
        try:
            with open(self.db_config_file) as file:
                json_contents = json.load(file)
        except FileNotFoundError:
            Logger.log('Wrong input JSON file for the database connection!')
            return

        URI = json_contents['URI']
        db_name = json_contents['db_name']
        feeds_name_collection = json_contents['feeds_name_collection']
        feeds_collection = json_contents['feeds_collection']
        image_collection = json_contents['image_collection']
        return URI, db_name, feeds_name_collection, feeds_collection, image_collection


    def load_feed_list(self):
        try:
            with open(self.feeds_file) as file:
                feeds_data = json.load(file)
        except FileNotFoundError:
            Logger.log('Wrong input JSON file of the feed list!')
            return None, None

        feed_list = []
        for feed in feeds_data:
            feed_list.append(feed['url'])

        # print('feed urls: {0}'.format(feed_list))
        return feed_list, feeds_data

    @staticmethod
    def load_image_collection_path(images_path_file):
        try:
            with open(images_path_file) as file:
                contents = json.load(file)
        except FileNotFoundError:
            Logger.log('Wrong input JSON file for the image collection path!')
            return None

        return contents['path']

    def append_feed(self, website_url, tags, db_context):
        try:
            with open(self.feeds_file) as file:
                json_contents = json.load(file)
        except FileNotFoundError:
            Logger.log('Wrong input JSON file of the feed list!')
            return

        feed_url = get_rss_feed.get_rss_feed(website_url)
        data = {'url': feed_url, 'tags': tags}

        json_contents.append(data)

        # write out the updated file
        with open(self.feeds_file, 'w') as file:
            json.dump(json_contents, file)

        if db_context:
            # insert into the database
            db_context.feeds_name_collection.insert(data)


    def remove_feed(self, url, db_context):
        try:
            with open(self.feeds_file) as file:
                json_contents = json.load(file)
        except FileNotFoundError:
            Logger.log('Wrong input JSON file of the feed list!')
            return

        # remove the selected feed
        for json_item in json_contents:
            if json_item['url'] == url:
                json_contents.remove(json_item)

        # write out the updated feed list
        with open(self.feeds_file, 'w') as file:
            json.dump(json_contents, file)

        if db_context:
            # remove the feed url from the database
            db_context.feeds_name_collection.delete_many({'url': url})
            

import os
from pprint import pprint
import requests

import feedparser

from config_handler import ConfigHandler
from db_context import DbContext


# UNFINISHED

class UpdateMonitor:
    def __init__(self, feeds_file_input, db_config_file):
        self.config_handler = ConfigHandler(feeds_file_input, db_config_file)
        URI, db_name, feeds_name_collection, feeds_collection, image_collection = self.config_handler.get_db_config()
        self.db_context = DbContext(URI, db_name, feeds_name_collection, feeds_collection, image_collection)

    def get_intervals(self, feed_url):

        # simple HTTP request header checking does not work for the update_interval calculation
        '''
        response = requests.get(feed_url)
        if 'Last-Modified' in response.headers:
            build_date = response.headers['Last-Modified']
            print(build_date)
            data = {'Last-Modified': build_date, 'expires': -1, 'Cache-Control': 'must-revalidate'}
            resp = requests.get(feed_url, params=data)
            
            #date = 'Fri, 4 Aug 2017 23:00:00 GMT'
            #resp = requests.get(feed_url, params={'If-Modified-Since': build_date})
            print(resp)
            update_interval = ''
        '''

        feed = feedparser.parse(feed_url)
        if 'updated' in feed['channel']:
            build_date = feed['channel']['updated']
            update_interval = ''
        elif 'sy_updateperiod' in feed['channel']:
            period = feed['channel']['sy_updateperiod']
            if period == 'hourly':
                update_interval = '60'
            else:
                update_interval = ''
            response = requests.get(feed_url)
            if 'Last-Modified' in response.headers:
                build_date = response.headers['Last-Modified']
            else:
                build_date = ''
        else:
            # if no updatePeriod is defined then the feed's build date refreshes with every request
            build_date = ''
            update_interval = ''
        if 'ttl' in feed['channel']:
            # ttl - time to live (minutes): http://www.rssboard.org/rss-specification#ltttlgtSubelementOfLtchannelgt
            update_interval = feed['channel']['ttl']

        print('\tlast updated on: {0}'.format(build_date))
        print('\tupdate interval: {0}'.format(update_interval))

        return update_interval, build_date

    def check_feeds(self):
        feed_list, feeds_data = self.config_handler.load_feed_list()
        for feed in feed_list:
            print(feed)
            update_interval, build_date = self.get_intervals(feed)
            self.db_context.feeds_name_collection.update_one({'url': feed}, {'$set': {'update_interval': update_interval, 'build_date': build_date}},
                                                                      upsert=True)
            print()

feeds_file = os.path.abspath('../config/feed_list.json')
db_config_file = os.path.abspath('../config/db_config.json')
update_monitor = UpdateMonitor(feeds_file, db_config_file)

update_monitor.check_feeds()

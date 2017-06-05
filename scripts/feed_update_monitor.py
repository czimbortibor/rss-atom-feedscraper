
import os
from datetime import datetime
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
        pass
        # simple HTTP request header checking does not work for the update_interval calculation
        """
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
        """

        feed = feedparser.parse(feed_url)
        if 'updated' in feed['channel']:
            try:
                build_date = datetime.strptime(feed['channel']['updated'], '%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                build_date = feed['channel']['updated']
            update_interval = 0
        elif 'sy_updateperiod' in feed['channel']:
            period = feed['channel']['sy_updateperiod']
            if period == 'hourly':
                update_interval = 60
            else:
                update_interval = 0
            response = requests.get(feed_url)
            if 'Last-Modified' in response.headers:
                build_date = datetime.strptime(response.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %z')
            else:
                build_date = 0
        else:
            # if no updatePeriod is defined then the feed's build date refreshes with every request
            build_date = 0
            update_interval = 0
        if 'ttl' in feed['channel']:
            # ttl - time to live (minutes): http://www.rssboard.org/rss-specification#ltttlgtSubelementOfLtchannelgt
            update_interval = int(feed['channel']['ttl'])

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

    def reload_feed(self, feed_name):
        """
            should the feed be reloaded
        """

        feed = self.db_context.feeds_name_collection.find_one({'url': feed_name})
        build_date = feed['build_date']
        update_interval = feed['update_interval']
        time_now = datetime.utcnow()
        difference = datetime(build_date) + datetime(update_interval) - time_now
        if build_date + update_interval > time_now:
            return True
        return False

feeds_file = os.path.abspath('../config/feed_list.json')
db_config_file = os.path.abspath('../config/db_config.json')
update_monitor = UpdateMonitor(feeds_file, db_config_file)

update_monitor.check_feeds()


from concurrent import futures
import re
import os
from datetime import datetime
from collections import defaultdict

import feedparser
import urllib3
from bs4 import BeautifulSoup

from logger import Logger


class Scraper:
    def __init__(self, feed_list, image_dir=''):
        self.entries = self.get_feeds(feed_list)
        self.download_dir = self.get_download_dir(image_dir)

    def get_entries(self):
        return self.entries

    def get_feeds(self, feed_list):
        entries = []
        with futures.ThreadPoolExecutor() as executor:
            future_urls = {executor.submit(feedparser.parse, feed): feed for feed in feed_list}
            for future in futures.as_completed(future_urls):
                url = future_urls[future]
                try:
                    feed = future.result()
                    entries.extend(feed['items'])
                except Exception as ex:
                    Logger.log(ex)
                finally:
                    Logger.log('{0} \t\t - parsed'.format(url))
        return entries

    def get_metadata(self, entry):
        metadata = defaultdict(list)

        if 'title' in entry:
            metadata['title'] = entry['title']
        if 'author' in entry:
            metadata['author'] = entry['author']
        if 'title_detail' in entry:
            metadata['rss'] = entry['title_detail']['base']
            domain_name = entry['title_detail']['base'].rsplit('/')[2].replace('www.', '')
        if 'summary' in entry:
            # remove the html tags
            metadata['summary'] = BeautifulSoup(entry['summary'], 'lxml').text
        if 'published' in entry:
            try:
                publish_date = datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %z').isoformat()
            except ValueError:
                publish_date = entry['published']
            metadata['published'] = publish_date
        elif 'updated' in entry:
            try:
                publish_date = datetime.strptime(entry['updated'], '%a, %d %b %Y %H:%M:%S %z').isoformat()
            except ValueError:
                publish_date = entry['updated']
            metadata['published'] = publish_date
        if 'updated' in entry:
            metadata['updated'] = entry['updated']
        if 'link' in entry:
            metadata['link'] = entry['link']

        img_url = self.scrape_image(entry)
        metadata['image_url'] = img_url

        if img_url and domain_name:
            url = img_url.rsplit('/')
            img_name = url[len(url) - 1]
            img_file_name = self.download_dir + os.path.sep + domain_name + '_' + img_name
            metadata['image_path'] = img_file_name
        else:
            metadata['image_path'] = None
        return metadata

    def scrape_image(self, entry):
        pattern_src = re.compile('(src=.*)|(img src=.*)')
        pattern_url = re.compile('url=.*')
        contents = []

        # possible image locations in the tags
        if 'content' in entry:
            contents.append(entry['content'])
        if 'media_thumbnail' in entry:
            contents.append(entry['media_thumbnail'])
        if 'summary' in entry:
            contents.append(entry['summary'])
        if 'enclosures' in entry:
            contents.append(entry['enclosures'])

        for content in contents:
            if isinstance(content, list):
                for tag in content:
                    if isinstance(tag, dict):
                        if 'value' in tag:
                            href = pattern_src.search(tag['value'])
                            if href:
                                return href.group().split('\"')[1]
                        else:
                            href = tag['url']
                            return href
                    else:
                        href = pattern_src.search(tag)
                        if href:
                            return href.group().split('\"')[1]
                        elif 'href' in tag:
                            href = tag['href']
                            return href
            else:
                href = pattern_src.search(content)
                if href:
                    splitted = href.group().split('\"')
                    if len(splitted) == 1:
                        splitted = href.group().split('\'')
                    return splitted[1]
                else:
                    href = pattern_url.search(content)
                    if href:
                        return href.group()

    def download_images(self, metadata, image_dir=''):
        count = 0
        http = urllib3.PoolManager()
        for item in metadata:
            url = item['image_url']
            try:
                response = http.request('GET', url)
            except:
                continue
            image_bytes = response.data
            url = url.rsplit('/')
            img_name = url[len(url)-1]

            if img_name:
                domain_name = item['rss'].rsplit('/')[2].replace('www.', '')
                file_name = self.download_dir + os.path.sep + domain_name + '_' + img_name
                with open(file_name, 'w+b') as output_f:
                    output_f.write(image_bytes)
                # Logger.log('{0}/{1} done'.format(count, len(metadata)))
                count += 1

        Logger.log('downloaded images: {0}'.format(count))

    def get_download_dir(self, image_dir=''):
        date_now = str(datetime.today().date())
        if image_dir == '':
            # parent directory
            image_dir = os.path.dirname(os.getcwd())
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        # specified directory + current date
        download_dir = os.path.join(image_dir, date_now)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        return download_dir

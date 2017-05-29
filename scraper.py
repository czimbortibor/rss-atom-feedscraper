from concurrent import futures
import re
import os
import datetime
from collections import defaultdict

import feedparser
import urllib3


'''
    TODO: scrape images from the original website (at least from the <head> section)
'''


class Scraper:
    def __init__(self, feed_list):
        self.entries = self.get_feeds(feed_list)

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
                    print(ex)
                finally:
                    print('{0} \t\t - parsed'.format(url))
        return entries

    def get_metadata(self, entry):
        metadata = defaultdict(list)

        if 'title' in entry:
            metadata['title'] = entry['title']
        if 'title_detail' in entry:
            metadata['rss'] = entry['title_detail']['base']
        if 'summary' in entry:
            metadata['summary'] = entry['summary']
        if 'published' in entry:
            metadata['published'] = entry['published']
        if 'updated' in entry:
            metadata['updated'] = entry['updated']
        if 'link' in entry:
            metadata['link'] = entry['link']

        return metadata

    def scrape_images(self, entry):
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
                    return href.group().split('\"')[1]
                else:
                    href = pattern_url.search(content)
                    if href:
                        return href.group()

    def download_images(self, img_urls):
        print('\ndownloading the images...\n')
        img_dir = str(datetime.date.today())
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        os.chdir(img_dir)

        count = 0
        http = urllib3.PoolManager()
        for url in img_urls:
            try:
                response = http.request('GET', url)
            except:
                continue
            image_bytes = response.data
            url = url.rsplit('/')
            file_name = url[len(url)-1]

            if file_name:
                with open(file_name, 'w+b') as output_f:
                    output_f.write(image_bytes)
                print(file_name)
                count += 1

        os.chdir('..')
        print('\ndownloaded images: {0}'.format(count))
        return img_dir
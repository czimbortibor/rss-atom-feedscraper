from concurrent import futures
import re
import os
import datetime
from collections import defaultdict

import feedparser
import urllib3
from bs4 import BeautifulSoup


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
        if 'author' in entry:
            metadata['author'] = entry['author']
        if 'title_detail' in entry:
            metadata['rss'] = entry['title_detail']['base']
            domain_name = entry['title_detail']['base'].rsplit('/')[2].replace('www.', '')
        if 'summary' in entry:
            # remove the html tags
            metadata['summary'] = BeautifulSoup(entry['summary'], 'lxml').text
        if 'published' in entry:
            metadata['published'] = entry['published']
        if 'updated' in entry:
            metadata['updated'] = entry['updated']
        if 'link' in entry:
            metadata['link'] = entry['link']

        img_url =  self.scrape_image(entry)
        metadata['image_url'] = img_url
        if img_url and domain_name:
            url = img_url.rsplit('/')
            img_name = url[len(url) - 1]
            img_file_name = domain_name + '_' + img_name
            metadata['image_file_name'] = img_file_name

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
                    return href.group().split('\"')[1]
                else:
                    href = pattern_url.search(content)
                    if href:
                        return href.group()

    def download_images(self, metadata):
        img_dir = str(datetime.date.today())
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        os.chdir(img_dir)

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
                file_name = domain_name + '_' + img_name
                with open(file_name, 'w+b') as output_f:
                    output_f.write(image_bytes)
                print(file_name)
                count += 1

        os.chdir('..')
        print('\ndownloaded images: {0}'.format(count))
        return img_dir

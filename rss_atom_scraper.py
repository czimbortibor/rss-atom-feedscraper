import feedparser
import urllib3

import sys
from concurrent import futures
from multiprocessing import Pool
import re
import os, datetime
from collections import defaultdict

import config_handler
from db_context import DbContext

'''
    TODO: scrape images from the original website (at least from the <head> section)
'''


def get_feeds(feed_list):
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


def get_metadata(entry):
    metadata = defaultdict(list)

    if 'title' in entry:
        metadata['title'] = entry['title']
    if 'summary' in entry:
        metadata['summary'] = entry['summary']
    if 'published' in entry:
        metadata['published'] = entry['published']
    if 'updated' in entry:
        metadata['updated'] = entry['updated']
    if 'link' in entry:
        metadata['link'] = entry['link']

    return metadata


def scrape_images(entry):
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


def download_images(img_urls):
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

    print('\ndownloaded images: {0}'.format(count))


def main(argv):
    if len(argv) == 1:
        feeds_file_input = 'feed_list.json'
    else:
        feeds_file_input = argv[1]
    feed_list, feed_data = config_handler.load_feed_list(feeds_file_input)
    print('feeds: {0}'.format(len(feed_list)))

    entries = get_feeds(feed_list)

    # MongoDB connection
    URI = 'mongodb://localhost:27017'
    db_name = 'local'
    collection_name = 'RSSFeeds'
    db_context = DbContext(URI, db_name, collection_name)

    # get the metadata in interest
    with Pool() as pool:
        metadata = pool.map(get_metadata, entries)

    db_context.insert_feeds(metadata)

    # get the images
    with Pool() as pool:
        img_urls = pool.map(scrape_images, entries)

    download_images(img_urls)


if __name__ == '__main__':
    main(sys.argv)

import feedparser
import urllib3

import sys
from concurrent import futures
from multiprocessing import Pool
import re
import os, datetime

import config_handler
import db_handler

'''
    sapientia   : links 
    verge       : summary
'''

# config_handler.load_feed_list('feed_list.json')
# config_handler.append_feed_list('feed_list.json', 'http://transindex.ro', ['transindex', 'transylvania', 'news', 'hirek'])

testfeed = feedparser.parse('http://www.ziaruldemures.ro/?feed=rss2')

image_regexp = re.compile('.*img.*')
for entry in testfeed['entries']:
    #print(entry)
    for link in entry['content']:
        # print(link)
        if image_regexp.search(link['value']):
            # print(link)
            pass
    #if 'media-thumbnail' in entry:
    #    print(entry['media-thumbnail'])
    #if 'media-content' in entry:
    #    print(entry['media-content'])


# testfeed = feedparser.parse('https://www.reddit.com/r/funny/.rss')
# print(testfeed['feed']['link'])
# print(type(testfeed.entries[0].content))
# print(testfeed.entries[0].content[0])


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
                print('{0} \t - parsed'.format(url))
    return entries


def parse_result(entry):
    pattern = re.compile('(src=.*)|(img src=.*)')
    tag_list = []
    if 'content' in entry:
        contents = entry['content']
    elif 'media_thumbnail' in entry:
        contents = entry['media_thumbnail']
    else:
        return None
    for tag in contents:
        if 'value' in tag:
            # print(tag['value'])
            href = pattern.search(tag['value'])
            if href:
                # tag_list.append(href.group().split('\"')[1])
                return href.group().split('\"')[1]
        else:
            href = contents[0]['url']
            # tag_list.append(href)
            return href
            # print(contents)


def download_images(img_urls):
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

    print('downloaded images: {0}'.format(count))


def main(argv):
    if len(argv) == 1:
        feeds_file_input = 'feed_list.json'
    else:
        feeds_file_input = argv[1]
    feed_list, feed_data = config_handler.load_feed_list(feeds_file_input)
    print('feeds: {0}'.format(len(feed_list)))

    entries = get_feeds(feed_list)
    with Pool() as pool:
        img_urls = pool.map(parse_result, entries)

    download_images(img_urls)


if __name__ == '__main__':
    main(sys.argv)
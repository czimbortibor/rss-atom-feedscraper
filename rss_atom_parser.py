import feedparser
import urllib3
import pymongo

from concurrent import futures
import re
import os, datetime


testfeed = feedparser.parse('https://www.theverge.com/rss/index.xml')
print(len(testfeed['entries']))

''' -------- categories ---------- '''
#for entry in testfeed['feed']:
#    print(entry)

for entry in testfeed['entries']:
    for link in entry['links']:
        print(link)
    #if 'media_thumbnail' in entry:
    #    print(entry['media_thumbnail'])
    #if 'media-content' in entry:
    #    print(entry['media-content'])


# testfeed = feedparser.parse('https://www.reddit.com/r/funny/.rss')
# print(testfeed['feed']['link'])
# print(type(testfeed.entries[0].content))
# print(testfeed.entries[0].content[0])

# db_init()
# download_images()

def db_init():
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client['local']
    collection = db['feeds']
    collection.insert_one({'url': 'https://www.theverge.com/rss/index.xml',
                           'tags': ''})
    print(db.collection_names(include_system_collections=False))


feed_list = ['http://www.ms.sapientia.ro/hu/hirek?rss&limit=25', 'https://www.reddit.com/r/funny/.rss',
             'https://www.theverge.com/rss/index.xml', 'http://feeds.feedburner.com/d0od',
             'http://feeds.washingtonpost.com/rss/entertainment', 'http://feeds.bbci.co.uk/news/rss.xml?edition=int',
             'http://marosvasarhelyi.info/feed', 'http://marosvasarhelyiradio.ro/feed']
feed_list = []
print('feeds: {0}'.format(len(feed_list)))

entries = []
with futures.ThreadPoolExecutor() as executor:
    future_urls = {executor.submit(feedparser.parse, feed): feed for feed in feed_list}
    for future in futures.as_completed(future_urls):
        url = future_urls[future]
        try:
            feed = future.result()
            # print(feed.entries[0].content)
            entries.extend(feed['items'])
        except Exception as ex:
            print(ex)
        finally:
            print('{0} \t - parsed'.format(url))

# list(map(print, entries))


def parse_result(entry):
    pattern = re.compile('(src=.*)|(img src=.*)')
    tag_list = []
    if 'content' in entry:
        contents = entry['content']
    elif 'media_thumbnail' in entry:
        contents = entry['media_thumbnail']
    else:
        return []
    for tag in contents:
        if 'value' in tag:
            # print(tag['value'])
            href = pattern.search(tag['value'])
            if href:
                tag_list.append(href.group().split('\"'))
        else:
            href = contents[0]['url']
            tag_list.append(href)
            #print(contents)
    return tag_list

'''
metadata = {}
with futures.ProcessPoolExecutor() as executor:
    for entry, tags in zip(entries, executor.map(parse_result, entries)):
        metadata[tags[1]] = tags[2:]
'''

metadata = {}
parsed = []
for entry in entries:
    parsed.extend(parse_result(entry))

for tags in parsed:
    if isinstance(tags, str):
        metadata[tags] = ''
    else:
        metadata[tags[1]] = tags[2:]

# print(len(metadata.keys()))


def download_images():
    img_dir = str(datetime.date.today())
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    os.chdir(img_dir)

    count = 0
    http = urllib3.PoolManager()
    for url in metadata.keys():
        response = http.request('GET', url)
        image_bytes = response.data
        url = url.replace('https://', '').rsplit('/')
        file_name = url[len(url)-1]

        if file_name:
            with open(file_name, 'w+b') as output_f:
                output_f.write(image_bytes)
            print(file_name)
            count += 1

    print('downloaded images: {0}'.format(count))



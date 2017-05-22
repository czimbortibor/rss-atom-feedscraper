import json


def load_feed_list():
    with open('feed_list.json') as feeds_file:
        feeds_data = json.load(feeds_file)

    feed_list = []
    for feed in feeds_data['feeds']:
        feed_list.append(feed['url'])

    print('feed urls: {0}'.format(feed_list))
    return feed_list, feeds_data

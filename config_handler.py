import json
import get_rss_feed


def load_feed_list(feeds_file):
    try:
        with open(feeds_file) as file:
            feeds_data = json.load(file)
    except FileNotFoundError:
        print('Wrong input JSON file of the feed list!')
        return None, None

    feed_list = []
    for feed in feeds_data:
        feed_list.append(feed['url'])

    # print('feed urls: {0}'.format(feed_list))
    return feed_list, feeds_data


def append_feed_list(feeds_file, website_url, tags):
    try:
        with open(feeds_file) as file:
            json_contents = json.load(file)
    except FileNotFoundError:
        print('Wrong input JSON file of the feed list!')
        return

    feed_url = get_rss_feed.get_rss_feed(website_url)
    data = {'url': feed_url, 'tags': tags}

    json_contents.append(data)

    with open(feeds_file, 'w') as file:
        json.dump(json_contents, file)

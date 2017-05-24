import requests
from bs4 import BeautifulSoup


def get_rss_feed(website_url):
    if website_url is None:
        print('The URL should not be null!')
        return None
    else:
        source_code = requests.get(website_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'lxml')
        rss_href = soup.find('link', {'type': 'application/rss+xml'}).get('href')
        return rss_href

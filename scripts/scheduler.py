import sys
import time

import schedule

import rss_atom_scraper


def job():
    print('running the scrape...')
    rss_atom_scraper.main('test.json')


def main(argv=None):
    if len(argv) == 1:
        print('using default 6 minutes interval to run the script')
        run_period = 6
    else:
        run_period = int(argv[1])

    schedule.every(run_period).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv)

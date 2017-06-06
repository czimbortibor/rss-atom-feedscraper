import sys
import time

import schedule

import rss_atom_scraper
from logger import Logger


def job():
    Logger.log('\trunning the scrape...\n')
    rss_atom_scraper.main()


def main(argv):
    if len(argv) == 1:
        Logger.log('using default 30 minute interval to run the script')
        run_period = 30
    else:
        run_period = int(argv[1])
        
    # first run
    job()

    # schedule the next runs
    schedule.every(run_period).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv)

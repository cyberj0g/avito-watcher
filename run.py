import datetime
import argparse
import os
import time
import requests
from scrapy.crawler import CrawlerProcess
import config
import sqlitedict
from analysis import plots
from analysis import utils
import tqdm

from middlewares import aab
from spiders.avito_spider import AvitoSpider
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('./logfile.log'), logging.StreamHandler()])


def crawl(args):
    process = CrawlerProcess(config.as_dict())
    process.crawl(AvitoSpider)
    process.start()


def query_listing(url):
    return requests.get(url, cookies=config.COOKIES, headers={'User-Agent': config.USER_AGENT}, allow_redirects=False)


def check_listings(args, start_time):
    db = sqlitedict.SqliteDict(config.DB_PATH, autocommit=True)
    listings = [(k, f) for k, f in db.iteritems() if f.get('last_updated', datetime.datetime.min) < start_time and not f.get('is_finished') and f.get('start_url') in config.AVITO_URLS.split(';')]
    for key, fields in tqdm.tqdm(listings):
        try:
            res = query_listing(fields['url'])
            if res.status_code == 302 and 'blocked' in res.headers['Location']:
                logger.info('Soft ban, resetting cookies')
                aab.reset_cookies()
                res = query_listing(fields['url'])
            if res.status_code == 302 and 'blocked' not in res.headers['Location']:
                data = db[key]
                data['is_finished'] = True
                data['finished_at'] = datetime.datetime.utcnow()
                db[key] = data
            logger.info(f'Url {fields["url"]} status {res.status_code}')
            blocked = "blocked" in res.headers.get("Location", "")
            if blocked:
                logger.info('Hard ban, giving up')
            time.sleep(0.6)
        except requests.ConnectionError:
            logger.exception('Connection error, skipping')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--crawl', action='store_true', help='Crawl listings')
    ap.add_argument('--check-finished', action='store_true', help='Check if some of not crawled listings from DB are finished')
    ap.add_argument('--plot-prices', action='store_true', help='Display price histogram')
    args = ap.parse_args()
    start_time = datetime.datetime.utcnow()
    if args.crawl:
        logger.info('Crawling data...')
        crawl(args)
    if args.check_finished:
        logger.info('Checking finished listings...')
        check_listings(args, start_time)
    if args.plot_prices:
        logger.info('Displaying price plot...')
        data = utils.load_data()
        plots.plot_prices(data)


if __name__ == '__main__':
    main()

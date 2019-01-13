import logging

from scrapy.exceptions import IgnoreRequest
from six.moves.urllib.parse import urljoin

from w3lib.url import safe_url_string

import time

import config
from selenium import webdriver

logger = logging.getLogger(__name__)


def reset_cookies():
    # get main page executing all scripts to get valid cookies
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(1280, 1024)
    driver.delete_all_cookies()
    res = driver.get('https://www.avito.ru')
    time.sleep(4)
    res = driver.refresh()
    time.sleep(4)
    cookies = driver.get_cookies()
    driver.quit()
    config.COOKIES = dict((i['name'], i['value']) for i in cookies)


class AntiAntiBotMiddleware(object):
    """
    Refresh cookies with headless browser if blocked
    """

    def __init__(self, settings):
        self.max_aab_times = 1

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if response.status == 302:
            location = safe_url_string(response.headers['location'])
            if 'block' in location:
                logger.info('Banned!')
                # blocked, use headless browser to refresh cookies, then try again
                if request.meta.get('max_aab_times', 0) < self.max_aab_times:
                    reset_cookies()
                    retryreq = request.copy()
                    retryreq.cookies = config.COOKIES
                    retryreq.dont_filter = True
                    retryreq.meta['max_aab_times'] = request.meta.get('max_aab_times', 0) + 1
                    return retryreq
                else:
                    logger.info('Giving up')
                    raise IgnoreRequest()
        return response

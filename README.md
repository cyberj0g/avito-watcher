# About
This is a tiny [Avito](https://avito.ru) (a russian craigslist) crawler for personal use, which allows to:
* crawl listings given search results URL
* bypass some of anti-bot protection measures without using proxies
* watch listings finished after the last crawl
* plot prices
* save data to sqlite in no-sql format  

# Installation
1. Navigate to project folder and run
```
sudo apt-get install python3-tk 
pipenv install
cd /tmp
wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
```

# Usage
1. Open [Avito](https://avito.ru) and customize search for your items of interest. Use as specific search parameters as possible to reduce number of results and crawl time.
2. Copy the URL with all search terms to `AVITO_URLS` variable of `config/settings.py`. You can use multiple URLs split by `;`. You can also override any value in `config/settings.py` with environment variable passed to the script.
3. Run the script
    ```
    pipenv run python run.py --crawl --plot-prices
    ```
4. Crawled data is stored in `/data/crawler-db.sqlite`. Use [sqlitedict](https://pypi.org/project/sqlitedict/) to consume it.

# Customization
* The crawler is built with scrapy, it also uses Selenium with Firefox driver to bypass some anti-bot protection measures. Data is stored as a key-value pairs in sqlite database.
* To customize what is crawled from each listings, edit item fields in `spiders/avito_spider.py`
* To change scraping behavior, add or edit any valid scrapy setting in `config/settings.py`. Attention: current values are picked to crawl slowly to not trigger captcha-based anti-bot protection. You can add a list of proxies to make crawling faster. 
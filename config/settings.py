class BaseConfig:
    AVITO_URLS = ''
    DB_PATH = 'data/crawler-db.sqlite'

    # scrapy settings
    USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
    CONCURRENT_REQUESTS_PER_DOMAIN = 1
    CONCURRENT_REQUESTS = 1
    DOWNLOAD_DELAY = 1
    COOKIES = ''
    COOKIES_ENABLED = True
    DOWNLOADER_MIDDLEWARES = {
        'middlewares.aab.AntiAntiBotMiddleware': 700,
    }
    ITEM_PIPELINES = {
        'pipelines.sqlite_pipeline.SqlitePipeline': 300,
    }

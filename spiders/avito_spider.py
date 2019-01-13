import datetime

import scrapy
import config
from scrapy.spiders import Rule
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor


class AvitoSpider(scrapy.Spider):
    name = 'avito.ru'
    allowed_domains = ['avito.ru']
    ru_months = ['января',
                 'февраля'
                 'марта',
                 'апреля',
                 'мая',
                 'июня',
                 'июля',
                 'августа',
                 'сентября',
                 'октября',
                 'ноября',
                 'декабря',
                 ''
                 ]

    def __init__(self, *args, **kwargs):
        super(AvitoSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.settings['AVITO_URLS'].split(';'):
            request = scrapy.Request(url, self.parse, cookies=config.COOKIES)
            request.meta['start_url'] = url
            yield request

    def parse(self, response):
        cookies = {}
        cookies.update(config.COOKIES)
        cookies.update(dict([(v.decode('ascii').split(';')[0].split('=')[0], v.decode('ascii').split(';')[0].split('=')[1]) for v in response.headers.getlist('Set-Cookie')]))
        # parse listings
        for url in response.xpath('//a[@class="item-description-title-link"]/@href').extract():
            yield scrapy.Request(response.urljoin(url), callback=self.parse_item, meta=response.meta, cookies=cookies)
        # navigate pages
        for url in response.xpath('//a[@class="pagination-page"]/@href').extract():
            yield scrapy.Request(response.urljoin(url), meta=response.meta, cookies=cookies)

    @staticmethod
    def parse_publish_date(item_metadata):
        publish_date = None
        if 'сегодня' in item_metadata:
            publish_date = datetime.datetime.utcnow().date()
        elif 'вчера' in item_metadata:
            publish_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
        else:
            for i, m in enumerate(AvitoSpider.ru_months):
                if m in item_metadata:
                    break
            if i < 12:
                month = i + 1
                year = (datetime.datetime.utcnow().year - 1) if month > datetime.datetime.utcnow().month else datetime.datetime.utcnow().year
                day = int(item_metadata.split('размещено')[-1].split()[0])
                publish_date = datetime.datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d')
        return publish_date

    def parse_item(self, response):
        item = AvitoListing()
        item['id'] = response.url.split('/')[-1]
        fields = {}
        fields['title'] = response.xpath('//span[@class="title-info-title-text"]/text()').extract()[0]
        fields['price'] = float(response.xpath('//span[@class="js-item-price"]/text()').extract()[0].replace(' ', ''))
        fields['last_updated'] = datetime.datetime.utcnow()
        fields['url'] = response.url
        fields['start_url'] = response.meta['start_url']
        fields['seller_info_value'] = ' '.join(response.xpath('//div[@class="item-view-seller-info"]//div[@class="seller-info-value"]/text()').extract())
        # parse publish date
        item_metadata = response.xpath('//div[@class="title-info-metadata-item"]/text()').extract()[0]
        fields['publish_date'] = AvitoSpider.parse_publish_date(item_metadata)
        # custom fields
        try:
            fields['lat'] = float(response.xpath('//div[@data-map-lat]/@data-map-lat').extract()[0])
            fields['lon'] = float(response.xpath('//div[@data-map-lon]/@data-map-lon').extract()[0])
        except:
            pass
        item['fields'] = fields
        return item


class AvitoListing(scrapy.Item):
    id = scrapy.Field()
    fields = scrapy.Field()

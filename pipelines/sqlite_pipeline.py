import datetime

from sqlitedict import SqliteDict


class SqlitePipeline(object):

    def __init__(self, db_path):
        self.db_path = db_path

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_path=crawler.settings.get('DB_PATH'),
        )

    def open_spider(self, spider):
        self.db = SqliteDict(self.db_path, autocommit=True)

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        fields = self.db.get(item['id'], {})
        fields.update(item['fields'])
        fields['created_at'] = fields.get('created_at', datetime.datetime.utcnow())
        fields['crawled_times'] = fields.get('crawled_times', 0) + 1
        self.db[item['id']] = fields
        return item

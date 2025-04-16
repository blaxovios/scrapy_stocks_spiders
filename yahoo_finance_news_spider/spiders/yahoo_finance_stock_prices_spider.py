import json
import logging

from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from yahoo_finance_news_spider.items import YahooFinanceStockPricesItem
from yahoo_finance_news_spider.utils import generate_uuid, setup_logging


class YahooFinanceStockPriceSpider(CrawlSpider):
    name = "yahoo_finance_stock_prices_spider"
    allowed_domains = ["finance.yahoo.com"]

    def __init__(self, *args, **kwargs):
        super(YahooFinanceStockPriceSpider, self).__init__(*args, **kwargs)
        with open('data/json/stock_symbols.json') as f:
            stock_symbols = json.load(f)
        self.start_urls = [
            f'https://finance.yahoo.com/quote/{symbol["Symbol"]}/history/?period1=1577836800&period2=1744818085'
            for symbol in stock_symbols
        ]

    rules = [
        Rule(
            LinkExtractor(allow=r'https://finance\.yahoo\.com/quote/[a-zA-Z0-9\-]+/history/\?period1=1577836800&period2=1744818085'),
            callback='parse_link',
            follow=True
        ),
    ]
    
    custom_settings = {
        'FEED_URI': 'data/parquet/scraped_stock_prices_{time}.parquet',
        'FEED_FORMAT': 'parquet',
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YahooFinanceStockPriceSpider, cls).from_crawler(crawler, *args, **kwargs)
        setup_logging(
            debug_filename=crawler.settings.get('LOG_FILE', 'yahoo_finance_stock_prices_spider'),
            console_level=crawler.settings.get('LOG_LEVEL', logging.INFO)
        )
        return spider

    def parse_link(self, response):
        # If flagged as duplicate, skip processing.
        if response.meta.get('duplicate', False):
            self.logger.debug("Skipping duplicate URL: %s", response.url)
            return

        item_loader = ItemLoader(item=YahooFinanceStockPricesItem(), response=response)
        table_container = response.xpath('//div[contains(@class, "table-container")]')
        rows = table_container.xpath('.//tr')

        for row in rows:
            columns = row.xpath('.//td')
            if len(columns) == 7:
                stock_price_date = columns[0].xpath('./text()').get()
                open_price = columns[1].xpath('./text()').get()
                high_price = columns[2].xpath('./text()').get()
                low_price = columns[3].xpath('./text()').get()
                close_price = columns[4].xpath('./text()').get()
                adj_close_price = columns[5].xpath('./text()').get()
                volume = columns[6].xpath('./text()').get()

                item_loader.add_value('stock_price_date', stock_price_date)
                item_loader.add_value('open_price', open_price)
                item_loader.add_value('high_price', high_price)
                item_loader.add_value('low_price', low_price)
                item_loader.add_value('close_price', close_price)
                item_loader.add_value('adj_close_price', adj_close_price)
                item_loader.add_value('volume', volume)

        item = item_loader.load_item()

        scraped_data = {
            'id': generate_uuid(response),
            'url': response.url,
            'stock_price_date': item.get('stock_price_date'),
            'open_price': item.get('open_price'),
            'high_price': item.get('high_price'),
            'low_price': item.get('low_price'),
            'close_price': item.get('close_price'),
            'adj_close_price': item.get('adj_close_price'),
            'volume': item.get('volume'),
        }
        yield scraped_data
import re
import logging
from datetime import datetime

from scrapy.loader import ItemLoader
from itemloaders.processors import Join
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem
from yahoo_finance_news_spider.utils import generate_uuid, setup_logging


class YahooFinanceNewsSpider(CrawlSpider):
    name = "yahoofinance_news"
    allowed_domains = ["finance.yahoo.com"]
    start_urls = ['https://finance.yahoo.com']
    
    # Only extract links that have "/news/" and end with ".html",
    # while denying URLs with unwanted segments.
    rules = [
        Rule(
            LinkExtractor(allow=r'https://finance\.yahoo\.com/news/[a-zA-Z0-9\-]+'),
            callback='parse_link',
            follow=True
        ),
    ]
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YahooFinanceNewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        setup_logging(
            debug_filename=crawler.settings.get('LOG_FILE', 'yahoo_finance_news_spider'),
            console_level=crawler.settings.get('LOG_LEVEL', logging.INFO)
        )
        return spider

    def parse_link(self, response):
        # If flagged as duplicate, skip processing.
        if response.meta.get('duplicate', False):
            self.logger.debug("Skipping duplicate URL: %s", response.url)
            return

        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[contains(@class, "cover-title")]/text()')
        item_loader.add_xpath('content', '//div[contains(@class, "article-wrap")]//p/text()', Join())
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.now().isoformat())

        # Extract stock prices, if available.
        stock_prices = {}
        for fin_streamer in response.xpath('//fin-streamer'):
            symbol = fin_streamer.xpath('./@data-symbol').get()
            value = fin_streamer.xpath('./span/text()').get()
            stock_prices[symbol] = value
        item_loader.add_value('stock_prices', stock_prices)

        item = item_loader.load_item()

        scraped_data = {
            'id': generate_uuid(response),
            'url': item.get('url'),
            'title': item.get('title'),
            'content': item.get('content'),
            'article_date': item.get('article_date'),
            'timestamp': item.get('timestamp'),
            'stock_prices': item.get('stock_prices')
        }
        yield scraped_data
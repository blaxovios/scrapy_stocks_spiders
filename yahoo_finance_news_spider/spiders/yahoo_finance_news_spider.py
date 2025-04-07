from scrapy.loader import ItemLoader
from itemloaders.processors import Join
from scrapy.spiders import (CrawlSpider, Rule)
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import logging
from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem
from yahoo_finance_news_spider.utils import (generate_uuid, setup_logging)


class YahooFinanceNewsSpider(CrawlSpider):
    name = "yahoofinance_news"
    allowed_domains = ["finance.yahoo.com"]
    start_urls = ['https://finance.yahoo.com/']
    
    rules = [
        Rule(
            LinkExtractor(allow=r'https://finance\.yahoo\.com/news/[a-zA-Z0-9\-]+'),
            callback='parse_link',
            follow=True
        ),
    ]
    
    def __init__(self, *args, **kwargs):
        super(YahooFinanceNewsSpider, self).__init__(*args, **kwargs)
        setup_logging(debug_filename=self.settings.get('LOG_FILE', 'yahoo_finance_news_spider'),
                      console_level=self.settings.get('LOG_LEVEL', logging.INFO))

    def parse_link(self, response):
        # If the middleware marked this response as duplicate, do not yield an item.
        if response.meta.get('duplicate', False):
            self.logger.debug("Skipping item yield for duplicate URL: %s", response.url)
            # Return nothing; however, CrawlSpider will still extract links per its rules.
            return

        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[contains(@class, "cover-title")]/text()')
        item_loader.add_xpath('content', '//div[contains(@class, "article-wrap")]//p/text()', Join())
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.now().isoformat())
        stock_prices = {}
        for fin_streamer in response.xpath('//fin-streamer'):
            symbol = fin_streamer.xpath('./@data-symbol').get()
            value = fin_streamer.xpath('./span/text()').get()
            stock_prices[symbol] = value
        item = item_loader.load_item()

        scraped_data = {
            'id': generate_uuid(response),
            'url': item.get('url', None),
            'title': item.get('title', None),
            'content': item.get('content', None),
            'article_date': item.get('article_date', None),
            'timestamp': item.get('timestamp', None),
            'stock_prices': stock_prices
        }
        yield scraped_data
from scrapy.loader import ItemLoader
from itemloaders.processors import Join
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from datetime import datetime
import uuid
from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem


class YahooFinanceNewsSpider(CrawlSpider):
    name = "yahoofinance_news"
    
    start_urls = [
        'https://finance.yahoo.com/',
    ]
    
    rules = [
        Rule(LinkExtractor(allow=r'https://finance\.yahoo\.com/news/[a-zA-Z0-9\-]+'), callback='parse_link', follow=True),
    ]

    def parse_link(self, response):
        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[contains(@class, "cover-title")]/text()')
        item_loader.add_xpath('content', '//div[contains(@class, "article-wrap")]//p/text()', Join())
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.now().isoformat())
        item = item_loader.load_item()

        unique_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url))

        scraped_data = {
            'id': unique_id,
            'url': item.get('url', None),
            'title': item.get('title', None),
            'content': item.get('content', None),
            'article_date': item.get('article_date', None),
            'timestamp': item.get('timestamp', None)
        }

        yield scraped_data


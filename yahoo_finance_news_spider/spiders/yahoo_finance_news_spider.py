from scrapy.loader import ItemLoader
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.http import Request
from datetime import datetime
import uuid
from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem


class YahooFinanceNewsSpider(Spider):
    name = "yahoofinance_news"
    dont_follow = [
        r'https://consent\.yahoo\.com/v2/.*',
    ]
    rules = [
        Rule(LinkExtractor(deny=r'https://consent\.yahoo\.com/v2/.*')),
    ]
    
    def start_requests(self):
        yield Request('https://finance.yahoo.com/news/', meta={'dont_redirect': True})

    def parse(self, response):
        # Extract all links on the page
        links = response.css('a::attr(href)').get()
        for link in links:
            yield response.follow(link, self.parse_link)

    def parse_link(self, response):
        # Extract data from the crawled pages
        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="cover-title"]/text()')
        item_loader.add_xpath('content', '//p[@class="yf-1pe5jgt"]/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.datetime.now().isoformat())
        item = item_loader.load_item()

        # Generate unique ID
        unique_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url))

        # Save scraped data in correct format
        scraped_data = {
            'id': unique_id,
            'url': item['url'],
            'title': item['title'],
            'content': item['content'],
            'article_date': item['article_date'],
            'timestamp': item['timestamp']
        }

        yield scraped_data
from scrapy.loader import ItemLoader
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_playwright.page import PageMethod
from scrapy.http import Request
from datetime import datetime
import uuid
from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem


class YahooFinanceNewsSpider(Spider):
    name = "yahoofinance_news"
    
    start_urls = [
        'https://finance.yahoo.com/',
    ]
    dont_follow = [
        r'https://consent\.yahoo\.com/v2/.*',
        r'https://consent\.yahoo\.com/v2/partners\?sessionId.*',
        r'https://legal\.yahoo\.com/ie/el/yahoo/privacy/index\.html',
    ]
    rules = [
        Rule(LinkExtractor(deny=r'https://consent\.yahoo\.com/v2/.*')),
    ]
    
    def start_requests(self):
        yield Request(
        url=self.start_urls[0],
        # dont_filter=True,
        callback=self.parse,
        meta={
            "dont_proxy": True,  # Disable scrapy-zyte-smartproxy, playwright has separate proxy
            # "dont_redirect": True,
            # "handle_httpstatus_list": [302],  # Disables the redirect middleware for the download
            "playwright": True,  # Use Playwright to execute Javascript
            "playwright_include_page": True,  # The Playwright page that was used to download the request; available in the callback via response.meta['playwright_page'].
            "playwright_context": "default",
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "button[name='agree']", timeout=60000),  # Wait for the consent button to appear
                PageMethod("click", "button[name='agree']", timeout=60000),  # Click the consent button
            ],
            "playwright_redirect": True,  # Enable redirect handling
            "playwright_retries": 0,  # Reset retries to 0
        }
    )

    def parse(self, response):
        # If the consent button was clicked, proceed with the original start_url
        if response.meta.get("playwright_retries") > 0:
            yield Request(
                url=self.start_urls[0],
                callback=self.parse,
                meta={
                    "dont_proxy": True,
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "default",
                    "playwright_retries": 0,  # Reset retries to 0
                }
            )
        else:
            links = response.css('a::attr(href)').getall()
            for link in links:
                yield response.follow(link, self.parse_link)

    def parse_link(self, response):
        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="cover-title"]/text()')
        item_loader.add_xpath('content', '//p[@class="yf-1pe5jgt"]/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.now().isoformat())
        item = item_loader.load_item()

        unique_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url))

        scraped_data = {
            'id': unique_id,
            'url': item['url'],
            'title': item['title'],
            'content': item['content'],
            'article_date': item['article_date'],
            'timestamp': item['timestamp']
        }

        yield scraped_data

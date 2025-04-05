import os
import polars as pl
from scrapy.exceptions import IgnoreRequest
from scrapy.loader import ItemLoader
from itemloaders.processors import Join
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from yahoo_finance_news_spider.items import YahooFinanceNewsSpiderItem
from yahoo_finance_news_spider.utils import generate_uuid


class YahooFinanceNewsSpider(CrawlSpider):
    name = "yahoofinance_news"
    allowed_domains = ["finance.yahoo.com"]
    start_urls = [
        'https://finance.yahoo.com/',
    ]
    rules = [
        Rule(
            LinkExtractor(allow=r'https://finance\.yahoo\.com/news/[a-zA-Z0-9\-]+'),
            callback='parse_link',
            follow=True
        ),
    ]

    def __init__(self, *args, **kwargs):
        super(YahooFinanceNewsSpider, self).__init__(*args, **kwargs)
        self.scraped_urls = set()
        self.skipped_urls = 0
        self.load_scraped_urls()

    def load_scraped_urls(self):
        """Reads existing parquet files and logs & collects all scraped URLs."""
        parquet_dir = 'data/parquet'
        if not os.path.exists(parquet_dir):
            self.logger.info("Parquet directory does not exist: %s", parquet_dir)
            return

        parquet_files = [f for f in os.listdir(parquet_dir) if f.endswith('.parquet')]
        for file in parquet_files:
            file_path = os.path.join(parquet_dir, file)
            try:
                # Read only the 'url' column
                df = pl.read_parquet(file_path, columns=['url'])
                urls = df['url'].to_list()
                self.logger.info("Loaded URLs from %s: %s", file, urls)
                # Add each URL to the scraped_urls set
                for url in urls:
                    # In case the column is stored as a list per row, iterate over its elements
                    if isinstance(url, list):
                        for u in url:
                            self.scraped_urls.add(u)
                    else:
                        self.scraped_urls.add(url)
            except Exception as e:
                self.logger.error("Error reading file %s: %s", file, e)
        self.logger.info("Total scraped URLs loaded: %d", len(self.scraped_urls))

    def make_requests_from_url(self, url):
        # Check if the initial URL has already been scraped.
        if url in self.scraped_urls:
            self.skipped_urls += 1
            self.logger.info("Skipping start URL (already scraped): %s", url)
            raise IgnoreRequest(f"Skipping {url} as it has already been scraped")
        return super().make_requests_from_url(url)

    def _requests_to_follow(self, response):
        # Filter out links that have already been scraped.
        for request in super()._requests_to_follow(response):
            if request.url in self.scraped_urls:
                self.skipped_urls += 1
                self.logger.info("Skipping discovered URL (already scraped): %s", request.url)
                continue
            yield request

    def parse_link(self, response):
        item_loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        item_loader.add_xpath('title', '//div[contains(@class, "cover-title")]/text()')
        item_loader.add_xpath('content', '//div[contains(@class, "article-wrap")]//p/text()', Join())
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('article_date', '//time/@datetime')
        item_loader.add_value('timestamp', datetime.now().isoformat())
        item = item_loader.load_item()

        scraped_data = {
            'id': generate_uuid(response),
            'url': item.get('url', None),
            'title': item.get('title', None),
            'content': item.get('content', None),
            'article_date': item.get('article_date', None),
            'timestamp': item.get('timestamp', None)
        }

        yield scraped_data

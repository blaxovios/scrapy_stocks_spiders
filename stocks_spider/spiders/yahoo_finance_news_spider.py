import os
import logging
from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings
from itemloaders.processors import Join

from stocks_spider.items import YahooFinanceNewsSpiderItem
from stocks_spider.utils import generate_uuid


class YahooFinanceNewsSpider(CrawlSpider):
    name = "yahoo_finance_news_spider"
    allowed_domains = ["finance.yahoo.com"]
    start_urls = ["https://finance.yahoo.com"]

    # Only follow news links, run parse_link on each
    rules = [
        Rule(
            LinkExtractor(allow=r"https://finance\.yahoo\.com/news/[A-Za-z0-9\-]+"),
            callback="parse_link",
            follow=True,
        ),
    ]

    # pull in our global settings
    _settings = get_project_settings()
    custom_settings = {
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            _settings["FEED_URI_TEMPLATE"]: {
                **_settings["FEEDS_DEFAULT_CONFIG"],
                "batch_item_count": 100,
                "format": "parquet",
            }
        },
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        # ensure logs/ exists
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # timestamped logfile name
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"{spider.name}_{ts}.log")

        # create & attach FileHandler to root logger
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(crawler.settings.get("LOG_LEVEL"))
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        ))
        root = logging.getLogger()
        root.setLevel(crawler.settings.get("LOG_LEVEL"))
        root.addHandler(fh)

        return spider

    def parse_link(self, response):
        # skip duplicates flagged by your middleware
        if response.meta.get("duplicate"):
            self.logger.info(f"Skipping already-scraped URL: {response.url}")
            return

        loader = ItemLoader(item=YahooFinanceNewsSpiderItem(), response=response)
        loader.add_xpath("title", '//div[contains(@class, "cover-title")]/text()')
        loader.add_xpath(
            "content", 
            '//div[contains(@class, "article-wrap")]//p/text()',
            Join()
        )
        loader.add_value("url", response.url)
        loader.add_xpath("article_date", "//time/@datetime")
        loader.add_value("timestamp", datetime.now().isoformat())

        # collect in-page stock prices
        stock_prices = {}
        for fs in response.xpath("//fin-streamer"):
            sym = fs.xpath("./@data-symbol").get()
            val = fs.xpath("./span/text()").get()
            if sym and val:
                stock_prices[sym] = val
        loader.add_value("stock_prices", stock_prices)

        item = loader.load_item()
        yield {
            "id": generate_uuid(response),
            "url": item["url"],
            "title": item["title"],
            "content": item["content"],
            "article_date": item["article_date"],
            "timestamp": item["timestamp"],
            "stock_prices": item["stock_prices"],
        }
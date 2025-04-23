import os
import json
import logging
from datetime import datetime, timezone

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

from stocks_spider.items import YahooFinanceStockPricesItem
from stocks_spider.utils import generate_uuid


class YahooFinanceStockPriceSpider(scrapy.Spider):
    name = "yahoo_finance_stock_prices_spider"
    allowed_domains = ["finance.yahoo.com"]

    _settings = get_project_settings()
    custom_settings = {
        # parquet feeds in batches
        "FEEDS": {
            _settings["FEED_URI_TEMPLATE"]: {
                **_settings["FEEDS_DEFAULT_CONFIG"],
                "batch_item_count": 10_000,
            }
        },

        # shared browser‐like headers
        "DEFAULT_REQUEST_HEADERS": _settings["DEFAULT_REQUEST_HEADERS"],

        # Playwright on only here
        "DOWNLOAD_HANDLERS": _settings["DOWNLOAD_HANDLERS"],
        "PLAYWRIGHT_BROWSER_TYPE": _settings["PLAYWRIGHT_BROWSER_TYPE"],
        "PLAYWRIGHT_CONTEXTS": _settings["PLAYWRIGHT_CONTEXTS"],
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": _settings["PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT"],
        # (we now rely on the global PLAYWRIGHT_ABORT_REQUEST)
    }
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        # ensure logs/ exists
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # build a timestamped filename
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(logs_dir, f"{spider.name}_{ts}.log")

        # create & configure the handler
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(crawler.settings.get("LOG_LEVEL"))
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        ))

        # attach immediately so we catch *all* logs
        root = logging.getLogger()
        root.setLevel(crawler.settings.get("LOG_LEVEL"))
        root.addHandler(fh)

        return spider

    HISTORY_URL = "https://finance.yahoo.com/quote/{symbol}/history/"

    def start_requests(self):
        # keep this snippet handy for switching back to JSON
        with open('data/json/stock_symbols.json') as f:
            stock_symbols = json.load(f)
        # stock_symbols = [{"Symbol": "NVDA"}]

        headers = self.settings.get("DEFAULT_REQUEST_HEADERS")
        for s in stock_symbols:
            url = self.HISTORY_URL.format(symbol=s["Symbol"]) + \
                  "?period1=1577836800&period2=1744818085"

            yield scrapy.Request(
                url=url,
                callback=self.parse_history,
                headers=headers,
                meta={
                    "symbol": s["Symbol"],
                    "playwright": True,
                    "playwright_context": "default",
                },
                errback=self.on_error,
                priority=10,
                dont_filter=True,
            )

    def on_error(self, failure):
        self.logger.error("Request failed: %s", failure.request.url)

    def parse_history(self, response):
        symbol = response.meta["symbol"]
        rows = response.xpath('//div[contains(@class, "table-container")]//tr')

        for row in rows:
            cols = row.xpath('.//td')
            if len(cols) != 7:
                continue

            loader = ItemLoader(
                item=YahooFinanceStockPricesItem(),
                selector=row,
                response=response
            )

            loader.add_value('id', generate_uuid(response))
            loader.add_value('url', response.url)
            loader.add_value('symbol', symbol)
            loader.add_value('timestamp', datetime.now(timezone.utc))

            loader.add_xpath('stock_price_date',   './td[1]//text()')
            loader.add_xpath('open_price',         './td[2]//text()')
            loader.add_xpath('high_price',         './td[3]//text()')
            loader.add_xpath('low_price',          './td[4]//text()')
            loader.add_xpath('close_price',        './td[5]//text()')
            loader.add_xpath('adj_close_price',    './td[6]//text()')
            loader.add_xpath('volume',             './td[7]//text()')

            yield loader.load_item()
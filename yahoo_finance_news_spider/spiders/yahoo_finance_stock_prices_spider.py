import json
import logging
from datetime import datetime, timezone
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

from yahoo_finance_news_spider.items import YahooFinanceStockPricesItem
from yahoo_finance_news_spider.utils import generate_uuid, setup_logging


class YahooFinanceStockPriceSpider(scrapy.Spider):
    name = "yahoo_finance_stock_prices_spider"
    allowed_domains = ["finance.yahoo.com"]

    custom_settings = {
        'FEED_URI': 'data/parquet/scraped_stock_prices_{time}.parquet',
        'FEED_FORMAT': 'parquet',
        'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    }
    
    # only allow requests whose URL matches our history‐page pattern
    HISTORY_RE = re.compile(r"^https://finance\.yahoo\.com/quote/[^/]+/history/")
    
    def route(self, route, request):
        if self.HISTORY_RE.match(request.url):
            return route.continue_()
        return route.abort()

    def start_requests(self):
        settings = get_project_settings()
        default_headers = settings.getdict('DEFAULT_REQUEST_HEADERS')

        with open('data/json/stock_symbols.json') as f:
            stock_symbols = json.load(f)

        for symbol in stock_symbols:
            url = (
                f'https://finance.yahoo.com/quote/{symbol["Symbol"]}/'
                f'history/?period1=1577836800&period2=1744818085'
            )
            yield scrapy.Request(
                url=url,
                callback=self.parse_history,
                headers=default_headers,
                meta={
                    "symbol": symbol["Symbol"],
                    "playwright": True,
                    "playwright_context": "default"
                },
                errback=self.on_error,
                priority=10,
                dont_filter=True,
            )

    def on_error(self, failure):
        self.logger.error("Request failed: %s", failure.request.url)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        setup_logging(
            debug_filename=crawler.settings.get('LOG_FILE', spider.name),
            console_level=crawler.settings.get('LOG_LEVEL', logging.INFO)
        )
        return spider

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

            # static fields
            loader.add_value('id', generate_uuid(response))
            loader.add_value('url', response.url)
            loader.add_value('symbol', symbol)
            loader.add_value('timestamp', datetime.now(timezone.utc))

            # per‑column fields via XPath
            loader.add_xpath('stock_price_date', './td[1]//text()')
            loader.add_xpath('open_price', './td[2]//text()')
            loader.add_xpath('high_price', './td[3]//text()')
            loader.add_xpath('low_price', './td[4]//text()')
            loader.add_xpath('close_price', './td[5]//text()')
            loader.add_xpath('adj_close_price', './td[6]//text()')
            loader.add_xpath('volume', './td[7]//text()')

            yield loader.load_item()
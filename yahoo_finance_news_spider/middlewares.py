from os import path, listdir
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import polars as pl
# Import local modules
from yahoo_finance_news_spider.utils import normalize_url


class YahooFinanceNewsSpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    async def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        async for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class YahooFinanceNewsSpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        try:
            return super().process_response(request, response, spider)
        except ValueError as e:
            spider.logger.error("Caught ValueError in process_response: %s", e)
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, ValueError):
            spider.logger.error("Caught ValueError in process_exception: %s", exception)
            reason = str(exception)
            return self._retry(request, reason, spider)


class DuplicateUrlFilterMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        middleware.scraped_urls = set()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        """Load and log scraped URLs from existing parquet files in 'data/parquet' dir."""
        parquet_dir = 'data/parquet'
        if not path.exists(parquet_dir):
            spider.logger.debug("Parquet directory does not exist: %s", parquet_dir)
            return

        try:
            # Read only the 'url' column from all parquet files
            dfs = []
            for file in listdir(parquet_dir):
                if file.endswith(".parquet"):
                    df = pl.read_parquet(path.join(parquet_dir, file), columns=['url'])
                    dfs.append(df)
            df = pl.concat(dfs)
            urls = df['url'].to_list()
            spider.logger.debug("Loaded URLs from %s: %s", parquet_dir, urls)
            for url in urls:
                if isinstance(url, list):
                    for u in url:
                        self.scraped_urls.add(normalize_url(u))
                else:
                    self.scraped_urls.add(normalize_url(url))
        except Exception as e:
            spider.logger.error("Error reading files in %s: %s", parquet_dir, e)
        spider.logger.debug("Total scraped URLs loaded: %d", len(self.scraped_urls))

    def process_request(self, request, spider):
        """
        For every outgoing request (except for start_urls and dont_filter requests), check if the
        normalized URL is in the scraped set. If so, mark it as duplicate.
        """
        # Allow requests flagged to bypass filtering.
        if request.meta.get("dont_filter", False):
            return None

        # Always allow start_urls to be processed.
        if request.url in spider.start_urls:
            return None

        normalized = normalize_url(request.url)
        if normalized in self.scraped_urls:
            spider.logger.debug("Marking URL as duplicate (already scraped): %s", request.url)
            request.meta['duplicate'] = True
        return None

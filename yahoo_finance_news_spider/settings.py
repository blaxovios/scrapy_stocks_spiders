# Scrapy settings for yahoo_finance_news_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "yahoo_finance_news_spider"

SPIDER_MODULES = ["yahoo_finance_news_spider.spiders"]
NEWSPIDER_MODULE = "yahoo_finance_news_spider.spiders"

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 400, 403, 404]
LOG_LEVEL='DEBUG'
LOG_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "yahoo_finance_news_spider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5  # If Set to 0, I get 404 and spider shuts down early.
RANDOMIZE_DOWNLOAD_DELAY = False
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Add more user agents here...
]

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept-Language': 'en-US,en;q=0.5',
  'Referer': 'https://finance.yahoo.com/',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "yahoo_finance_news_spider.middlewares.YahooFinanceNewsSpiderSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "yahoo_finance_news_spider.middlewares.YahooFinanceNewsSpiderDownloaderMiddleware": 543,
#}
DOWNLOADER_MIDDLEWARES = {
    "yahoo_finance_news_spider.middlewares.YahooFinanceNewsSpiderDownloaderMiddleware": 543,
    "yahoo_finance_news_spider.middlewares.DuplicateUrlFilterMiddleware": 545,
    # Keep your custom retry middleware if applicable
    # "yahoo_finance_news_spider.middlewares.CustomRetryMiddleware": 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "yahoo_finance_news_spider.pipelines.YahooFinanceNewsSpiderPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = False
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = CONCURRENT_REQUESTS
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEED_FORMAT = 'parquet'
FEEDS = {
    'data/parquet/scraped_data_{time}.parquet': {
        'format': 'parquet',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,
        'item_export_kwargs': {
            'include_headers': True,
        },
    },
    'data/parquet/scraped_stock_prices_{time}.parquet': {
        'format': 'parquet',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,
        'item_export_kwargs': {
            'include_headers': True,
        },
    },
}
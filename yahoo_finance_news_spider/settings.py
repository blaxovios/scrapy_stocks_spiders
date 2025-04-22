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
LOG_LEVEL='INFO'
LOG_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "yahoo_finance_news_spider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 128

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0  # If Set to 0, I get 404 and spider shuts down early.
RANDOMIZE_DOWNLOAD_DELAY = False
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

#USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",

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

# ----------------------------------------
# PLAYWRIGHT SETTINGS
# ----------------------------------------
DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# The browser type to be launched, e.g. chromium, firefox, webkit.
PLAYWRIGHT_BROWSER_TYPE = "chromium"

# A dictionary with options to be passed as keyword arguments when launching the Browser.
# See https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
PLAYWRIGHT_LAUNCH_OPTIONS = {
    # "headless": False,
    "timeout": 60000.0 * 3,  # 10 minutes to wait for the browser instance to start
}

# A dictionary which defines Browser contexts to be created on startup. It should be a mapping of (name, keyword arguments).
# See https://playwright.dev/python/docs/api/class-browser#browser-new-context
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "ignore_https_errors": True,
        "java_script_enabled": False,
    },
}

# Maximum amount of allowed concurrent Playwright contexts. If unset or None, no limit is enforced.
# See https://github.com/scrapy-plugins/scrapy-playwright#maximum-concurrent-context-count
#PLAYWRIGHT_MAX_CONTEXTS = 8

# A predicate function (or the path to a function) that receives a playwright.async_api.Request object and must return True if the request should be aborted, False otherwise.
PLAYWRIGHT_ABORT_REQUEST = lambda req: req.resource_type == "image" or "GetFile" in req.url

# Timeout to be used when requesting pages by Playwright. If None or unset, the default value will be used (30000 ms at the time of writing this).
# See https://playwright.dev/python/docs/api/class-browsercontext#browser-context-set-default-navigation-timeout
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000.0 * 3  # 10 minutes, should be overkill

# Maximum amount of allowed concurrent Playwright pages for each context; defaults to the value of Scrapy's CONCURRENT_REQUESTS setting
# See https://github.com/scrapy-plugins/scrapy-playwright#receiving-page-objects-in-callbacks
#PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = CONCURRENT_REQUESTS

# To handle media redirections (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/media-pipeline.html#allowing-redirections
MEDIA_ALLOW_REDIRECTS = False
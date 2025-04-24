import os

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------
LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_ENABLED = True
LOG_LEVEL = "INFO"
LOG_STDOUT = True   # Captures python stdout/stderr into the log

BOT_NAME = "stocks_spider"
SPIDER_MODULES = ["stocks_spider.spiders"]
NEWSPIDER_MODULE = "stocks_spider.spiders.yahoo_finance_news_spider"
STOCKS_SPIDER_MODULE = "stocks_spider.spiders.yahoo_finance_stock_prices_spider"


# -------------------------------------------------------------------
# RETRY
# -------------------------------------------------------------------
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 400, 403, 404]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5  # If Set to 0, I get 404 and spider shuts down early.
RANDOMIZE_DOWNLOAD_DELAY = False
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# -------------------------------------------------------------------
# COMMON DEFAULT REQUEST HEADERS
# -------------------------------------------------------------------

USER_AGENT = "Chrome/51.0.2704.64"
# these will be applied unless a spider overrides or extends them
DEFAULT_REQUEST_HEADERS = {
    # emulate a real browser
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://finance.yahoo.com/",
}

# -------------------------------------------------------------------
# MIDDLEWARES
# -------------------------------------------------------------------

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    f"{BOT_NAME}.middlewares.PersistentDuplicateFilterMiddleware": 700,
}


# -------------------------------------------------------------------
# DEDUPLICATION
# -------------------------------------------------------------------

DUPLICATE_FILTER_DIR = os.path.join(os.getcwd(), "data", "parquet")
DUPLICATE_FILTER_FIELD = "url"

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
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

# -------------------------------------------------------------------
# FEED EXPORT TEMPLATE
# -------------------------------------------------------------------

# a URI template: %(name)s → spider.name   %(time)s → ISO8601 timestamp
FEED_URI_TEMPLATE = "data/parquet/%(name)s/scraped_%(name)s_%(time)s_%(batch_id)d.parquet"
# the common feed‐export options for all spiders
FEEDS_DEFAULT_CONFIG = {
    "format": "parquet",
    "encoding": "utf8",
    "store_empty": True,
    "fields": None,
    "item_export_kwargs": {
        "include_headers": True,
    },
    "compression": "snappy",
}
FEEDS = {
    FEED_URI_TEMPLATE: {
        **FEEDS_DEFAULT_CONFIG,
        "batch_item_count": 1_000,
        "format": "parquet",      # your custom format
    }
}
FEED_EXPORTERS = {
    "parquet": f"{BOT_NAME}.exporters.PolarsParquetItemExporter",
}

# -------------------------------------------------------------------
# PLAYWRIGHT, MIDDLEWARES, ETC.
# -------------------------------------------------------------------

DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "timeout": 60000.0 * 3,  # 10 minutes
}
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "ignore_https_errors": True,
        "java_script_enabled": False,
    },
}
# only let the main HTML document load; kill everything else
PLAYWRIGHT_ABORT_REQUEST = lambda request: request.resource_type != "document"

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000.0 * 3

MEDIA_ALLOW_REDIRECTS = False
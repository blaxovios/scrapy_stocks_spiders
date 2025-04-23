from pathlib import Path
import logging
import polars as pl

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.defaultheaders import DefaultHeadersMiddleware as _DFH
from scrapy.utils.project import get_project_settings

from stocks_spider.utils import normalize_url


class PersistentDuplicateFilterMiddleware:
    """
    Prevents re-scraping items whose identifying field (default 'url')
    already exists in any valid Parquet file under DUPLICATE_FILTER_DIR.
    """

    @classmethod
    def from_crawler(cls, crawler):
        settings    = crawler.settings
        parquet_dir = settings.get("DUPLICATE_FILTER_DIR")
        field       = settings.get("DUPLICATE_FILTER_FIELD", "url")
        if not parquet_dir:
            raise NotConfigured("DUPLICATE_FILTER_DIR is not set")

        mw = cls(parquet_dir=parquet_dir, field=field)
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def __init__(self, parquet_dir: str, field: str):
        self.parquet_dir = Path(parquet_dir)
        self.field       = field
        self.seen        = set()
        self.logger      = logging.getLogger(self.__class__.__name__)

    def spider_opened(self, spider):
        if not self.parquet_dir.exists():
            self.logger.debug("Parquet dir %s does not exist, skipping load", self.parquet_dir)
            return

        files = list(self.parquet_dir.glob("**/*.parquet"))
        if not files:
            self.logger.debug("No .parquet files found under %s", self.parquet_dir)
            return

        dfs = []
        for fp in files:
            size = fp.stat().st_size
            if size < 12:
                self.logger.debug("Skipping invalid/parital parquet file %s (size %d bytes)", fp, size)
                continue
            try:
                df = pl.read_parquet(str(fp), columns=[self.field])
                dfs.append(df)
            except Exception as e:
                self.logger.error("Failed to read %s: %s", fp, e)
                continue

        if not dfs:
            self.logger.debug("No valid parquet data loaded from %s", self.parquet_dir)
            return

        all_df = pl.concat(dfs, how="vertical")
        # iterate values via to_list()
        for val in all_df[self.field].to_list():
            if isinstance(val, list):
                for v in val:
                    self.seen.add(normalize_url(v))
            else:
                self.seen.add(normalize_url(val))

        self.logger.info("Loaded %d seen %r values from %d files",
                         len(self.seen), self.field, len(dfs))

    def process_request(self, request, spider):
        # bypass if explicitly told so
        if request.meta.get("dont_filter"):
            return
        norm = normalize_url(request.url)
        if norm in self.seen:
            spider.logger.debug("Skipping already-seen URL: %s", request.url)
            request.meta["duplicate"] = True
        return


class DefaultHeadersMiddleware(_DFH):
    """
    Extends the builtin DefaultHeadersMiddleware to also inject USER_AGENT
    from settings into the headers dict, so you no longer need the
    separate UserAgentMiddleware.
    """
    def __init__(self, settings=None):
        # settings can be either passed by Scrapy or fetched here
        s = settings or get_project_settings()
        default_headers = s.getdict("DEFAULT_REQUEST_HEADERS")
        ua = s.get("USER_AGENT")
        if ua:
            default_headers["User-Agent"] = ua
        # initialize the parent with our merged headers
        super().__init__(default_headers)

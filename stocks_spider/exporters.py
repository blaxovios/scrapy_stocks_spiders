# yahoo_finance_news_spider/exporters.py
import polars as pl
from scrapy.exporters import BaseItemExporter


class PolarsParquetItemExporter(BaseItemExporter):
    """
    Collect items, then write them to Parquet via Polars.lazy().sink_parquet().
    Strips out any unsupported feed-export options like include_headers.
    """
    def __init__(self, file, **kwargs):
        # Drop feed-export options BaseItemExporter doesn’t expect
        
        for unsupported in (
            "include_headers",      # from item_export_kwargs
            "indent",               # if you passed it
            "fields",               # if you passed it
            "encoding",             # etc.
        ):
            kwargs.pop(unsupported, None)

        super().__init__(**kwargs)
        self._file = file
        self._rows = []

    def export_item(self, item):
        self._rows.append(dict(item))

    def finish_exporting(self):
        if not self._rows:
            return
        # build a LazyFrame and write parquet
        pl.DataFrame(self._rows).lazy().sink_parquet(self._file)
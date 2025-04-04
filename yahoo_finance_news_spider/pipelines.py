import os
import polars as pl
import datetime

class YahooFinanceNewsSpiderPipeline:
    def __init__(self):
        self.file_path = 'data/parquet/'
        self.items = []
        self.file_count = 0

    def process_item(self, item, spider):
        self.items.append(dict(item))
        if len(self.items) >= 100:
            self._append_to_parquet()
            self.items = []
            self.file_count += 1
        return item

    def close_spider(self, spider):
        if self.items:
            self._append_to_parquet()

    def _append_to_parquet(self):
        lf = pl.LazyFrame(self.items)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = f'scraped_data_{self.file_count:03d}_{timestamp}.parquet'
        file_path = os.path.join(self.file_path, file_name)
        os.makedirs(self.file_path, exist_ok=True)
        lf.sink_parquet(file_path)
import polars as pl
import os


class YahooFinanceNewsSpiderPipeline:
    def __init__(self):
        self.file_path = 'scraped_data.parquet'
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))
        if len(self.items) >= 10:
            self._append_to_parquet()
            self.items = []
        return item

    def close_spider(self, spider):
        if self.items:
            self._append_to_parquet()

    def _append_to_parquet(self):
        df = pl.DataFrame(self.items)
        if not os.path.exists(self.file_path):
            df.write_parquet(self.file_path)
        else:
            existing_df = pl.read_parquet(self.file_path)
            df = pl.concat([existing_df, df])
            df.write_parquet(self.file_path)
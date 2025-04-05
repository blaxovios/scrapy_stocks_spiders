import os
import polars as pl
import datetime
import asyncio

class YahooFinanceNewsSpiderPipeline:
    def __init__(self):
        self.file_path = 'data/parquet/'
        self.items = []
        self.file_count = 0
        self.lock = asyncio.Lock()

    async def process_item(self, item, spider):
        async with self.lock:
            self.items.append(dict(item))
            if len(self.items) >= 100:
                await self._append_to_parquet()
                self.items = []
                self.file_count += 1
        return item

    async def close_spider(self, spider):
        async with self.lock:
            if self.items:
                await self._append_to_parquet()

    async def _append_to_parquet(self):
        lf = pl.LazyFrame(self.items)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = f'scraped_data_{self.file_count:03d}_{timestamp}.parquet'
        file_path = os.path.join(self.file_path, file_name)
        os.makedirs(self.file_path, exist_ok=True)
        await asyncio.to_thread(lf.sink_parquet, file_path)
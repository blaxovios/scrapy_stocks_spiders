# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item
from itemloaders.processors import TakeFirst


class YahooFinanceNewsSpiderItem(Item):
    id = Field(output_processor=TakeFirst(), default="")
    url = Field(output_processor=TakeFirst(), default="")
    title = Field(output_processor=TakeFirst(), default="")
    content = Field(output_processor=TakeFirst(), default="")
    article_date = Field(output_processor=TakeFirst(), default=None)
    timestamp = Field(output_processor=TakeFirst(), default=None)
    stock_prices = Field(output_processor=TakeFirst(), default={})
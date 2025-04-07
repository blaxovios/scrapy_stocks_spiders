# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item
from itemloaders.processors import TakeFirst


class YahooFinanceNewsSpiderItem(Item):
    id = Field(output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    title = Field(output_processor=TakeFirst())
    content = Field(output_processor=TakeFirst())
    article_date = Field(output_processor=TakeFirst())
    timestamp = Field(output_processor=TakeFirst())
    stock_prices = Field()
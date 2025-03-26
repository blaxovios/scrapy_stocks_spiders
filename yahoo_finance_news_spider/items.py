# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class YahooFinanceNewsSpiderItem(Item):
    id = Field()
    url = Field()
    title = Field()
    content = Field()
    article_date = Field()
    timestamp = Field()

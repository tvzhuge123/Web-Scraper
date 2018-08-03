# Author: Yan Zhang
import scrapy


class WikiScraperItem(scrapy.Item):
    depth = scrapy.Field()  # number of http requests made
    status = scrapy.Field() # status of current process
    visited_list = scrapy.Field() # list of visited pages
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class JobbotItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    company_name = scrapy.Field()


class SearchItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    location = scrapy.Field()

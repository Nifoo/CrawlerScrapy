# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    urlObjId = scrapy.Field()
    coverImgUrl = scrapy.Field()
    coverImagFilePath = scrapy.Field()
    thumbUp = scrapy.Field()
    favNum = scrapy.Field()
    commentNum = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class WeibocommentItem(scrapy.Item):

    collection = table = 'weibo_comment'
    user_name = Field()
    comment = Field()
    date = Field()
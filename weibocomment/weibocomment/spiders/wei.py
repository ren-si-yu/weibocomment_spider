# -*- coding: utf-8 -*-
import re
from urllib.parse import quote

import scrapy
from pyquery import PyQuery as pq
from scrapy import Request

from weibocomment.items import WeibocommentItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['s.weibo.com']
    base_url = 'https://s.weibo.com/weibo?q='

    def start_requests(self):

        for keyword in self.settings.get('KEYWORD'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                # 这里先不设置page
                # 因为还不确定下一页还存不存在
                print('page=' + str(page) + '#' * 20)
                url = self.base_url + keyword + '&page='+str(page)
                yield Request(url=url,
                              headers=self.settings.get(
                                  'DEFAULT_REQUEST_HEADERS'),
                              callback=self.parse,
                              meta={
                                  'page': page,
                                  'max_page': self.settings.get('MAX_PAGE') + 1
                              })

    def parse(self, response):

        resp = response.css('.card-wrap .card .card-feed .content').extract()

        # 此处有坑 其中热门文章的标签也是card-wrap，因为不需要，所以要删除。否则报错

        for item_ in resp:
            item_doc = pq(pq(item_).html())
            item = WeibocommentItem()

            if not item_doc('[node-type=feed_list_content_full]').text() == '':
                if not item_doc('.wbicon').text() == '':
                    item_doc('.wbicon').parent().remove()
                html_comment = pq(
                    item_doc(
                        '[node-type=feed_list_content_full]').html()).text()
                pattern_object = re.compile('#(.*?)#')
                comment = pattern_object.sub('', html_comment)
                item['comment'] = comment
            else:
                if not item_doc('.wbicon').text() == '':
                    item_doc('.wbicon').parent().remove()
                html_comment = pq(
                    item_doc(
                        '[node-type=feed_list_content]').html()).text()
                pattern_object = re.compile('#(.*?)#')
                comment = pattern_object.sub('', html_comment)
                item['comment'] = comment

            item['user_name'] = item_doc('.name').attr('nick-name')
            item['date'] = pq(item_doc.find('.from').html()).text()

            yield item

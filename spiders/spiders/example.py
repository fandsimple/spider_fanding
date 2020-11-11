# -*- coding: utf-8 -*-
import logging
import pdb
from spiders.spiders.base import BaseSpider


class ExampleSpider(BaseSpider):
    name = 'baidu'
    allowed_domains = ['baidu.com']
    start_urls = ['https://www.baidu.com']
    parsePage = 'first'

    def first(self, response):
        pdb.set_trace()
        itemInfoList = []

        url = response.xpath('//title/text()').extract()[0]

        urlInfo = {
            'itemType':'url',
            'parsePage':'second',
            'metaInfo': {"name":'fanding'},
            'item':'http://49.233.143.57/',
            'dont_filter':True,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def second(self, response):
        pdb.set_trace()
        pass


# 运行命令：scrapy crawl baidu -a taskType='spider' -a taskId=1

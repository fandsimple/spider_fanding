# -*- coding: utf-8 -*-

import scrapy


# 日志信息
class LogItem(scrapy.Item):
    itemType = 'log'
    logDetail = scrapy.Field()
    taskId = scrapy.Field()
    level = scrapy.Field()
    ip = scrapy.Field()
    url = scrapy.Field()
    spiderName = scrapy.Field()


class BugInfoItem(scrapy.Item):
    itemType = 'bugInfo'
    title = scrapy.Field()
    description = scrapy.Field()
    sourceBulletinUrl = scrapy.Field()
    cveCode = scrapy.Field()
    score = scrapy.Field()
    detailUrl = scrapy.Field()
    releaseTime = scrapy.Field()
    dataSource = scrapy.Field()


class FileDownloadItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()

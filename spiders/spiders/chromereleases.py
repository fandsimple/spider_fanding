# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json
import scrapy

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class ChromereleasesSpider(BaseSpider):
    name = 'chromereleases'
    allowed_domains = ['googleblog.com']
    start_urls = ['https://chromereleases.googleblog.com/']
    parsePage = 'getList'
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数

        cveItemInfoList = response.xpath('//div[@id="Blog1"]/div[@itemtype]')
        for i, cveItemSel in enumerate(cveItemInfoList):
            detailUrl = cveItemSel.xpath('./h2/a/@href').extract()[0]
            pubTime = cveItemSel.xpath('.//div[@class="published"]/span/text()').extract()[0].strip()
            if self.pageCount == 1 and i == 0:  # 记录当天最新数据
                self.today_latest_item_data = {
                    'url': detailUrl,
                    'pubTime': pubTime
                }
                logging.info('lastest data is %s' % json.dumps(self.today_latest_item_data))

            if detailUrl == self.latestDataInfo.get('url') and pubTime == self.latestDataInfo.get(
                    'pubTime'):  # 根据时间和url进行判断是否为新数据
                logging.info('find history data, stop spider')
                self.resInfo['endInfo'] = 'find history data, stop spider'
                break

            urlInfo = {
                'itemType': TYPE_URL,
                'parsePage': 'getCveItemInfo',
                'metaInfo': metaInfo,
                'item': detailUrl,
            }
            itemInfoList.append(urlInfo)

        else:
            # next page
            nextPageUrl = response.xpath('//a[@class="blog-pager-older-link"]/@href').extract()[0]
            urlInfo = {
                'itemType': TYPE_URL,
                'parsePage': 'getList',
                'metaInfo': metaInfo,
                'item': nextPageUrl,
            }
            if self.pageCount < self.maxPageCount:  # 防止出错停止不了
                itemInfoList.append(urlInfo)
            else:
                logging.info('stop spider mandatory, spider page count is %d' % self.maxPageCount)
        return itemInfoList

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        descriptionStrList = response.xpath('//div[@class="post-body"]//script/text()').extract()
        descStr = ''.join(descriptionStrList)
        contentSel = scrapy.Selector(text=descStr)
        description = ''.join(contentSel.xpath('.//text()').extract()).strip()

        item = {}
        item['cveDesc'] = description
        item['cveSource'] = 'GOOGLE'
        item['cveItemTitle'] = response.xpath('//h2[@class="title"]/a/text()').extract()[0].strip()
        item['cveItemUrl'] = response.url
        item['pubTime'] = self.parseTime(response.xpath('//span[@class="publishdate"]/text()').extract()[0].strip())
        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        monthDict = {'January': '1',
                     'February': '2',
                     'March': '3',
                     'April': '4',
                     'May': '5',
                     'June': '6',
                     'July': '7',
                     'August': '8',
                     'September': '9',
                     'October': '10',
                     'November': '11',
                     'December': '12'
                     }
        timeStrList = timeStr.split(',')[1:]
        year = timeStrList[1].strip()
        day = timeStrList[0].strip().split(' ')[1]
        month = monthDict.get(timeStrList[0].strip().split(' ')[0].strip())
        timeStr = '%s-%s-%s' % (year, month, day)
        return timeStr


# 运行命令：scrapy crawl chromereleases -a taskType=spider -a taskId=1 -o data.csv
# 部分抓取：scrapy crawl chromereleases -a taskType=update -a taskId=1 -a sourceUrls=[\"https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/\"]
# 调试：scrapy crawl chromereleases -a taskType=update -a spiderType=test  -a taskId=1 -a sourceUrls=[\"https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/\"]

'''

https://chromereleases.googleblog.com/2020/10/stable-channel-update-for-desktop.html


https://chromereleases.googleblog.com/2020/09/stable-channel-update-for-desktop_21.html

'''

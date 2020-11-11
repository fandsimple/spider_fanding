# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.spiders.base import BaseSpider


class PacketstormsecuritySpider(BaseSpider):
    name = 'packetstormsecurity'
    allowed_domains = ['packetstormsecurity.com']
    start_urls = ['https://packetstormsecurity.com/files/page1/']
    parsePage = 'getList'
    visit_page_count = 0

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数
        detailInfoList = response.xpath('//div[@id="m"]/dl')
        for item_index, detailInfo in enumerate(detailInfoList):
            itemUrl = response.urljoin(detailInfo.xpath('./dt/a/@href').extract()[0]).strip()
            pubTime = detailInfo.xpath('./dd[@class="datetime"]/a/text()').extract()[0].strip()
            if self.pageCount == 1 and item_index == 0:  # 记录当天最新数据
                self.today_latest_item_data = {
                    'url': itemUrl,
                    'pubTime': pubTime
                }
                logging.info('lastest data is %s' % json.dumps(self.today_latest_item_data))

            if itemUrl == self.latestDataInfo.get('url') and pubTime == self.latestDataInfo.get(
                    'pubTime'):  # 根据时间和url进行判断是否为新数据
                logging.info('find history data, stop spider')
                self.resInfo['endInfo'] = 'find history data, stop spider'
                break

            urlInfo = {
                'itemType': TYPE_URL,
                'parsePage': 'getCveItemInfo',
                'metaInfo': metaInfo,
                'item': itemUrl,
            }
            itemInfoList.append(urlInfo)
        else:
            # 翻页操作
            nextPageUrl = response.urljoin(response.xpath('//a[contains(text(), "Next")]/@href').extract()[0])
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
        itemInfoList = []
        itemTitle = response.xpath('//div[@id="m"]/div[@class="h1"][1]/h1/text()').extract()[0].strip()
        # author = response.xpath('//a[@class="person"]/text()').extract()[0].strip()
        author = response.xpath('//dd[@class="refer"]/a[1]/text()').extract()[0].strip()
        source = 'PACKET_STORM'
        sourceId = 'PACKET_STORM-' + response.url.split('files/')[1].split('/')[0].strip()
        pubTime = self.parseTime(response.xpath('//dd[@class="datetime"]/a/text()').extract()[0].strip())
        itemUrl = response.url
        cveCodeUrlList = response.xpath('//dd[@class="cve"]/a/@href').extract()

        item = {}
        item['cveItemUrl'] = itemUrl
        item['cveItemTitle'] = itemTitle
        item['author'] = author
        item['pubTime'] = pubTime
        item['cveSource'] = source
        item['sourceId'] = sourceId
        if not cveCodeUrlList:
            logging.info('no cveCode')
            item['cveDesc'] = response.xpath('//dd[@class="detail"]/p/text()').extract()[0].strip()
            item['cveCode'] = ''
            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': item,
            }
            itemInfoList.append(urlInfo)

        cveCodeUrlResList = []
        for cveCodeUrl in cveCodeUrlList:
            cveCodeUrlResList.append(response.urljoin(cveCodeUrl))

        for url in cveCodeUrlResList:
            urlInfo = {
                'itemType': TYPE_URL,
                'parsePage': 'parseDes',
                'metaInfo': {'item': item},
                'item': url,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList

    def parseDes(self, response):
        logging.info('start parseDes')
        itemInfoList = []
        metaInfo = response.meta.get('metaInfo')
        item = metaInfo.get('item')
        desc = response.xpath('//div[@id="cve-detail"]/text()').extract()[0]
        item['cveDesc'] = desc
        item['cveCode'] = response.url.split('/')[-1]

        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStrList = [i.strip(',') for i in timeStr.split(' ') if i]
        monthDict = {
            'Jan': '1',
            'Feb': '2',
            'Mar': '3',
            'Apr': '4',
            'May': '5',
            'Jun': '6',
            'Jul': '7',
            'Aug': '8',
            'Sep': '9',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12',
        }
        timeStr = '%s-%s-%s' % (timeStrList[2], monthDict.get(timeStrList[0]), timeStrList[1])
        return timeStr

# 运行命令：scrapy crawl packetstormsecurity -a taskType=spider -a taskId=1
# 单条抓取命令：scrapy crawl packetstormsecurity -a taskType=update -a taskId=1 -a sourceUrls=[\"https://packetstormsecurity.com/files/159452/Ubuntu-Security-Notice-USN-4563-1.html\"]

'''

没有cvecode的情况:https://packetstormsecurity.com/files/159723/TDM-Digital-Signage-PC-Player-4.1-Insecure-File-Permissions.html
'''

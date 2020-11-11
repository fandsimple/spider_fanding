# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class IBMSpider(BaseSpider):
    name = 'ibm'
    allowed_domains = ['ibm.com']
    start_urls = ['https://www.ibm.com/blogs/psirt/']
    # start_urls = ['https://www.ibm.com/blogs/psirt/page/10/']
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

        cveItemInfoList = response.xpath(
            "//div[@id='story-space ibm-padding-top-2']/div[@class='ibm-col-6-4']/div[contains(@class,'ibm-columns')]")
        for i, cveItemSel in enumerate(cveItemInfoList):
            detailUrl = cveItemSel.xpath(".//h4/a[contains(@class, 'ibm-blog__header-link')]/@href").extract()[0]
            pubTime = cveItemSel.xpath(".//h4[contains(text(), 'EDT')]/text()").extract()[0].replace('|', '').strip()
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
            nextPageUrl = response.xpath('//a[contains(@class, "ibm-next-link")]/@href').extract()[0]
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
        # parse title
        title = response.xpath('//h1/text()').extract()[0]
        title = title.strip().split(':')[-1].strip()
        # parse detailUrl
        sourceBulletinUrl = response.url
        # parse release time
        releaseTime = response.xpath('//p[contains(@class,"ibm-date-time")]/text()').extract()[0].strip()
        # data source
        dataSource = 'IBM'
        # 详情链接
        detailUrl = response.xpath(
            '//div[@class="ibm-blog__article-main"]/p[contains(text(), "Source Bulletin")]/a/@href').extract()[0]

        metaInfo['title'] = title
        metaInfo['detailUrl'] = detailUrl
        metaInfo['releaseTime'] = releaseTime
        metaInfo['dataSource'] = dataSource
        metaInfo['sourceBulletinUrl'] = sourceBulletinUrl

        urlInfo = {
            'itemType': TYPE_URL,
            'parsePage': 'parseCveExtInfo',
            'metaInfo': metaInfo,
            'item': detailUrl,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseCveExtInfo(self, response):
        logging.info('start parseCveExtInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []

        description = response.xpath('//div[contains(@class, "field--name-field-summary")]/p/text()').extract()[
            0].strip()

        try:
            allInfoStr = \
                response.xpath('//div[contains(@class, "field--name-field-vulnerability-details")]/div').extract()[
                    0]
            allInfoStrList = re.split('<br>\s*?<br>', allInfoStr)
        except:
            allInfoStrSelList = \
                response.xpath('//div[contains(@class, "field--name-field-vulnerability-details")]/p').extract()
            for allInfoStrSel in allInfoStrSelList:
                if "DESCRIPTION" in allInfoStrSel:
                    allInfoStr = allInfoStrSel
                    break
            allInfoStrList = re.split('<br>\s*?<br>', allInfoStr)

        for info in allInfoStrList:
            item = {}
            cveCode = ''
            score = re.findall('CVSS Base score:(.*?)<br', info)[0].strip()
            cveCodeList = re.findall('<a.*?>(.*?)</a>', info)

            description = re.findall('DESCRIPTION:(.*?)<br', info,re.DOTALL)[0].strip().replace('</b>', '')
            for cveCodeInfo in cveCodeList:
                if 'CVE' in cveCodeInfo:
                    cveCode = cveCodeInfo.strip()
            item['cveDesc'] = description
            item['cveCode'] = cveCode
            item['cveScore'] = score
            item['cveItemTitle'] = metaInfo['title']
            item['pubTime'] = self.parseTime(metaInfo['releaseTime'])
            item['cveSource'] = metaInfo['dataSource']
            item['cveItemUrl'] = metaInfo['sourceBulletinUrl']

            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': item,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStrList = timeStr.split(' ')[0:3]
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
        timeStr = '%s-%s-%s' % (timeStrList[2].strip(','), monthDict[timeStrList[0]], timeStrList[1].strip(','))
        return timeStr


# 运行命令：scrapy crawl ibm -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl ibm -a taskType=update -a taskId=1 -a spiderType=test -a sourceUrls=[\"https://www.ibm.com/blogs/psirt/security-bulletin-rational-build-forge-security-advisory-for-apache-http-server/\"]

'''

'''
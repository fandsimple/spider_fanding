# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.spiders.base import BaseSpider


class CxsecuritySpider(BaseSpider):
    name = 'cxsecurity'
    allowed_domains = ['cxsecurity.com']
    start_urls = ['https://cxsecurity.com/exploit']
    parsePage = 'getList'
    currentPage = 1

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数
        cveItemInfoList= response.xpath('//table[@class="table table-striped table-hover "]/tbody/tr')
        for i, cveItemSel in enumerate(cveItemInfoList):
            detailUrl = cveItemSel.xpath('.//h6/a/@href').extract()[0]
            if self.pageCount == 1 and i == 0:  # 记录当天最新数据
                self.today_latest_item_data = {
                    'url': detailUrl,
                }
                logging.info('lastest data is %s' % json.dumps(self.today_latest_item_data))

            if detailUrl == self.latestDataInfo.get('url'):  # 根据url进行判断是否为新数据
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
            self.currentPage += 1
            nextPageUrl = 'https://cxsecurity.com/exploit/%d' % self.currentPage
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

        # parse title
        title = response.xpath('//h4/b/text()').extract()[0].strip()
        # parse detailUrl
        author = ''
        cweIds = ''
        cveCode = ''
        releaseTime = ''
        divSelList = response.xpath('//div[@class="row"]//b/..')
        for i, divSel in enumerate(divSelList):
            key = divSel.xpath('./u/text()').extract()
            if key:
                if key[0].strip() == 'Credit:':
                    author = divSel.xpath('.//a/text()').extract()[0].strip()
                elif key[0].strip() == 'CWE:':
                    cweIds = divSel.xpath('./b/text()').extract()[0].strip()
                    if not cweIds:
                        cweIds = divSel.xpath('./b/a/text()').extract()[0].strip()
                elif key[0].strip() == 'CVE:':
                    cveCode = divSel.xpath('./b/text()').extract()
                    if cveCode:
                        cveCode = cveCode[0].strip()
                    else:
                        cveCode = divSel.xpath('./b/a/text()').extract()[0].strip()
            else:
                if i == 0:
                    releaseTime = divSel.xpath('./b/text()').extract()[0].strip()

        # data source
        dataSource = 'CXSECURITY'
        if cveCode == 'N/A':
            cveCode = ''
        if cweIds == 'N/A' or cweIds == 'NVD-CWE-noinfo':
            cweIds = ''


        item = {}
        item['cveDesc'] = title
        item['cveSource'] = dataSource
        item['cveItemTitle'] =title
        item['pubTime'] = releaseTime.replace('.', '-')
        item['cveItemUrl'] = response.url
        item['cveCode'] = cveCode
        item['author'] = author
        item['cweIds'] = cweIds
        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

# 运行命令：scrapy crawl cxsecurity -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl cxsecurity -a taskType=update -a taskId=1 -a spiderType=test -a sourceUrls=[\"https://cxsecurity.com/issue/WLB-2020080098\"]

'''
有cve情况：https://cxsecurity.com/issue/WLB-2019040193
'''
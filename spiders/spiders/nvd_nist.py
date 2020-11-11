# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class NvdSpider(BaseSpider):
    name = 'nvd_nist'
    allowed_domains = ['nvd.nist.gov']
    start_urls = ['https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&search_type=all']
    parsePage = 'getList'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数
        logging.info('current page is %d' % self.pageCount)
        cveItemSelList = response.xpath('//div[@id="row"]/table/tbody/tr')
        for itemIdex, cveItemSel in enumerate(cveItemSelList):
            cveItemUrl = response.urljoin(cveItemSel.xpath("./th//a/@href").extract()[0])
            pubTime = cveItemSel.xpath("./td[1]/span[@data-testid]/text()").extract()[0].strip()
            if self.pageCount == 1 and itemIdex == 0:  # 记录当天最新数据
                self.today_latest_item_data = {
                    'url': cveItemUrl,
                    'pubTime': pubTime
                }
                logging.info('lastest data is %s' % json.dumps(self.today_latest_item_data))
            if cveItemUrl == self.latestDataInfo.get('url') and pubTime == self.latestDataInfo.get(
                    'pubTime'):  # 根据时间和url进行判断是否为新数据
                logging.info('find history data, stop spider')
                self.resInfo['endInfo'] = 'find history data, stop spider'
                break

            urlInfo = {
                'itemType': TYPE_URL,
                'parsePage': 'getCveItemInfo',
                'metaInfo': metaInfo,
                'item': cveItemUrl,
            }
            itemInfoList.append(urlInfo)
        else:
            # next page
            nextPageUrl = response.urljoin(
                response.xpath('//a[@data-testid="pagination-link-page->"]/@href').extract()[0])
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
        cveCode = response.xpath(
            '//div[@class="bs-callout bs-callout-info"]/a[@data-testid="vuln-cve-dictionary-entry"]/text()').extract()[
            0].strip()
        pubTime = response.xpath(
            '//div[@class="bs-callout bs-callout-info"]/span[@data-testid="vuln-published-on"]/text()').extract()[
            0].strip()
        cveUpdateTime = response.xpath(
            '//div[@class="bs-callout bs-callout-info"]/span[@data-testid="vuln-last-modified-on"]/text()').extract()[
            0].strip()
        cveItemDesc = response.xpath('//p[@data-testid="vuln-description"]/text()').extract()[0].strip()
        cveScore = ''

        # 解析cveScore
        cveScoreSelList = response.xpath('//div[@id="Vuln3CvssPanel"]/div[contains(@class, "row")]')
        for cveScoreSel in cveScoreSelList:
            cveScoreList = cveScoreSel.xpath('.//span[@class="severityDetail"]/a/text()').extract()
            if 'N/A' not in cveScoreList:
                cveScore = cveScoreList[0].strip().split(' ')[0]

        # 解析cwe
        cweIdList = []
        cweSelList = response.xpath('//div[@id="vulnTechnicalDetailsDiv"]/table/tbody/tr')
        for cweSel in cweSelList:
            cweId = cweSel.xpath('./td/a/text()').extract()
            if cweId: # 会出现无效的cwe
                cweId = cweId[0].strip()
                cweIdList.append(cweId)
        cweIds = ','.join(cweIdList)

        cveSource = 'NVD'
        cveItemUrl = response.url

        item = {}
        item['cveDesc'] = cveItemDesc
        item['cveCode'] = cveCode
        item['cveScore'] = cveScore
        item['cveSource'] = cveSource
        item['cveItemUrl'] = cveItemUrl
        item['cweIds'] = cweIds
        item['pubTime'] = self.parseTime(pubTime)
        item['cveUpdateTime'] = self.parseTime(cveUpdateTime)

        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStrList = timeStr.split('/')
        timeStr = '%d-%d-%d' % (int(timeStrList[2]), int(timeStrList[0]), int(timeStrList[1]))
        return timeStr



# 运行命令：scrapy crawl nvd_nist -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl nvd_nist -a taskType='update' -a taskId=1 -a sourceUrls='["https://nvd.nist.gov/vuln/detail/CVE-2020-15371"]'

'''
最新数据：
{"url":"https://nvd.nist.gov/vuln/detail/CVE-2020-15216","pubTime":"September 29, 2020; 12:15:11 PM -0400"}

'''
# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider
import copy


class JvndbSpider(BaseSpider):
    name = 'jvndb'
    allowed_domains = ['jvn.jp']
    start_urls = ['https://jvndb.jvn.jp/en/']
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

        cveItemInfoList = response.xpath('//ul[contains(@class,"news-list")]/li[not(@class="header")]')
        for cve_index, cveItemSel in enumerate(cveItemInfoList):
            cveItemUrl = response.urljoin(cveItemSel.xpath("./a/@href").extract()[0])
            pubTime = cveItemSel.xpath('./a/div[@class="date"]/text()').extract()[0]
            # cveScore = cveItemSel.xpath('.//div[@class="severity"]/div/text()').extract()[0].split('(')[0].strip()
            metaData = copy.deepcopy(metaInfo)
            # metaData['pubTime'] = pubTime
            # metaData['cveScore'] = cveScore

            if self.pageCount == 1 and cve_index == 0:  # 记录当天最新数据
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
                'metaInfo': metaData,
                'item': cveItemUrl,
            }
            itemInfoList.append(urlInfo)

            # 测试打开
            break
        # todo 翻页待做 目前不确定情况
        # else:
        #     # next page
        #     nextPageUrl = response.xpath('//a[contains(@class, "ibm-next-link")]/@href').extract()[0]
        #     urlInfo = {
        #         'itemType': TYPE_URL,
        #         'parsePage': 'getList',
        #         'metaInfo': metaInfo,
        #         'item': nextPageUrl,
        #     }
        #     if self.pageCount < self.maxPageCount:  # 防止出错停止不了
        #         itemInfoList.append(urlInfo)
        #     else:
        #         logging.info('stop spider mandatory, spider page count is %d' % self.maxPageCount)

        return itemInfoList

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        pdb.set_trace()

        if metaInfo.get('cveScore').strip() == '-':
            metaInfo['cveScore'] = ''

        # trSelList = response.xpath('//table[@class="vuln_table_clase"]//tr')
        # parse title
        title = response.xpath('//tr/td/h2/text()').extract()[0].strip()
        # parse cveItemUrl
        cveItemUrl = response.url
        # parse release time
        releaseTime = self.parseTime(metaInfo.get('pubTime'))

        # 解析更新时间
        lastUpdateTime = response.xpath('//div[@class="modifytxt"]/text()').extract()[0]

        # data source
        dataSource = 'JVN'



        # parse all cveCode
        allCveCodeList = response.xpath(
            '//table[@class="vuln_table_clase"]//tr//a[contains(text(), "What is CVE?")]/../../following-sibling::tr[1]//ol/li/a/text()').extract()
        parseCveCodeList = []  # 从描述中解析出来的cveCode

        if not allCveCodeList:  # 没有cveCode情况
            infoStrList = response.xpath(
                '//table[@class="vuln_table_clase"]//tr//a[@name="overview"]/../../following-sibling::tr[1]//blockquote//text()').extract()
            cveItem = {}
            cveItem['cveItemTitle'] = title
            cveItem['cveItemUrl'] = cveItemUrl
            cveItem['pubTime'] = releaseTime
            cveItem['cveSource'] = dataSource
            cveItem['cveDesc'] = ''.join(infoStrList)
            cveItem['cveScore'] = metaInfo.get('cveScore')
            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': cveItem,
            }
            itemInfoList.append(urlInfo)

        # parse cveCode and cweId
        infoStrList = response.xpath(
            '//table[@class="vuln_table_clase"]//tr//a[@name="overview"]/../../following-sibling::tr[1]//blockquote//text()').extract()
        for infoStr in infoStrList:  # cwe与cve一一对应情况
            infoStr = infoStr.strip()
            if infoStr.startswith('*'):
                cweIds = '~'.join(re.findall('CWE-\d+', infoStr))
                cveCode = re.findall('CVE-\d+-\d+', infoStr)
                if cveCode:
                    cveCode = cveCode[0]
                    cveItem = {}
                    cveItem['cveItemTitle'] = title
                    cveItem['cveItemUrl'] = cveItemUrl
                    cveItem['pubTime'] = releaseTime
                    cveItem['cveSource'] = dataSource
                    cveItem['cweIds'] = cweIds
                    cveItem['cveCode'] = cveCode
                    cveItem['cveDesc'] = ''.join(infoStrList)
                    cveItem['cveScore'] = metaInfo.get('cveScore')
                    urlInfo = {
                        'itemType': TYPE_ITEM,
                        'item': cveItem,
                    }
                    itemInfoList.append(urlInfo)
                    parseCveCodeList.append(cveCode)

        # 做cveCode是否解析完全
        for cveCodeTem in allCveCodeList:
            if cveCodeTem not in parseCveCodeList:
                cveItem = {}
                cveItem['cveItemTitle'] = title
                cveItem['cveItemUrl'] = cveItemUrl
                cveItem['pubTime'] = releaseTime
                cveItem['cveSource'] = dataSource
                cveItem['cveCode'] = cveCodeTem
                cveItem['cveDesc'] = ''.join(infoStrList)
                cveItem['cveScore'] = metaInfo.get('cveScore')
                urlInfo = {
                    'itemType': TYPE_ITEM,
                    'item': cveItem,
                }
                itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStrList = timeStr.split('/')
        timeStr = '%d-%d-%d' % (int(timeStrList[0]), int(timeStrList[1]), int(timeStrList[2]))
        return timeStr


# 运行命令：scrapy crawl jvndb -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl jvndb -a taskType='update' -a taskId=1 -a sourceUrls='["https://jvndb.jvn.jp/en/contents/2020/JVNDB-2020-000064.html"]'


'''

https://jvndb.jvn.jp/search/index.php?mode=_vulnerability_search_IA_VulnSearch&lang=en&datePublicFromMonth=08&datePublicFromYear=2020&dateLastPublishedFromMonth=08&dateLastPublishedFromYear=2020



特殊情况网址：
https://jvndb.jvn.jp/en/contents/2020/JVNDB-2020-000062.html
https://jvndb.jvn.jp/en/contents/2020/JVNDB-2020-006617.html

'''



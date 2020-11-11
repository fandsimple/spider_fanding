# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json
import copy

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class AuscertSpider(BaseSpider):
    name = 'auscert'
    allowed_domains = ['auscert.org.au']
    start_urls = ['https://www.auscert.org.au/bulletins/']
    # start_urls = ['https://www.auscert.org.au/bulletins/?page=7']
    parsePage = 'getList'
    handle_httpstatus_list = [403]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数
        logging.info('current page is %d' % self.pageCount)

        cveItemInfoList = response.xpath('//div[@class="security_bulletins_block"]/div')
        for cve_index, cveItemSel in enumerate(cveItemInfoList):
            cveItemUrl = response.urljoin(cveItemSel.xpath("./@href").extract()[0])
            pubTime = cveItemSel.xpath('.//p[@class="date uppercase"]/text()').extract()[0].strip()
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
                'metaInfo': metaInfo,
                'item': cveItemUrl,
            }
            itemInfoList.append(urlInfo)

            # # 测试打开
            # break
        else:
            # next page
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
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        except_code = [403]
        if response.status in except_code:  # 数据访问异常（锁住了，不让访问 vip）
            logging.info('The data is not access')
            return

        cveSourceCode = response.xpath('//h2[@class="subtitle"]/text()').extract()[0].strip()
        cveTitle = response.xpath('//h1[@class="title"]/text()').extract()[0].strip()
        cveItemUrl = response.url
        # 解析cve编号
        infoStrAll = response.xpath('//pre/text()').extract()[0]
        infoStr = re.findall('AusCERT Security Bulletin Summary(.*?)BEGIN INCLUDED TEXT', infoStrAll, re.DOTALL)[0]

        # 受影响产品
        affected_product = re.findall('Product:(.*?)Publisher', infoStr, re.DOTALL)[0].strip()
        affected_product_list = re.split('\n', affected_product)
        affected_product = ','.join(affected_product_list)
        # 作者
        author = re.findall('Publisher:(.*?)Operating System', infoStr, re.DOTALL)[0].strip()
        # 受影响系统
        affected_system = re.findall('Operating System:(.*?)Impact/Access', infoStr, re.DOTALL)[0].strip()
        # 影响
        affection = re.findall('Impact/Access:(.*?)Resolution:', infoStr, re.DOTALL)[0].strip()
        # 漏洞原文
        desc = re.findall('BEGIN INCLUDED TEXT(.*?)END INCLUDED TEXT', infoStrAll, re.DOTALL)[0].strip().replace(
            '-----',
            '')
        # 原始公告链接
        announcementSource = re.findall('Original Bulletin:(.*?)BEGIN INCLUD', infoStrAll, re.DOTALL)[0].strip()
        announcementSource = [url.strip() for url in announcementSource.split('\n') if url.strip().startswith('http')]
        announcementSource = '*'.join(announcementSource)
        # 发布时间
        pubTime = response.xpath('//div[@class="bulletin_description"]/p[@class="description"]/text()').extract()[
            0].strip()

        # allCveList = re.findall('CVE Names:(.*)?Reference', infoStr, re.DOTALL)

        # allCveStr = re.findall('CVE Names:(.*?)Reference', infoStr, re.DOTALL)
        # allCveStr = re.findall('CVE Names:(.*)', infoStr, re.DOTALL)[0]
        allCveStr = re.findall('CVE Names:(.*)', infoStr, re.DOTALL)
        if allCveStr:  # 有cve编号情况
            allCveStr = allCveStr[0].split('CVE Names:')[0].replace('\n', '')
            allCveStr = re.sub('Reference:.*', '', allCveStr)
            allCveStr = re.sub('Original.*', '', allCveStr)
            allCveStr = allCveStr.strip().replace('CVE', '~CVE')
            allCveCodeList = allCveStr.split('~')
            allCveCodeList = [cveCode for cveCode in allCveCodeList if cveCode]

            # allCveStr = allCveStr[0].strip()
            # allCveCodeList = re.split('\s+', allCveStr)
        else:  # 没有cve编号情况
            allCveCodeList = []

        item = {}
        item['cveDesc'] = desc
        item['cveItemTitle'] = cveTitle
        item['cveItemUrl'] = cveItemUrl
        item['pubTime'] = self.parseTime(pubTime)
        item['referenceLink'] = announcementSource
        item['cveSource'] = 'AUSCERT'
        item['sourceId'] = cveSourceCode
        item['affectedProduct'] = affected_product
        item['author'] = author
        # item['sourceId'] = response.xpath('//h2[@class="subtitle"]/text()').extract()[0].strip()

        # item['affectedSystem'] = affected_system
        # item['affection'] = affection

        if allCveCodeList:
            for cveCode in allCveCodeList:
                cveItem = copy.deepcopy(item)
                cveItem['cveCode'] = cveCode.strip()
                urlInfo = {
                    'itemType': TYPE_ITEM,
                    'item': cveItem,
                }
                itemInfoList.append(urlInfo)
        else:
            cveItem = copy.deepcopy(item)
            cveItem['cveCode'] = ''
            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': cveItem,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStrList = timeStr.split(' ')
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
        timeStr = '%s-%s-%s' % (timeStrList[2], monthDict[timeStrList[1]], timeStrList[0])
        return timeStr


# 运行命令：scrapy crawl auscert -a taskType=spider -a taskId=1 -o data.csv
# 部分抓取：scrapy crawl auscert -a taskType=update -a taskId=1 -a sourceUrls=[\"https://www.auscert.org.au/bulletins/ESB-2020.3307.2/\"]
# 调试：scrapy crawl auscert -a taskType=update -a taskId=1 -a spiderType=test -a sourceUrls=[\"https://www.auscert.org.au/bulletins/ESB-2020.3713/\"]

'''
最新数据：
{"url":"https://www.auscert.org.au/bulletins/ESB-2020.3343/","pubTime":"29 September 2020"}
'''

'''
跟踪特殊数据：ASB-2020.0197，ASB-2020.0196  -----10.23号数据，可用如下链接直接访问，https://www.auscert.org.au/bulletins/ASB-2020.0192/

'''

'''
{'January':'',
'February':'',
'March':'',
'April':'',
'May':'',
'June':'',
'July':'',
'August':'',
'September':'',
'October':'',
'November':'',
'December':''
}


'''

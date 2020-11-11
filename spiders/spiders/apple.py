# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json
import scrapy

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class AppleSpider(BaseSpider):
    name = 'apple'
    allowed_domains = ['apple.com']
    start_urls = ['https://support.apple.com/en-us/HT201222']
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

        cveItemInfoList = response.xpath('//div[@id="tableWraper"]/table/tbody/tr')[1:-1]
        for i, cveItemSel in enumerate(cveItemInfoList):
            detailUrl = cveItemSel.xpath("./td[1]/a/@href").extract()
            if not detailUrl:
                logging.info('第%d条数据没有详情链接' % (i + 1))
                continue
            detailUrl = detailUrl[0].strip()
            pubTime = cveItemSel.xpath("./td[3]/text()").extract()[0].strip()
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
            # # 测试
            break
        return itemInfoList

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        # parse title
        affect_os = response.xpath('//div[@id="sections"]/div[3]/h2/text()').extract()[0]
        # parse detailUrl
        sourceBulletinUrl = response.url
        dataSource = 'APPLE'

        pubTime = response.xpath('//div[@id="sections"]/div[3]/div/p[1]/span/text()').extract()[0].strip()
        desc = ''
        contentSelList = response.xpath('//div[@id="sections"]/div[3]/div/p')[1:-1]
        contentSelStr = response.xpath('//div[@id="sections"]/div[3]/div').extract()[0]
        infoList = re.split('<strong>.*</strong>', contentSelStr)[1:]
        componentsLis = re.findall('<strong>(.*)</strong>', contentSelStr)
        resInfoList = zip(componentsLis, infoList)
        for component, infStr in resInfoList:
            infStrList = re.sub('<.*?>', '', infStr).strip().split('\n')
            for infStr in infStrList:
                if infStr.startswith('CVE'):  # 构建cve漏洞信息
                    cveCode = infStr.split(':')[0]
                    item = {}
                    item['cveCode'] = cveCode
                    item['pubTime'] = self.parseTime(pubTime)
                    item['cveSource'] = dataSource
                    item['cveItemUrl'] = sourceBulletinUrl
                    item['cveDesc'] = affect_os + ' ' + component + ' ' + desc
                    urlInfo = {
                        'itemType': TYPE_ITEM,
                        'item': item,
                    }
                    itemInfoList.append(urlInfo)
                else:
                    desc += ' ' + infStr
            else:
                desc = ''
        return itemInfoList

    def parseTime(self, timeStr):
        if '发布于' in timeStr:
            timeStr = timeStr.replace('发布于', '').strip()
            year, resStr = timeStr.split('年')[0].strip(), timeStr.split('年')[1].strip()
            month, resStr = resStr.split('月')[0].strip(), resStr.split('月')[1].strip()
            day = resStr.split('日')[0].strip()
            timeStr = '%s-%s-%s' % (year, month, day)
        else:
            timeStr = timeStr.replace('Released', '').strip()
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
            timeStr = '%s-%s-%s' % (timeStrList[2].strip(','), monthDict[timeStrList[0].strip()], timeStrList[1].strip(','))
        return timeStr


# 运行命令：scrapy crawl apple -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl apple -a taskType=update -a taskId=1 -a sourceUrls=[\"https://support.apple.com/zh-cn/HT211294\"]

'''
一个条目下多个cve情况：https://support.apple.com/zh-cn/HT211294
常规：https://support.apple.com/zh-cn/HT211928
'''

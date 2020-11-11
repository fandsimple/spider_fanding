# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM, TYPE_REQUEST
from spiders.spiders.base import BaseSpider


class Nsfocuspider(BaseSpider):
    name = 'nsfocus'
    allowed_domains = ['nsfocus.net']
    start_urls = ['http://www.nsfocus.net/index.php?act=sec_bug']
    parsePage = 'getList'
    maxPageCount = 5

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        self.pageCount += 1  # 统计页数

        cveItemInfoList = response.xpath('//div[@class="vulbar"]/ul/li')
        for i, cveItemSel in enumerate(cveItemInfoList):
            detailUrl = response.urljoin(cveItemSel.xpath(".//a/@href").extract()[0].strip())
            pubTime = cveItemSel.xpath("./span/text()").extract()[0].strip()
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
            nextPageUrl = response.urljoin(response.xpath('//a[@title="Next"]/@href').extract()[0])
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
        title = response.xpath('//div[@align="center"]/b/text()').extract()[0].strip()
        # parse detailUrl
        sourceBulletinUrl = response.url

        dataInfoStr = response.xpath('//div[@class="vulbar"]').extract()[0]
        # parse release time
        releaseTime = re.findall('发布日期：</b>(\d+-\d+-\d+?)<br>', dataInfoStr, re.DOTALL)[0].strip()
        updateTime = re.findall('更新日期：</b>(\d+-\d+-\d+?)<br>', dataInfoStr, re.DOTALL)[0].strip()
        # data source
        dataSource = 'NSFOCUS'

        # 解析受影响产品
        affect_system_list = re.findall('受影响系统：</b><blockquote>(.*?)</blockquote>', dataInfoStr, re.DOTALL)[0].replace(
            '<br>', '').split('\n')
        affect_system = ','.join(affect_system_list).replace('&lt;', '<')
        # 描述
        desc = re.findall('描述：.*建议：', dataInfoStr, re.DOTALL)[0].strip()
        desc = self.delHtmlScript(desc) + '受影响系统如下：' + affect_system
        cveCode = re.findall('CVE\(CAN\) ID: <a.*?>(CVE-\d+-\d+)</a>', dataInfoStr, re.DOTALL)[0].strip()

        item = {}
        item['cveDesc'] = desc
        # item['cveCode'] = title.split('（')[1].strip('）').strip()
        item['cveCode'] = cveCode
        item['cveItemTitle'] = title
        item['pubTime'] = releaseTime
        item['cveSource'] = dataSource
        item['cveItemUrl'] = sourceBulletinUrl
        item['cveUpdateTime'] = updateTime
        # item['affectedProduct'] = affect_system
        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def delHtmlScript(self, orgStr):
        pattern = re.compile(r'<[^>]+>', re.S)
        result = pattern.sub('', orgStr)
        return result


# 运行命令：scrapy crawl nsfocus -a taskType=spider -a taskId=1
# 调试或者部分抓取：scrapy crawl nsfocus -a taskType=update -a taskId=1 -a spiderType=test -a sourceUrls=[\"http://www.nsfocus.net/vulndb/50158\"]


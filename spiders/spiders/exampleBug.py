# # -*- coding: utf-8 -*-
# import logging
# import pdb
# import re
# import json
#
# from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
# from spiders.common.http_post import send_http
# from spiders.spiders.base import BaseSpider
#
#
# class ChromereleasesSpider(BaseSpider):
#     name = 'chromereleases'
#     allowed_domains = ['googleblog.com']
#     start_urls = ['https://chromereleases.googleblog.com/']
#     # start_urls = ['https://www.ibm.com/blogs/psirt/page/10/']
#     parsePage = 'getList'
#
#     custom_settings = {
#         'CONCURRENT_REQUESTS': 1,
#         'DOWNLOAD_DELAY': 2,
#     }
#
#     def getList(self, response):
#         logging.info('start getList')
#         metaInfo = response.meta.get('metaInfo')
#         itemInfoList = []
#         self.pageCount += 1  # 统计页数
#
#         cveItemInfoList = response.xpath("")
#         for i, cveItemSel in enumerate(cveItemInfoList):
#             detailUrl = cveItemSel.xpath("").extract()[0]
#             pubTime = cveItemSel.xpath("").extract()[0]
#             if self.pageCount == 1 and i == 0:  # 记录当天最新数据
#                 self.today_latest_item_data = {
#                     'url': detailUrl,
#                     'pubTime': pubTime
#                 }
#                 logging.info('lastest data is %s' % json.dumps(self.today_latest_item_data))
#
#             if detailUrl == self.latestDataInfo.get('url') and pubTime == self.latestDataInfo.get(
#                     'pubTime'):  # 根据时间和url进行判断是否为新数据
#                 logging.info('find history data, stop spider')
#                 break
#
#             urlInfo = {
#                 'itemType': TYPE_URL,
#                 'parsePage': 'getCveItemInfo',
#                 'metaInfo': metaInfo,
#                 'item': detailUrl,
#             }
#             itemInfoList.append(urlInfo)
#         else:
#             # next page
#             nextPageUrl = response.xpath('').extract()[0]
#             urlInfo = {
#                 'itemType': TYPE_URL,
#                 'parsePage': 'getList',
#                 'metaInfo': metaInfo,
#                 'item': nextPageUrl,
#             }
#             if self.pageCount < self.maxPageCount:  # 防止出错停止不了
#                 itemInfoList.append(urlInfo)
#             else:
#                 logging.info('stop spider mandatory, spider page count is %d' % self.maxPageCount)
#         return itemInfoList
#
#     def getCveItemInfo(self, response):
#         logging.info('start getCveItemInfo')
#         metaInfo = response.meta.get('metaInfo')
#         itemInfoList = []
#
#         # item = {}
#         #
#         # item['cveDesc'] = description
#         # item['cveCode'] = cveCode
#         # item['cveScore'] = score
#         # item['cveItemTitle'] = metaInfo['title']
#         # item['cveItemDetailUrl'] = metaInfo['detailUrl']
#         # item['pubTime'] = self.parseTime(metaInfo['releaseTime'])
#         # item['cveSource'] = metaInfo['dataSource']
#         # item['cveItemUrl'] = metaInfo['sourceBulletinUrl']
#         #
#         # urlInfo = {
#         #     'itemType': TYPE_ITEM,
#         #     'item': item,
#         # }
#         # itemInfoList.append(urlInfo)
#
#         return itemInfoList
#
#     def parseTime(self, timeStr):
#         timeStrList = timeStr.split(' ')[0:3]
#         monthDict = {
#             'Jan': '1',
#             'Feb': '2',
#             'Mar': '3',
#             'Apr': '4',
#             'May': '5',
#             'Jun': '6',
#             'Jul': '7',
#             'Aug': '8',
#             'Sep': '9',
#             'Oct': '10',
#             'Nov': '11',
#             'Dec': '12',
#         }
#         timeStr = '%s-%s-%s' % (timeStrList[2].strip(','), monthDict[timeStrList[0]], timeStrList[1].strip(','))
#         return timeStr
#
#
# # 运行命令：scrapy crawl chromereleases -a taskType='spider' -a taskId=1 -o data.csv
# # 部分抓取：scrapy crawl chromereleases -a taskType='update' -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'
# # 调试：scrapy crawl chromereleases -a taskType='update' -a spiderType='test'  -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'
#
# '''
#
# https://chromereleases.googleblog.com/2020/10/stable-channel-update-for-desktop.html
#
#
# https://chromereleases.googleblog.com/2020/09/stable-channel-update-for-desktop_21.html
#
# '''
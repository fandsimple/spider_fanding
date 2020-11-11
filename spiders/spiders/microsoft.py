# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json
import scrapy
import datetime
import os
import xlrd
import xlsxwriter

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM, TYPE_REQUEST
from spiders.common.http_post import send_http
from spiders.settings import BASE_DIR
from spiders.spiders.base import BaseSpider


class MicrosoftSpider(BaseSpider):
    name = 'microsoft'
    allowed_domains = ['microsoft.com']
    start_urls = ['https://portal.msrc.microsoft.com/zh-cn/security-guidance']
    # start_urls = ['https://portal.msrc.microsoft.com/api/security-guidance/zh-cn']
    parsePage = 'getList'

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getList(self, response):
        logging.info('start getList')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        # 发起列表页请求
        # data = '{"familyIds":[],"productIds":[],"severityIds":[],"impactIds":[100000005,100000002,100000001,100000007,100000003,100000006,100000009,100000008,100000000,100000004,0],"pageNumber":1,"pageSize":20,"includeCveNumber":true,"includeSeverity":true,"includeImpact":true,"orderBy":"publishedDate","orderByMonthly":"releaseDate","isDescending":true,"isDescendingMonthly":true,"queryText":"","isSearch":false,"filterText":"","fromPublishedDate":"%s","toPublishedDate":"%s"}' % (self.get_date(today='preday'), self.get_date(today='today'))
        data = '{"familyIds":[],"productIds":[],"severityIds":[],"impactIds":[100000005,100000002,100000001,100000007,100000003,100000006,100000009,100000008,100000000,100000004,0],"pageNumber":1,"pageSize":20,"includeCveNumber":true,"includeSeverity":true,"includeImpact":true,"orderBy":"publishedDate","orderByMonthly":"releaseDate","isDescending":true,"isDescendingMonthly":true,"queryText":"","isSearch":false,"filterText":"","fromPublishedDate":"%s","toPublishedDate":"%s"}' % (
        '9/17/2020/', self.get_date(today='today'))
        # data = '{"familyIds":[],"productIds":[],"severityIds":[],"impactIds":[100000005,100000002,100000001,100000007,100000003,100000006,100000009,100000008,100000000,100000004,0],"pageNumber":1,"pageSize":20,"includeCveNumber":true,"includeSeverity":true,"includeImpact":true,"orderBy":"impact","orderByMonthly":"releaseDate","isDescending":true,"isDescendingMonthly":true,"queryText":"","isSearch":false,"filterText":"","fromPublishedDate":"10/15/2020","toPublishedDate":"10/15/2020"}'

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://portal.msrc.microsoft.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://portal.msrc.microsoft.com/zh-cn/security-guidance',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        request = scrapy.http.Request('https://portal.msrc.microsoft.com/api/security-guidance/zh-cn/excel',
                                      method='POST',
                                      body=data,
                                      headers=headers)
        urlInfo = {
            'itemType': TYPE_REQUEST,
            'parsePage': 'parseExcel',
            'metaInfo': {},
            'item': request,
            'dont_filter': True,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseExcel(self, response):
        logging.info('parseExcel')
        itemInfoList = []
        path = os.path.join(BASE_DIR, 'src/microsoft/microsoft_%s_%s.xls' % (
        self.get_date(today='preday', sig='-'), self.get_date(today='today', sig='-')))
        with open(path, 'wb') as fp:
            fp.write(response.body)
        # 处理excel表格
        resultData = self.deal_excel()
        if not resultData:
            logging.info('no data')

        # url = 'https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/%s'
        url = 'https://portal.msrc.microsoft.com/api/security-guidance/zh-CN/CVE/%s'

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2020-17022',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        for cveId, data in resultData.items():
            detailUrl = url % cveId
            request = scrapy.Request(url=detailUrl, headers=headers)
            urlInfo = {
                'itemType': TYPE_REQUEST,
                'parsePage': 'getCveItemInfo',
                'metaInfo': {},
                'item': request,
                'dont_filter': True,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList


    def parseExcel(self, response):
        logging.info('parseExcel')
        itemInfoList = []
        path = os.path.join(BASE_DIR, 'src/microsoft/microsoft_%s_%s.xls' % (
        self.get_date(today='preday', sig='-'), self.get_date(today='today', sig='-')))
        with open(path, 'wb') as fp:
            fp.write(response.body)
        # 处理excel表格
        resultData = self.deal_excel()
        if not resultData:
            logging.info('no data')

        # url = 'https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/%s'
        url = 'https://portal.msrc.microsoft.com/api/security-guidance/zh-CN/CVE/%s'

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2020-17022',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        for cveId, data in resultData.items():
            detailUrl = url % cveId
            request = scrapy.Request(url=detailUrl, headers=headers)
            urlInfo = {
                'itemType': TYPE_REQUEST,
                'parsePage': 'getCveItemInfo',
                'metaInfo': {},
                'item': request,
                'dont_filter': True,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        data = json.loads(response.text)
        pubTime = data.get('publishedDate', '')
        cveId = data.get('cveNumber', '')
        cveTitle = data.get('cveTitle', '')
        affectedProducts = data.get('affectedProducts', '')
        affetcproductList = []
        for affetcproduct in affectedProducts:
            affetcproductName = affetcproduct.get('name', '')
            affetcproductList.append(affetcproductName)

        affectedProductsStr = ','.join(affetcproductList)
        description = data.get('description', '')
        description = self.del_script(data.get('description', '<script></script>')) + '受影响产品如下：' + affectedProductsStr
        cveItemUrl = 'https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/%s' % cveId
        authorList = data.get('acknowledgments', '')
        authorResList = []
        for author in authorList:
            author = re.sub('<a.*?>', '', author)
            author = re.sub('</a>', '', author)
            authorResList.append(author)
        authorStr = ','.join(authorResList)

        item = {}
        item['cveDesc'] = description
        item['cveCode'] = cveId
        item['author'] = authorStr
        item['cveItemTitle'] = cveTitle
        item['pubTime'] = self.parseTime(pubTime)
        item['cveSource'] = 'MICROSOFT'
        item['cveItemUrl'] = cveItemUrl
        urlInfo = {
            'itemType': TYPE_ITEM,
            'item': item,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def parseTime(self, timeStr):
        timeStr = timeStr.split('T')[0].strip()
        return timeStr

    def get_date(self, today='today', sig='/'):
        todayDate = datetime.datetime.now()
        predataDate = todayDate + datetime.timedelta(days=-1)
        if sig == '/':
            if today == 'today':
                todayStr = '%s/%s/%s' % (todayDate.month, todayDate.day, todayDate.year)
                return todayStr
            elif today == 'preday':
                predayStr = '%s/%s/%s' % (predataDate.month, predataDate.day, predataDate.year)
                return predayStr
        else:
            if today == 'today':
                todayStr = '%s-%s-%s' % (todayDate.month, todayDate.day, todayDate.year)
                return todayStr
            elif today == 'preday':
                predayStr = '%s-%s-%s' % (predataDate.month, predataDate.day, predataDate.year)
                return predayStr

    def deal_excel(self):
        logging.info('start deal_excel')
        sourceFilePath = os.path.join(BASE_DIR, 'src/microsoft/microsoft_%s_%s.xls' % (self.get_date(today='preday', sig='-'), self.get_date(today='today', sig='-')))
        book = xlrd.open_workbook(sourceFilePath)
        sheet = book.sheets()[0]
        resulDict = {}
        rows = sheet.get_rows()
        for row_index, row in enumerate(rows):
            if row[0].value == '日期':
                continue
            affect_product = row[1].value
            # product_series = row[2].value
            # affect = row[7].value
            cveId = row[8].value
            data = {
               'affect_product':affect_product,
               # 'product_series':product_series,
               # 'affect':affect,
               'cveId':cveId,
            }
            if resulDict.get(cveId, ''):
                resulDict[cveId]['affect_product'] = resulDict[cveId]['affect_product'] + ',' + affect_product
                continue
            resulDict[cveId] = data

        return resulDict




# 运行命令：scrapy crawl microsoft -a taskType='spider' -a taskId=1 -o data.csv
# 部分抓取：scrapy crawl chromereleases -a taskType='update' -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'
# 调试：scrapy crawl chromereleases -a taskType='update' -a spiderType='test'  -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'

'''
https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2020-16974

'''

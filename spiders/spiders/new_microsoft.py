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


class NewMicrosoftSpider(BaseSpider):
    name = 'new_microsoft'
    allowed_domains = ['microsoft.com']
    start_urls = ['https://portal.msrc.microsoft.com/zh-cn/security-guidance']
    # start_urls = ['https://portal.msrc.microsoft.com/api/security-guidance/zh-cn']
    parsePage = 'parseExcel'

    contentPath = 'src/microsoft/2020_12_09.xlsx'
    contentTitlePath = 'src/microsoft/2020_12_09_title.xlsx'

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def parseExcel(self, response):
        logging.info('parseExcel')
        itemInfoList = []
        # 处理excel表格
        resultData = self.deal_excel()
        if not resultData:
            logging.info('no data')

        # url = 'https://portal.msrc.microsoft.com/api/security-guidance/zh-CN/CVE/%s'
        url = 'https://api.msrc.microsoft.com/sug/v2.0/zh-CN/vulnerability'
        headers = {
            'authority': 'api.msrc.microsoft.com',
            'access-control-allow-origin': '*',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'authorization': 'undefined',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'origin': 'https://msrc.microsoft.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://msrc.microsoft.com/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        request = scrapy.Request(url=url, headers=headers)
        urlInfo = {
            'itemType': TYPE_REQUEST,
            'parsePage': 'getCveItemInfo',
            'metaInfo': {'resultData': resultData},
            'item': request,
            'dont_filter': True,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        resultData = metaInfo.get('resultData', {})
        itemInfoList = []
        descList = json.loads(response.text).get('value', {})

        itemInfoMap = {}
        for descData in descList:
            cveNumber = descData.get('cveNumber', '')
            description = descData.get('description', '')
            pubTime = descData.get('latestRevisionDate', '').split('T')[0].strip()
            itemInfoMap[cveNumber] = {
                'description': description,
                'pubTime': pubTime
            }
        for cveCode, desc in resultData.items():
            resDesc = ''
            pubTime = ''
            info = itemInfoMap.get(cveCode, {})
            if info:
                desc_tem = info.get('description', '')
                pubTime = info.get('pubTime', '')
                if desc_tem:
                    resDesc = desc_tem + desc.split('请随时关注CNNVD或厂商公告。')[-1]
                else:
                    resDesc = desc
            else:
                pdb.set_trace()
                logging.info('竟然不存在cve')

            item = {}
            item['cveDesc'] = resDesc
            item['cveCode'] = cveCode
            item['cveSource'] = 'MICROSOFT'
            item['pubTime'] = pubTime
            # item['cveItemTitle'] =
            item['cveItemUrl'] = url = 'https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-17007/%s' % cveCode
            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': item,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList

    def deal_excel_content(self):
        logging.info('start deal_excel')
        sourceFilePath = os.path.join(BASE_DIR, self.contentPath)
        book = xlrd.open_workbook(sourceFilePath)
        sheet = book.sheets()[0]
        resulDict = {}
        rows = sheet.get_rows()
        for row_index, row in enumerate(rows):
            if row[0].value == '发布日期':
                continue
            affect_product = row[2].value
            cveId = row[9].value
            exec_os = row[3].value
            mean = row[5].value
            if exec_os:
                affect_product = '%s中的%s' % (exec_os, affect_product)
            data = {
                'affect_product': affect_product,
                'cveId': cveId,
                'mean': mean,
            }
            if resulDict.get(cveId, ''):
                resulDict[cveId]['affect_product'] = resulDict[cveId]['affect_product'] + ',' + affect_product
                continue
            resulDict[cveId] = data
        return resulDict

    def deal_excel_title(self):
        logging.info('start deal_excel')
        sourceFilePath = os.path.join(BASE_DIR, self.contentTitlePath)
        book = xlrd.open_workbook(sourceFilePath)
        sheet = book.sheets()[0]
        resulDict = {}

        rows = sheet.get_rows()
        for row_index, row in enumerate(rows):
            if row[0].value == '发布日期':
                continue
            title = row[2].value
            cveId = row[1].value
            resulDict[cveId] = title
        return resulDict

    def deal_excel(self):
        data_content = self.deal_excel_content()
        data_title = self.deal_excel_title()
        count = 0
        resultData = {}
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

        meanMap = {}
        for key, value in data_content.items():
            title = data_title.get(key, '自定义')
            if title == '自定义':
                count += 1
                pdb.set_trace()
                logging.info('没有找到有标题的')
            desc = '%s,目前尚无此漏洞的相关信息，请随时关注CNNVD或厂商公告。以下产品及版本受到影响:%s。' % (title, value['affect_product'])
            resultData[key] = desc
            meanMap[key] = value.get('mean', '')
        resList = []
        for key, value in resultData.items():
            resList.append([key, value, meanMap.get(key), data_title.get(key, '')])

        workbook = xlsxwriter.Workbook('src/microsoft/res/%s_%s_%s.xlsx' % (year, month, day))
        sheet = workbook.add_worksheet('sheet1')
        # 获取并写入数据段信息
        for row in range(0, len(resList)):
            for col in range(0, 4):
                sheet.write(row, col, resList[row][col])
        workbook.close()
        return resultData


# 运行命令：scrapy crawl new_microsoft -a taskType='spider' -a taskId=1 -o data.csv
# 部分抓取：scrapy crawl new_microsoft -a taskType='update' -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'
# 调试：scrapy crawl new_microsoft -a taskType='update' -a spiderType='test'  -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'

'''
https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2020-16974

'''

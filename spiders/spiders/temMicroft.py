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

def deal_excel_content(self):
    logging.info('start deal_excel')
    sourceFilePath = os.path.join(BASE_DIR, 'src/microsoft/microsoft_10-19-2020_11-11-2020.xlsx')
    book = xlrd.open_workbook(sourceFilePath)
    sheet = book.sheets()[0]
    resulDict = {}
    rows = sheet.get_rows()
    for row_index, row in enumerate(rows):
        if row[0].value == '产品':
            continue
        affect_product = row[0].value
        # product_series = row[2].value
        # affect = row[7].value
        cveId = row[2].value
        data = {
            'affect_product': affect_product,
            # 'product_series':product_series,
            # 'affect':affect,
            'cveId': cveId,
        }
        if resulDict.get(cveId, ''):
            resulDict[cveId]['affect_product'] = resulDict[cveId]['affect_product'] + ',' + affect_product
            continue
        resulDict[cveId] = data

    return resulDict


def deal_excel_title(self):
    logging.info('start deal_excel')
    sourceFilePath = os.path.join(BASE_DIR, 'src/microsoft/title.xlsx')
    book = xlrd.open_workbook(sourceFilePath)
    sheet = book.sheets()[0]
    resulDict = {}

    rows = sheet.get_rows()
    for row_index, row in enumerate(rows):
        if row[0].value == 'CVE 编号':
            continue
        title = row[1].value
        cveId = row[0].value
        resulDict[cveId] = title

    return resulDict


def temdeal(self, response):
    resulDict = self.deal_excel_content()
    titleData = self.deal_excel_title()
    count = 0
    resultData = {}
    vtype = ['配置错误',
             '代码问题',
             '资源管理错误',
             '数字错误',
             '输入验证错误',
             '信息泄露',
             '安全特征问题',
             '竞争条件问题',
             '缓冲区错误',
             '格式化字符串错误',
             '跨站脚本',
             '路径遍历',
             '后置链接',
             '注入',
             '代码注入',
             '命令注入',
             'SQL注入',
             '操作系统命令注入',
             '授权问题',
             '信任管理问题',
             '加密问题',
             '数据伪造问题',
             '跨站请求伪造',
             '权限许可和访问控制问题',
             '访问控制错误',
             '环境问题',
             '参数注入',
             '日志信息泄露',
             '调试信息泄露',
             '其他',
             '处理逻辑错误',
             '默认配置问题',
             ]
    for key, value in resulDict.items():
        title = titleData.get(key, '自定义')
        if title == '自定义':
            count += 1
        desc = '%s,目前尚无此漏洞的相关信息，请随时关注CNNVD或厂商公告。以下产品及版本受到影响:%s' % (title, value['affect_product'])
        resultData[key] = desc
    resList = []
    for key, value in resultData.items():
        resList.append([key, value])

    workbook = xlsxwriter.Workbook('src/microsoft/res_1111.xlsx')
    sheet = workbook.add_worksheet('sheet1')
    # 获取并写入数据段信息
    for row in range(0, len(resList)):
        for col in range(0, 2):
            sheet.write(row, col, resList[row][col])
    workbook.close()

    pdb.set_trace()
#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import random
import time
from urllib import parse

from scrapy.utils.project import get_project_settings

from spiders.common.http_post import send_http
from spiders.confs.userAgents import PROXY

'''
1、统计非正常返回
2、统计重定向
3、统计正常返回
4、统计失败代理
5、统计成功代理
6、统计使用代理总数
7、统计请求总数
'''

class CountMiddleware(object):

    def process_response(self, request, response, spider):
        statusCode = response.status
        proxy = response.meta.get('proxy', '')
        if statusCode >= 200 and statusCode < 300:
            #正常
            spider.successCount += 1
        elif statusCode >= 300 and statusCode < 400:
            # 重定向
            spider.redirectCount += 1
        elif statusCode >= 400 and statusCode < 500:
            # 客户端错误
            spider.clientErrorCount += 1
        elif statusCode >= 500 and statusCode < 600:
            # 服务端错误
            spider.serverErrorCount += 1



        return response











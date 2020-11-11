#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import random
import time
from urllib import parse

from scrapy.utils.project import get_project_settings

from spiders.common.http_post import send_http
from spiders.confs.userAgents import PROXY
import pdb

'''
1、限时更新代理
2、最大成功次数和最大失败次数限制
3、代理不重试配置
'''


class HttpProxyMiddleware(object):
    proxySettingList = PROXY
    usedProxy = []
    settings = get_project_settings()
    lastTime = int(time.time())

    def getProxys(self, country):
        url = ""
        data = {
            "country": country,
        }
        res = send_http(url=url, data=data)
        if res.code != 0:
            proxyList = []
            return proxyList
        data = res.get('data', '{}')
        proxyList = json.loads(data)
        return proxyList

    def process_request(self, request, spider):
        # proxyList = []
        # expirationTime = self.settings.get('expirationTime', 10)
        # spiderType = spider.spiderType
        # url = request.url
        # country = ''
        #
        # currentTime = int(time.time())
        # if currentTime - self.lastTime > expirationTime:
        #     proxyList = []
        # proxy = request.meta.get('proxy', '')
        # for domain, conf in self.proxySettingLib:
        #     if domain in url:
        #         country = conf.get(spiderType, '')
        #         break
        # if not proxyList and country:
        #     proxyList = self.getProxys(country)
        #     self.lastTime = int(time.time())
        # if not proxy and proxyList:
        #     proxy = random.choice(proxyList)
        #     spider.proxySet.add(proxy)
        # request.meta['proxy'] = proxy
        ignore_list = ('nsfocus',)
        if spider.name not in ignore_list:
            request.meta['proxy'] = '127.0.0.1:8118'


    # def process_response(self, request, response, spider):
    #     # 判断代理的健康状态
    #     proxy = response.meta.get('proxy', '')
    #     statuCode = response.status
    #     if proxy:
    #         spider.proxySet.add(proxy) #所有使用的代理
    #     if statuCode >=200 and statuCode <400 and proxy:
    #         spider.successProxySet.add(proxy) #健康代理
    #     return response








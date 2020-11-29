#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import scrapy
import json
import copy
import traceback
import logging
import pdb
import os
import datetime
import execjs
from scrapy.utils.project import get_project_settings

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM, TYPE_PROXY, TYPE_PIC, TYPE_REQUEST, TYPE_MOVIE
from spiders.common.http_post import send_http

from spiders.items import LogItem

settings = get_project_settings()
backend_host = settings.get("BACKEND_HOST", '127.0.0.1:8000')


class Tils(object):

    def get_text_list(self, response, xpath, urljoin=False):
        '''
        :func:将字符窜两端空格去掉,返回一个包含很多字符串的列表（urljoin参数可方便处理一些图片链接）
        :param response: 略
        :param xpath: 略
        :param urljoin: 如果为True，方便图片链接的处理。
        :return: 返回文字内容列表
        '''
        infoList = []
        for option in response.xpath(xpath):
            option = option.extract().strip()
            if option:
                if urljoin == True:
                    option = response.urljoin(option)
                infoList.append(option)
        return infoList

    def get_ip(self):
        '''
        func: 获取局域网IP
        :return: 返回当前机器ip
        '''
        osName = os.popen('uname').readline().strip()
        ip = ''
        if osName == "Darwin":
            # mac os
            ip = os.popen("ifconfig|grep 'inet '|grep -v '127.0'|xargs|awk -F '[ :]' '{print $2}'").readline().strip()
        elif osName == "Linux":
            # linux
            ip = os.popen("ifconfig|grep 'inet '|grep -v '127.0'|xargs|awk -F '[ :]' '{print $3}'").readline().strip()
        else:
            # raise ValueError('The os is not support!!!!!')
            return '127.0.0.1'
        return ip

    def dealExecjs(self, jsPath, callFunctionName, args):
        # 读取js文件
        with open(jsPath, 'r', encoding='utf8') as f:
            js = f.read()
        # 通过compile命令转成一个js对象
        docjs = execjs.compile(js)
        # 调用function
        res = docjs.call(callFunctionName, *args)
        return res

    def del_script(self, content):
        '''
        html代码过滤标签
        '''
        from scrapy.selector import Selector
        resStr = ''.join(Selector(text=content).xpath('.//text()').extract()).strip()
        return resStr


class BaseSpider(scrapy.Spider, Tils):
    taskId = -1
    taskType = 'spider'
    sourceUrls = ''  # json格式字符串，通过参数传入
    env_type = "offline"
    parsePage = 'call_url'
    extra_urls = []
    RETRY_TIMES = 5
    pageCount = 0
    maxPageCount = 20
    # today_latest_item_data = {}
    resInfo = {}

    def __init__(self, taskId, taskType, sourceUrls='', spiderType='', startUrls='', **kwargs):
        super(BaseSpider, self).__init__()
        self.runIp = self.get_ip()
        self.taskType = taskType
        self.taskId = taskId
        self.spiderType = spiderType
        self.sourceUrls = sourceUrls
        self.backend_host = backend_host
        ignore_type_list = ['test', 'update']
        ignore_source_list = ['microsoft', 'oracle', 'new_microsoft', 'z01']
        if self.spiderType not in ignore_type_list and self.name not in ignore_source_list:
            self.latestDataInfo = self.get_latest_data()  # 获取抓取过的最近数据
        else:
            self.latestDataInfo = {}

    # 根据任务类型不同进行调度
    def start_requests(self):
        logging.info("start start_requests")
        metaInfo = {}
        cookiejar = 1
        if self.taskType == 'update':  # 更新任务
            sourceUrlList = json.loads(self.sourceUrls)
            for url in sourceUrlList:
                request = scrapy.Request(url, callback=self.call_url)
                request.meta['metaInfo'] = copy.deepcopy(metaInfo)
                request.meta['parsePage'] = 'getCveItemInfo'
                request.meta['retry_times'] = -10
                request.dont_filter = True
                request.meta['cookiejar'] = cookiejar
                yield request
                cookiejar = cookiejar + 1
        else:  # 全量抓取任务
            for request_url in self.start_urls:
                request = scrapy.Request(request_url, callback=self.call_url)
                request.meta['metaInfo'] = copy.deepcopy(metaInfo)
                request.meta['parsePage'] = self.parsePage
                request.meta['retry_times'] = -10
                request.dont_filter = True
                request.meta['cookiejar'] = cookiejar
                yield request
                cookiejar = cookiejar + 1

    def call_url(self, response):
        try:
            logging.info('start call_url')
            parsePage = response.meta['parsePage']
            itemInfoList = getattr(self, parsePage)(response)
            if not itemInfoList:
                return
            for urlInfo in itemInfoList:
                itemType = urlInfo.get("itemType")
                metaInfo = copy.deepcopy(urlInfo.get("metaInfo"))
                cookies = urlInfo.get("cookies", None)
                cookiejar = ''
                if metaInfo and metaInfo.get('cookiejar', ''):
                    cookiejar = metaInfo.get('cookiejar', '')
                if itemType == TYPE_URL:
                    dont_filter = urlInfo.get("dont_filter", False)
                    request = scrapy.Request(urlInfo['item'], cookies=cookies, dont_filter=dont_filter,
                                             callback=self.call_url)
                    request.meta['metaInfo'] = metaInfo
                    request.meta['parsePage'] = urlInfo.get("parsePage")
                    request.meta['retry_times'] = self.RETRY_TIMES
                    if cookiejar:
                        request.meta['cookiejar'] = cookiejar
                    request.dont_filter = dont_filter
                    if metaInfo and metaInfo.get('priority'):
                        request.priority = metaInfo.get('priority')
                    if metaInfo and metaInfo.get('proxy'):
                        request.meta['proxy'] = metaInfo.get('proxy')
                    yield request
                elif itemType == TYPE_ITEM:  # 处理平常item类型数据
                    item = {}  # 此处的item为scrapy.Item的子类
                    for key, value in urlInfo['item'].items():
                        item[key] = value

                    if self.spiderType != 'test':
                        # 请求后端接口进行存储
                        saveItemUrl = 'http://' + self.backend_host + '/spidertask/savecveitem'
                        res = send_http(saveItemUrl, item)
                        if res.get('code') != 200:
                            logging.error('save item fail,data is %s' % json.dumps(item))
                            raise ValueError('save item fail, data is %s' % json.dumps(item) + res.get('data'))
                        yield item
                    else:
                        yield item
                elif itemType == TYPE_PROXY:  # 处理代理
                    proxy = {}
                    for key, value in urlInfo['item'].items():
                        proxy[key] = value
                    yield proxy
                elif itemType == TYPE_PIC:  # 处理图片的
                    image = {}
                    image['itemType'] = TYPE_PIC
                    image['image_urls'] = urlInfo['item']
                    yield image
                elif itemType == TYPE_REQUEST:  # 处理request对象，可处理一些post请求
                    request = urlInfo['item']
                    request.callback = self.call_url
                    request.meta['metaInfo'] = metaInfo
                    request.meta['parsePage'] = urlInfo.get("parsePage")
                    request.meta['retry_times'] = self.RETRY_TIMES
                    if cookiejar:
                        request.meta['cookiejar'] = cookiejar
                    yield request
                elif itemType == TYPE_MOVIE:  # 处理视屏，待扩展
                    pass
        except Exception as e:  # 调试错误的时候可以在此次打断点
            # logItem = LogItem()  # 替换为logItem
            logItem = {}  # 替换为logItem
            msgStr = json.dumps(traceback.format_exc())
            logging.warning(msgStr)
            pdb.set_trace()
            logItem['logDetail'] = msgStr
            logItem['taskId'] = self.taskId
            logItem['level'] = 'fatal'
            logItem['url'] = response.url
            logItem['spiderName'] = self.name
            logItem['ip'] = self.runIp

            if self.is_set_log():
                url = 'http://' + self.backend_host + '/spidertask/seterrorlog'
                res = send_http(url=url, data=logItem)
                if res.get('code') != 200:
                    logging.error(
                        'getlatestinfo fail, post data is %s, res data is %s' % (json.dumps(logItem), json.dumps(res)))
                    raise ValueError(
                        'getlatestinfo fail, post data is %s, res data is %s' % (json.dumps(logItem), json.dumps(res)))
            logging.error(json.dumps(logItem))
            yield logItem
        finally:
            # 预留
            pass

    def parse(self, response):
        raise ValueError('please rewrite parse or replace callback function')

    def getCveItemInfo(self, response):
        raise ValueError('must rewrite getCveItemInfo')

    def write(self, text):
        logging.info('start write_to_file')
        filePath = os.path.join(settings.get("BASE_DIR"), 'test')
        fileName = self.name + '.html'
        fullPath = os.path.join(filePath, fileName)
        with open(fullPath, 'w') as fp:
            fp.write(text)

    def get_latest_data(self):
        logging.info("start get_latest_data")
        # 获取最新数据信息
        data = {
            'sourceName': self.name
        }
        url = 'http://' + self.backend_host + '/spidertask/getlatestinfo'
        res = send_http(url=url, data=data)
        if res.get('code') != 200:
            logging.error('getlatestinfo fail, post data is %s, res data is %s' % (json.dumps(data), json.dumps(res)))
            raise ValueError(
                'getlatestinfo fail, post data is %s, res data is %s' % (json.dumps(data), json.dumps(res)))
        latestDataInfo = json.loads(res.get('data').get('latestDataInfo'))
        return latestDataInfo

    def set_latest_data(self):
        logging.info("start set_latest_data")
        data = {
            'sourceName': self.name,
            'latestDataInfo': json.dumps(self.today_latest_item_data)
        }
        url = 'http://' + self.backend_host + '/spidertask/setlatestinfo'
        res = send_http(url=url, data=data)
        if res.get('code') != 200:
            logging.error('set_latest_data fail, post data is %s, res data is %s' % (json.dumps(data), json.dumps(res)))
            raise ValueError(
                'getlatestinfo fail, post data is %s, res data is %s' % (json.dumps(data), json.dumps(res)))
        logging.info('set_latest_data success, data is %s, date is %s' % (
        json.dumps(data), datetime.date.today().strftime('%Y-%m-%d')))

    def close(self):
        logging.info('start close')
        ignore_list = ['microsoft', 'oracle', 'new_microsoft', 'z01']
        ignore_type_list = ['test', 'update']
        if self.taskType not in ignore_type_list and self.name not in ignore_list:
            self.set_latest_data()  # 设置最新数据
        # 抓取页数统计
        # logging.info('spider page count is %d' % self.pageCount)
        self.resInfo['spider_page'] = self.pageCount
        logging.info(json.dumps(self.resInfo))

    def is_set_log(self):
        if self.spiderType == 'test' or self.taskType == 'update':
            return False
        return True

#!/usr/bin/python
# -*- coding: utf-8 -*-

import pdb
from spiders.spiders.seleniumBase import SeleniumBase
import time
import logging


class ExampleSpider(SeleniumBase):
    name = 'selenium_test'
    allowed_domains = ['baidu.com']
    start_urls = ['https://www.baidu.com']

    def start_run(self):
        logging.info('start_run')
        # self.login()
        # self.click('//*[@id="app"]/div/div[2]/div[1]/div/ul/li[2]')
        # time.sleep(5)
        self.open('https://www.baidu.com')
        time.sleep(5)

# 运行命令：scrapy crawl selenium_test -a taskType='spider' -a taskId=1


#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import logging
import time
import json
import traceback
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from spiders.common.constantFields import PHANTOM_JS, GOOGLE_CHROME, LARGE_TIMEOUT
from spiders.common import page_actions


class SeleniumBase(scrapy.Spider):
    name = "selenium_base"
    allowed_domains = ["baidu.com"]
    start_urls = [
        "https://www.baidu.com",
    ]

    browser_name = GOOGLE_CHROME
    # browser_name = PHANTOM_JS
    user = 'admin'
    password = 'Wasp@202O'

    def parse(self, response):
        logging.info('parse')
        try:
            self.webdriver_init()
            self.start_run()
        except Exception as e:
            msgStr = json.dumps(traceback.format_exc())
            logging.error(msgStr)

    def start_run(self):
        return

    def init_phantomjs_driver(self, *args, **kwargs):
        # headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #     'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        #     'Connection': 'keep-alive'
        # }

        # for key, value in headers.iteritems():
        #     webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

        # webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        webdriver.DesiredCapabilities.PHANTOMJS[
            'phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'

        driver = webdriver.PhantomJS(*args, **kwargs)
        return driver

    def get_proxy(self):
        return None

    def webdriver_init(self):
        logging.info("webdriver_init of [%s]", self.browser_name)
        self.seleniumProxy = self.get_proxy()
        logging.info("self.seleniumProxy is [%s]", self.seleniumProxy)
        if self.browser_name == PHANTOM_JS:
            service_args = [
                '--ignore-ssl-errors=true',
                '--ssl-protocol=any',
            ]
            if self.seleniumProxy:
                service_args.append('--proxy=' + self.seleniumProxy)
                service_args.append('--proxy-type=http')
            self.driver = self.init_phantomjs_driver(service_args=service_args)
        elif self.browser_name == GOOGLE_CHROME:
            chrome_options = webdriver.ChromeOptions()
            downloads_path = ""
            prefs = {"download.default_directory": downloads_path}
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--allow-file-access-from-files")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            # chrome_options.add_argument("--disable-gpu")
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E216"
            )
            if self.seleniumProxy:
                chrome_options.add_argument('--proxy-server=http://%s' % self.seleniumProxy)
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            logging.warning("un support browser of [%s]", self.browser_name)
            raise ValueError("un support browser of [%s]", self.browser_name)
        self.driver.set_window_size(1400, 1000)
        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(60)

    def open(self, url):
        self.driver.get(url)

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR,
                                 timeout=LARGE_TIMEOUT):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.wait_for_element_visible(
            self.driver, selector, by, timeout)

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR,
                                 timeout=LARGE_TIMEOUT):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.wait_for_element_visible(
            self.driver, selector, by, timeout)

    def wait_for_element_not_visible(self, selector, by=By.CSS_SELECTOR,
                                     timeout=LARGE_TIMEOUT):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.wait_for_element_not_visible(
            self.driver, selector, by, timeout)

    def wait_for_element_list_visible(self, selectorList, by=By.CSS_SELECTOR,
                                      timeout=LARGE_TIMEOUT):
        return page_actions.wait_for_element_list_visible(
            self.driver, selectorList, by, timeout)

    def update_text_value(self, selector, new_value, by=By.CSS_SELECTOR,
                          timeout=LARGE_TIMEOUT, retry=False):
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        element.clear()
        pre_action_url = self.driver.current_url
        element.send_keys(new_value)

    def activate_jquery(self):
        page_actions.activate_jquery(self.driver)

    def execute_jquery(self, jqStr):
        self.activate_jquery()
        self.execute_script(jqStr)

    def find_visible_elements(self, selector, by=By.CSS_SELECTOR):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.find_visible_elements(self.driver, selector, by)

    def click(self, selector, by=By.CSS_SELECTOR,
              timeout=LARGE_TIMEOUT):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        element = page_actions.wait_for_element_visible(
            self.driver, selector, by, timeout=timeout)
        pre_action_url = self.driver.current_url
        element.click()

    def wait_and_click(self, selector, index=0):
        self.wait_for_element_visible(selector)
        click_script = """jQuery("%s").eq(%s).click();""" % (selector, index)
        self.execute_jquery(click_script)

    def get_text_list(self, response, xpath):
        infoList = []
        for option in response.xpath(xpath):
            option = option.extract().strip()
            if option:
                infoList.append(option)
        return infoList

    def switch_to_frame(self, frame):
        self.driver.switch_to.frame(frame)

    def wait_for_element_absent(self, selector, by=By.CSS_SELECTOR,
                                timeout=LARGE_TIMEOUT):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.wait_for_element_absent(
            self.driver, selector, by, timeout)

    def is_element_present(self, selector, by=By.CSS_SELECTOR):
        if selector.startswith('/') or selector.startswith('./'):
            by = By.XPATH
        return page_actions.is_element_present(self.driver, selector, by)

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def save_screenshot(self, name, folder=None):
        return page_actions.save_screenshot(self.driver, name, folder)

    def save_screen(self, name):
        def write_file(self, name, content, mode='w'):
            # self.prefix = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            html_file = os.path.join(self.prefix, 'log', name)
            html_dir = os.path.dirname(html_file)
            if not os.path.isdir(html_dir):
                os.makedirs(html_dir)
            file_object = open(html_file, mode)
            file_object.write(content)
            file_object.close()

        logging.info("save_screen of [%s]", name)
        if not self.driver:
            logging.info("no selenium driver , skip it")
            return
        picFolder = "log/%s/%s/" % (self.name, self.taskId)
        logFolder = "%s/%s/" % (self.name, self.taskId)
        timestamp = "%.6f" % time.time()
        timestamp = timestamp.split(".")[-1]

        filename = "%s_%s_%s" % (self.logIndex, name, timestamp)

        picName = filename + ".jpg"
        logName = logFolder + filename + ".html"
        page_actions.save_screenshot(self.driver, picName, picFolder)
        write_file(logName, self.driver.page_source)
        picFile = picFolder + picName
        self.logIndex = self.logIndex + 1
        ret = {
            'picFile': picFile,
        }
        return ret

    def close_selenium(self):
        try:
            self.driver.close()
        except Exception as e:
            msgStr = json.dumps(traceback.format_exc())
            # self.commonLib.set_header("taskRet",self.taskRet)
            logging.warning(msgStr)

    def login(self):
        logging.info('login')
        self.open('http://192.168.0.248/login')
        authCode = self.driver.get_cookie(name='authCode').get('value')
        self.update_text_value('//*[@id="app"]/div/div[1]/div[2]/form/div[1]/div/div/input', new_value=self.user)
        self.update_text_value('//*[@id="app"]/div/div[1]/div[2]/form/div[2]/div/div/input', new_value=self.password)
        self.update_text_value('//*[@id="app"]/div/div[1]/div[2]/form/div[3]/div/div/input', new_value=authCode)
        self.click('//*[@id="app"]/div/div[1]/div[2]/form/div[4]/div/button')
        time.sleep(4)

    def close(spider, reason):
        logging.info('close...')
        spider.close_selenium()

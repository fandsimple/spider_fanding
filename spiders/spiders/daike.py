# # -*- coding: utf-8 -*-
# import logging
# import pdb
# from spiders.spiders.base import BaseSpider
# import scrapy
#
# from spiders.common.constantFields import TYPE_REQUEST
#
#
# class ExampleSpider(BaseSpider):
#     name = 'daike'
#     allowed_domains = ['neea.edu.cn', 'baidu.com']
#     # start_urls = ['https://ielts.neea.edu.cn/login']
#     start_urls = ['https://www.baidu.com']
#     parsePage = 'get_login_page'
#
#     headers = {
#         'Connection': 'keep-alive',
#         'Pragma': 'no-cache',
#         'Cache-Control': 'no-cache',
#         'Upgrade-Insecure-Requests': '1',
#         'Origin': 'https://ielts.neea.edu.cn',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-User': '?1',
#         'Sec-Fetch-Dest': 'document',
#         'Referer': 'https://ielts.neea.edu.cn/login',
#         'Accept-Language': 'zh-CN,zh;q=0.9',
#     }
#
#     login_data = {
#         'userId': '15735183194',
#         'userPwd': '78a7a61cb6890daeaa8843bbe56cc738',
#         'checkImageCode': 'osgp',
#         'CSRFToken': ''
#     }
#     cookies = {
#         '1laYpfWboXsu443S': 'jeNWa1AXR.FastMeBeVYmzL6KsuyRe_lcugniOOmt0mSorLgzOJbewGHrz0CL9We',
#         'domain_port_https': '443',
#         'domain_port_http': '80',
#         'domain_name_edu': 'ielts.neea.edu.cn',
#         'domain_name_net': 'ielts.neea.cn',
#         'JSESSIONID': 'C7C1F8E175005B0E55317542F6970304',
#         'BIGipServerhw_ielts_internal_pool': '67815434.23040.0000',
#         '1laYpfWboXsu443T': '5FQYuLI4mZv7ix2B_uR14ERzYX6ghThgtfSIk6TU.xg_UKPXuQWXawP5_pCQUtGjeXK09UhO9sHhUsaJIysxD5x3jD_TYhKxUpEnMYGvlZ7JLmPYjvnSMldwMkJuniyn2zgSHN6E42Ev_T1AIN62my406lDJR5y.iWEq6JSZGTvpsLUGudgvwhfGuvfHGvPADYvO_CuEfbDjNupATtz0iqzIKFFdzini2nCdBBxlxDNNEvA6FhY5OP11mfWjOrsqTtSwAf1ZIjjenOKArOJDpdPlhQhTzeire2EjsvIL0HlpKFTJ0PFuvJBWyFoZnd6jm5fUv1suEYRoYknYcXKqNmvrlxoCSKVf3ZEhqNZSnAoCSmxY1iP5gzOYfPIdrLPZxAlL',
#     }
#
#     def get_login_page_one(self, response):
#         logging.info('get_login_page_one')
#         itemInfoList = []
#         url = 'https://ielts.neea.edu.cn/login'
#         request = scrapy.Request(url=url, headers=self.headers, cookies=self.cookies)
#         urlInfo = {
#             'itemType': TYPE_REQUEST,
#             'parsePage': 'get_login_page',
#             'metaInfo': {},
#             'item': request,
#             'dont_filter': True,
#         }
#         itemInfoList.append(urlInfo)
#         return itemInfoList
#
#     def get_login_page(self, response):
#         pdb.set_trace()
#         itemInfoList = []
#
#         csrfToken = response.xpath("//input[@name='CSRFToken']/@value").extract()[0]
#         login_data = self.login_data
#         login_data['CSRFToken'] = csrfToken
#
#         url = ''
#         request = scrapy.FormRequest(
#             url=url,
#             formdata=login_data,
#         )
#         urlInfo = {
#             'itemType': TYPE_REQUEST,
#             'parsePage': 'after_login',
#             'metaInfo': {},
#             'item': request,
#             'dont_filter': True,
#         }
#         itemInfoList.append(urlInfo)
#         return itemInfoList
#
#     def after_login(self, response):
#         pdb.set_trace()
#         pass

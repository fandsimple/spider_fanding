# -*- coding: utf-8 -*-
import logging
import pdb
import re
import json

from spiders.common.constantFields import TYPE_URL, TYPE_ITEM
from spiders.common.http_post import send_http
from spiders.spiders.base import BaseSpider


class OracleSpider(BaseSpider):
    name = 'oracle'
    allowed_domains = ['oracle.com']

    # 如下内容需要每次做抓取的时候进行手动修改
    start_urls = ['https://www.oracle.com/security-alerts/cpuoct2020.html']
    pubTime = '2020-10-21'
    descUrl = 'https://www.oracle.com/security-alerts/cpuoct2020verbose.html#OVIR'

    # start_urls = ['https://www.ibm.com/blogs/psirt/page/10/']
    parsePage = 'getCveItemInfo'


    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def getCveItemInfo(self, response):
        logging.info('start getCveItemInfo')
        metaInfo = response.meta.get('metaInfo')
        itemInfoList = []
        itemDataList = []
        allCveIdSet = set()

        tableSelList = response.xpath('//table')
        dataSelList = []
        for tableSel in tableSelList:
            if len(tableSel.xpath('./thead/tr[1]/th')) == 8:
                dataSelList.append(tableSel)

        for dataSel in dataSelList:  # 有产品的解析方式
            # theadStr = ''.join(dataSel.xpath('./thead/tr//text()').extract())
            # if 'Product' in theadStr:
            #     trSelList = dataSel.xpath('./tbody/tr')
            #     for tr in trSelList:
            #         cveId = tr.xpath('./th/text()').extract()[0].strip()
            #         component = tr.xpath('./td[1]/text()').extract()[0].strip()
            #         required = tr.xpath('./td[2]/text()').extract()[0].strip()
            #         protocol = tr.xpath('./td[3]/text()').extract()[0].strip()
            #
            #         isAuth = tr.xpath('./td[4]/text()').extract()[0].strip()
            #         baseScore = tr.xpath('./td[5]/text()').extract()[0].strip()
            #         vectorAttack = tr.xpath('./td[6]/text()').extract()[0].strip()
            #         vectorComplex = tr.xpath('./td[7]/text()').extract()[0].strip()
            #
            #         private = tr.xpath('./td[8]/text()').extract()[0].strip()
            #         userInteract = tr.xpath('./td[9]/text()').extract()[0].strip()
            #         scopeList = tr.xpath('./td[10]/text()').extract()
            #         scope = ''
            #         for scopeStr in scopeList:
            #             scope += scopeStr.strip()
            #
            #         confid_entiality = tr.xpath('./td[11]/text()').extract()[0].strip()
            #         inte_grity = tr.xpath('./td[12]/text()').extract()[0].strip()
            #         avail_ability = tr.xpath('./td[13]/text()').extract()[0].strip()
            #         version = tr.xpath('./td[14]/text()').extract()[0].strip()
            #
            #         item = {}
            #
            #         item['cveId'] = cveId
            #         item['component'] = component
            #         item['required'] = required
            #         item['protocol'] = protocol
            #         item['isAuth'] = isAuth
            #         item['baseScore'] = baseScore
            #         item['vectorAttack'] = vectorAttack
            #         item['vectorComplex'] = vectorComplex
            #         item['private'] = private
            #         item['userInteract'] = userInteract
            #         item['scope'] = scope
            #         item['confid_entiality'] = confid_entiality
            #         item['inte_grity'] = inte_grity
            #         item['confid_entiality'] = confid_entiality
            #         item['avail_ability'] = avail_ability
            #         item['version'] = version
            #         itemDataList.append(item)
            #
            #         urlInfo = {
            #             'itemType': TYPE_ITEM,
            #             'item': item,
            #         }
            #         # itemInfoList.append(urlInfo)
            #
            # else:  # 只有组件的解析方式
            trSelList = dataSel.xpath('./tbody/tr')
            for tr in trSelList:
                cveId = tr.xpath('./th/text()').extract()[0].strip()
                component = tr.xpath('./td[1]/text()').extract()[0].strip()
                required = tr.xpath('./td[2]/text()').extract()[0].strip()
                protocol = tr.xpath('./td[3]/text()').extract()[0].strip()

                isAuth = tr.xpath('./td[4]/text()').extract()[0].strip()
                baseScore = tr.xpath('./td[5]/text()').extract()[0].strip()
                vectorAttack = tr.xpath('./td[6]/text()').extract()[0].strip()
                vectorComplex = tr.xpath('./td[7]/text()').extract()[0].strip()

                private = tr.xpath('./td[8]/text()').extract()[0].strip()
                userInteract = tr.xpath('./td[9]/text()').extract()[0].strip()
                scopeList = tr.xpath('./td[10]/text()').extract()
                scope = ''
                for scopeStr in scopeList:
                    scope += scopeStr.strip()

                confid_entiality = tr.xpath('./td[11]/text()').extract()[0].strip()
                inte_grity = tr.xpath('./td[12]/text()').extract()[0].strip()
                avail_ability = tr.xpath('./td[13]/text()').extract()[0].strip()
                version = tr.xpath('./td[14]/text()').extract()[0].strip()

                item = {}

                item['cveId'] = cveId
                item['component'] = component
                item['required'] = required
                item['protocol'] = protocol
                item['isAuth'] = isAuth
                item['baseScore'] = baseScore
                item['vectorAttack'] = vectorAttack
                item['vectorComplex'] = vectorComplex
                item['private'] = private
                item['userInteract'] = userInteract
                item['scope'] = scope
                item['confid_entiality'] = confid_entiality
                item['inte_grity'] = inte_grity
                item['confid_entiality'] = confid_entiality
                item['avail_ability'] = avail_ability
                item['version'] = version
                itemDataList.append(item)
                allCveIdSet.add(cveId)
                # urlInfo = {
                #     'itemType': TYPE_ITEM,
                #     'item': item,
                # }
                # itemInfoList.append(urlInfo)

        urlInfo = {
            'itemType': TYPE_URL,
            'parsePage': 'getDec',
            'metaInfo': {'dataList':itemDataList, 'allCveIdSet': allCveIdSet, 'url': response.url},
            # 'item': 'https://www.oracle.com/security-alerts/cpuoct2020verbose.html#OVIR',
            'item': self.descUrl,
        }
        itemInfoList.append(urlInfo)
        return itemInfoList

    def getDec(self, response):
        logging.info('start getDec')
        metaInfo = response.meta.get('metaInfo')
        cveInfoList = metaInfo.get('dataList')
        allCveIdSet = metaInfo.get('allCveIdSet')
        itemInfoList = []
        resultList = []
        tableSelList = response.xpath('//table')
        for tableSel in tableSelList:
            trSelList = tableSel.xpath('./tbody/tr')
            for trSel in trSelList:
                dataDict = {}
                dataDict['cveId'] = trSel.xpath('./td[1]/a/text()').extract()[0]
                dataDict['des'] = ''.join(trSel.xpath('./td[2]//text()').extract())
                resultList.append(dataDict)

        for cveId in allCveIdSet:
            descStr = ''
            p_c_v_str = ''
            cveScore = ''
            for data in resultList:
                if cveId.strip() == data.get('cveId', '').strip():
                    descStr += data.get('des', '')
            for cveInfo in cveInfoList:
                if cveId.strip() == cveInfo.get('cveId'):
                   p_c_v_str += '(' + cveInfo.get('component') + '--' + cveInfo.get('required') + '--' + cveInfo.get('version') + '),'
                   cveScore += cveInfo.get('baseScore', '') + ','
            # item[cveId] = descStr.strip() + '受影响产品、组件及版本信息如下：' + p_c_v_str
            desc = descStr.strip() + '受影响产品、组件及版本信息如下：' + p_c_v_str

            item = {}
            item['cveDesc'] = desc
            item['cveItemUrl'] = metaInfo.get('url', '')
            item['cveSource'] = 'ORACLE'
            item['affectedProduct'] = p_c_v_str.strip(',')
            item['pubTime'] = self.pubTime
            item['cveScore'] = str(cveScore.strip(','))
            item['cveCode'] = cveId
            urlInfo = {
                'itemType': TYPE_ITEM,
                'item': item,
            }
            itemInfoList.append(urlInfo)
        return itemInfoList


# 运行命令：scrapy crawl oracle -a taskType=spider -a taskId=1 -o data.csv
# 部分抓取：scrapy crawl oracle -a taskType=update -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'
# 调试：scrapy crawl oracle -a taskType=update -a spiderType=test  -a taskId=1 -a sourceUrls='["https://www.ibm.com/blogs/psirt/security-bulletin-cross-site-scripting-vulnerability-affect-ibm-business-automation-workflow-and-ibm-business-process-manager-bpm-cve-2020-4698-2/"]'


'''
CVE-2020-9488	
'''


'''
(Oracle Communications Diameter Signaling Router (DSR)--IDIH (Apache Ant)--IDIH: 8.0.0-8.2.2),
(Oracle Business Process Management Suite--Runtime Engine (Apache Ant)--12.2.1.3.0, 12.2.1.4.0)
,(Oracle Retail Back Office--Security (Apache Ant)--14.0, 14.1),
(Oracle Retail Central Office--Security (Apache Ant)--14.0, 14.1),
(Oracle Retail Integration Bus--RIB Kernal (Apache Ant)--14.1, 15.0, 16.0),
(Oracle Retail Point-of-Service--Security (Apache Ant)--14.0, 14.1),
(Oracle Retail Returns Management--Security (Apache Ant)--14.0, 14.1),
(Oracle Utilities Framework--General (Apache Ant)--2.2.0.0.0, 4.2.0.2.0, 4.2.0.3.0, 4.3.0.1.0 - 4.3.0.6.0, 4.4.0.0.0, 4.4.0.2.0)

'''



#!/usr/bin/python
# -*- coding: utf-8 -*-

import pdb
import random

from spiders.common.constantFields import UA_ALL, UA_WEB, UA_PHONE

from spiders.confs.userAgents import WebUAList, MobileUAList


class randomUserAgentDownloaderMiddleware(object):

    def process_request(self, request, spider):
        metaInfo = request.meta
        is_random_ua = metaInfo.get('is_random_ua', False)
        ua_type = metaInfo.get('ua_type', UA_ALL)
        if spider.settings.get('RANDOM_UA_ENABLE', False):
            if is_random_ua:
                if ua_type.lower() == UA_ALL:
                    request.headers['User-Agent'] = random.choice(WebUAList + MobileUAList)
                elif ua_type.lower() == UA_WEB:
                    request.headers['User-Agent'] = random.choice(WebUAList)
                elif ua_type.lower() == UA_PHONE:
                    request.headers['User-Agent'] = random.choice(MobileUAList)
        return None

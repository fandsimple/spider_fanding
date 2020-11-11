#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Time    : 2020/9/16 1:43 PM
# @Author  : fanding
# @FileName: __init__.py.py
# @Software: PyCharm


import redis
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

host = settings.get('REDIS_HOST', '127.0.0.1')
port = settings.get('REDIS_PORT', 6379)
password = settings.get('REDIS_PASSWD', '')

pool = redis.ConnectionPool(host=host, port=port,  decode_responses=True)
redtils = redis.Redis(connection_pool=pool)

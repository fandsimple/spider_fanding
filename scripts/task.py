#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Time    : 2020/9/16 2:19 PM
# @Author  : fanding
# @FileName: task.py
# @Software: PyCharm


"""
一直开启着，提取符合条件的任务，然后执行任务。
功能：
    1、提取符合条件任务
    2、执行任务
    3、执行完毕后更新任务状态
"""
import logging
import os
import pdb
import subprocess
import time
import json
import requests
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fileName = os.path.join(BASE_DIR, 'logs/task/task.log')
logging.basicConfig(filename=fileName,level=logging.DEBUG)


host = '127.0.0.1'
port = '8000'



def get_ip():
    # linux
    # ip = os.popen("ifconfig|grep 'inet '|grep -v '127.0'|xargs|awk -F '[ :]' '{print $3}'").readline().strip()
    # mac os
    ip = os.popen("ifconfig|grep 'inet '|grep -v '127.0'|xargs|awk -F '[ :]' '{print $2}'").readline().strip()
    return ip


def http_post(url, data):
    ret = {}
    try:
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        }
        ret = requests.post(url=url, data=data, headers=headers)
        ret = json.loads(ret.text)
    except Exception as e:
        logging.error(traceback.format_exc())
    return ret


env_dist = os.environ # 获取节点名称（不同节点可以执行不同任务）
node_name = env_dist.get('NODE_NAME', 'default')
# node_name = 'spider'
flag = True
while flag:
    try:
        time.sleep(3)
        # 从redis队列中取出一个对应节点任务并进行执行。
        data = {
            'nodeName': node_name
        }
        url = 'http://%s:%s/spidertask/getredistask/' % (host, port)
        res = http_post(url=url, data=data)  # 请求将要执行的task

        if res.get('code') != 200:
            raise ValueError('获取任务失败')
        if not res.get('msg'):  # 当前没有任务可跑
            logging.info('no task')
            time.sleep(3)
            continue
        redisTaskData = res.get('msg')

        # 同步任务状态，将数据库中对应任务状态改为running
        data = {
            'taskId': redisTaskData.get('taskId'),
            'status': 'running',
            'ip': get_ip()
        }
        url = 'http://%s:%s/spidertask/updatetaskstatus/' % (host, port)
        res = http_post(url=url, data=data)  # 请求将要执行的task
        if res.get('code') != 200:
            raise ValueError("id为%d的%s在从状态ready修改为running状态时出错" % (redisTaskData.get('taskId'), redisTaskData.get('taskName')))

        # 构建cmd命令
        spiderName = redisTaskData.get('taskName', '')
        taskId = redisTaskData.get('taskId', '')
        taskType = redisTaskData.get('taskType', '')
        startUrls = redisTaskData.get('startUrls', '')
        sourceUrls = redisTaskData.get('sourceUrls', '')
        if taskType == 'spider':
            if startUrls != '空':
                cmd = 'scrapy crawl %s -a taskId=%s -a taskType="%s" -a startUrls="%s" -a sourceUrls="%s"' % (spiderName, taskId, taskType, startUrls, '')
            else:
                cmd = 'scrapy crawl %s -a taskId=%s -a taskType="%s" -a startUrls="%s" -a sourceUrls="%s"' % (spiderName, taskId, taskType, '', '')
        elif taskType == 'spider_update':
            if sourceUrls == '空':
                raise ValueError('sourceUrls should not be null')
            cmd = 'scrapy crawl %s -a taskId=%s -a taskType="%s" -a startUrls="%s" -a sourceUrls="%s"' % (spiderName, taskId, taskType, '', sourceUrls)
        else:
            raise ValueError('taskType is error')
        logging.info('cmd:%s' % cmd)
        # 执行任务，任务执行失败返回非0值
        (cmdStatus, output) = subprocess.getstatusoutput(cmd)
        if cmdStatus:
            raise ValueError("爬虫执行失败，具体信息为:%s" % output)


        # 任务执行完毕，更新任务状态running-->done
        data = {
            'taskId': redisTaskData.get('taskId'),
            'status': 'done'
        }
        url = 'http://%s:%s/spidertask/updatetaskstatus/' % (host, port)
        res = http_post(url=url, data=data)  # 请求将要执行的task
        if res.get('code') != 200:
            raise ValueError(
                "id为%d的%s在从状态running修改为done状态时出错" % (redisTaskData.get('taskId'), redisTaskData.get('taskName')))
    except Exception as e:
        logging.error(traceback.format_exc())
        # 任务执行完毕，更新任务状态为fail
        data = {
            'taskId': redisTaskData.get('taskId'),
            'status': 'fail'
        }
        url = 'http://%s:%s/spidertask/updatetaskstatus/' % (host, port)
        res = http_post(url=url, data=data)  # 请求将要执行的task
    finally:
        logging.info(time.strftime('time is %Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '*'*20 + '\n'*3)


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


host = ''
port = ''



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


flag = True
while flag:
    try:
        time.sleep(3)

        # 从redis队列中取出一个任务进行执行。
        # todo

        # 同步任务状态，将ready状态任务改为running状态
        # todo

        # 提取符合条件的任务（new、running、done、delete）
        data = {
            'ip': get_ip() #获取本机局域网IP
        }

        url = 'http://%s:%s/spidertask/gettask/' % (host, port)
        res = http_post(url=url, data=data) # 请求将要执行的task
        # 请求携带数据
        # {
        #     'code':200,
        #     'msg':'success',
        #     'data':{
        #         'ip': '127.0.0.1'
        #     }
        # }

        # 响应数据
        # {
        #     code: 200,
        #     data: {
        #         createTime: "2019-08-09 23:39:33",
        #         extra: null,
        #         finishTime: "2019-08-09 23:41:42",
        #         parentTaskId: "0",
        #         priority: 1,
        #         startTime: "2019-08-09 23:41:42",
        #         taskIP: "0.0.0.0",
        #         taskId: 4,
        #         taskName: "gap",
        #         taskRet: null,
        #         taskStatus: "running",
        #         taskType: "spider"
        #     },
        #     msg: "success"
        # }
        if res.get('code') != 200:
            raise ValueError('request task fail')
        if not res.get('data'): # 当前没有任务可跑
            logging.info('no task')
            time.sleep(3)
            continue
        # 构建cmd命令
        data = res.get('data')
        spiderName = data.get('taskName', '')
        taskId = data.get('taskId', '')
        taskType = data.get('taskType', '')
        startUrls = data.get('startUrls', '')
        sourceUrls = data.get('sourceUrls', '')
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
        pdb.set_trace()
        # 执行任务，任务执行失败返回非0值
        (cmdStatus, output) = subprocess.getstatusoutput(cmd)
        if cmdStatus:
            raise ValueError('command is error')

        # 任务执行完毕，更新任务状态running-->done
        url = 'http://%s:%s/spidertask/updatetaskdone/' % (host, port)
        data = {
            'taskId': taskId
        }
        res = http_post(url=url, data=data)
        if res.get('code') != 200:
            raise ValueError('update status is error')
    except Exception as e:
        logging.error(traceback.format_exc())
    finally:
        logging.info(time.strftime('time is %Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '*'*20 + '\n'*3)


''' 已完成爬虫，目前手动执行，目的是为了发现问题
scrapy crawl ibm -a taskType=spider -a taskId=1
scrapy crawl nvd_nist -a taskType=spider -a taskId=1
scrapy crawl packetstormsecurity -a taskType=spider -a taskId=1
scrapy crawl auscert -a taskType=spider -a taskId=1

scrapy crawl chromereleases -a taskType=spider -a taskId=1
scrapy crawl cxsecurity -a taskType=spider -a taskId=1
scrapy crawl nsfocus -a taskType=spider -a taskId=1


'''
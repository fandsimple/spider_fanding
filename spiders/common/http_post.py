# #!/usr/bin/python
# # -*- coding: utf-8 -*-
import json
import requests
import traceback


def send_http(url, data={}, headers={"Content-Type": "application/x-www-form-urlencoded"}):
    try:
        if data:  # post请求
            res = requests.post(url=url, data=data, headers=headers)
        else:  # get请求
            res = requests.get(url=url, headers=headers)
        return json.loads(res.text)
    except Exception as e:
        resData = {
            "code": 500,
            "data": json.dumps(traceback.format_exc()),
        }
        return resData

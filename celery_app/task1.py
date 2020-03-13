#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : task1.py
# @Software: PyCharm
from time import sleep
from celery_app import app


@app.task
def send_message(msg):
    sleep(5)  # 模拟耗时操作
    return "message send ok"

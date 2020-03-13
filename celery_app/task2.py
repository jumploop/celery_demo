#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : task2.py
# @Software: PyCharm
from time import sleep
from celery_app import app


@app.task
def send_mail(data):
    sleep(5)  # 模拟耗时操作
    print(data)
    return "mail send ok"

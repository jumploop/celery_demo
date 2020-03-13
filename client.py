#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : client.py
# @Software: PyCharm
from celery_app import task1
from celery_app import task2
# 执行异步任务的方式一:delay
task1.send_message.delay("hello world")
task2.send_mail.delay("hello celery")
# 执行异步任务的方式二:apply_async
task1.send_message.apply_async(args=("hello world",))
task2.send_mail.apply_async(args=("hello python",))

print("欢迎学习celery")

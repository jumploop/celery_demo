#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : celeryconfig.py
# @Software: PyCharm
BROKER_URL = 'redis://127.0.0.1:6379/1'  # 指定 Broker(消息中间件来接收和发送任务消息)
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'  # 指定 Backend(存储worker执行的结果)
# 指定时区,默认是 UTC
CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE='UTC'
# 指定任务的序列化
CELERY_TASK_SERIALIZER = 'json'
# 指定执行结果的序列化
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = (  # 指定导入的任务模块
    'celery_app.task1',
    'celery_app.task2'
)

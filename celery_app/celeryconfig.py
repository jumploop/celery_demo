#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : celeryconfig.py
# @Software: PyCharm
from datetime import timedelta

from celery.schedules import crontab

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
# schedules定时任务
CELERYBEAT_SCHEDULE = {
    'send_message-every-30-seconds': {
        'task': 'celery_app.task1.send_message',
        'schedule': timedelta(seconds=30),  # 每 30 秒执行一次
        'args': ("正在发送短信",)  # 任务函数参数
    },
    'send_mail-at-some-time': {
        'task': 'celery_app.task2.send_mail',
        'schedule': crontab(hour=22, minute=50),  # 每天晚上 22 点 50 分执行一次
        'args': ("正在发送邮件",)  # 任务函数参数
    }
}

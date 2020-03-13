#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:54
# @Author  : jumploop
# @File    : __init__.py
# @Software: PyCharm
from celery import Celery

app = Celery("demo")  # 创建 Celery 实例
app.config_from_object("celery_app.celeryconfig")  # 通过 Celery 实例加载配置模块

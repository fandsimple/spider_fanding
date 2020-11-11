#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Time    : 2020/9/13 5:51 PM
# @Author  : fanding
# @FileName: models.py
# @Software: PyCharm
from spiders.common.dbtils import engine
from spiders.common.dbtils.modelTools import BaseModel, db
from sqlalchemy import Column, String, Integer


class User(BaseModel):
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    username = Column(String(12))
    password_hash = Column(String(128))


class Log(BaseModel):
    __tablename__ = 'log'
    taskId = Column(String(128))
    spiderName = Column(String(128))
    level = Column(String(128))
    ip = Column(String(128))
    url = Column(String(128))
    logDetail = Column(String(128))


class BugInfo(BaseModel):
    __tablename__ = 'bugInfo'
    title = Column(String(128))
    description = Column(String(128))
    sourceBulletinUrl = Column(String(128))
    cveCode = Column(String(128))
    score = Column(String(128))
    detailUrl = Column(String(128))
    releaseTime = Column(String(128))
    dataSource = Column(String(128))


if __name__ == '__main__':
    BaseModel.metadata.create_all(engine)  # 创建表结构

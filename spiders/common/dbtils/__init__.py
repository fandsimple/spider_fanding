#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

# 创建对象的基类:
BaseClass = declarative_base()
# 初始化数据库连接:
engine = create_engine(settings.get('DB_URI'), echo=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Time    : 2020/7/8 5:21 PM
# @Author  : fanding
# @FileName: models.py
# @Software: PyCharm

import traceback
import logging
from spiders.common.dbtils import BaseClass, DBSession
from sqlalchemy import Column, Integer

db = DBSession()


class BaseModel(BaseClass):
    __abstract__ = True
    id = Column(Integer, autoincrement=True, primary_key=True)

    # 添加一条数据
    def save(self):
        try:
            # self 代表当前当前实例化的对象
            db.add(self)
            db.commit()
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
            db.rollback()
            return False

    # 添加多条数据
    @staticmethod
    def save_all(*args):
        try:
            db.add_all(args)
            db.commit()
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
            db.rollback()
            return False

    # 删除
    def delete(self):
        try:
            db.delete(self)
            db.commit()
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
            db.rollback()
            return False




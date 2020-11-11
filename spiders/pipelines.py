# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pdb
import logging
import scrapy
from scrapy.pipelines.files import FilesPipeline
from urlparse import urlparse
from os.path import basename,dirname,join

from spiders.common.dbtils.modelTools import db
from spiders.models import Log, BugInfo


class BugCollectPipeline(object):
    def process_item(self, item, spider):
        if item['itemType'] == 'log':
            logging.info('log item')
            pass
        elif item['itemType'] == 'bugInfo':
            logging.info('bugInfo')
            pass

        return item


class FileDownloadPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        path=urlparse(request.url).path
        return '%s/%s' % (basename(dirname(path)), basename(path))

# -*- coding: utf-8 -*-
import os
import sys


# 项目根目录设置
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加导包路径
sys.path.insert(0, BASE_DIR)



BOT_NAME = 'spiders'

SPIDER_MODULES = ['spiders.spiders']
NEWSPIDER_MODULE = 'spiders.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spiders (+http://www.yourdomain.com)'

# 配置随机userAgent,默认关闭
RANDOM_UA_ENABLE = True

# 是否遵循robots.txt 规则
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# 默认请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
}
# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'spiders.middlewares.SpidersSpiderMiddleware': 543,
#}


# downloadmiddlewares注册的地方，序号越大越后执行
DOWNLOADER_MIDDLEWARES = {
   # 'spiders.middlewares.SpidersDownloaderMiddleware': 543,
   'spiders.downloaderMiddlewares.userAgentMiddleware.randomUserAgentDownloaderMiddleware': 501,
   'spiders.downloaderMiddlewares.httpProxyMiddleware.HttpProxyMiddleware': 502,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'spiders.pipelines.BugCollectPipeline': 300,
   # 'spiders.pipelines.FileDownloadPipeline': 300,
    # 'scrapy.pipelines.files.FilesPipeline':1,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# ****使用时将这些配置全部打开即可****
# ****************日志配置***********************
# 每隔一小时进行日志分割
# fileName = time.strftime('%Y-%m-%d-%H', time.localtime(time.time())) + '-scrapy.log'
# fileName = os.path.join(BASE_DIR, 'logs', fileName)
# LOG_ENABLED = True # 日志引擎开启
# LOG_FILE = fileName # 日志记录位置
# LOG_ENCODING = 'utf-8' # 记录日志时的编码方式
# LOG_LEVEL = 'DEBUG' # 日志级别
# LOG_STDOUT = False # 是否将print等输出到标准输出流中的信息记录到日志文件中去


# *** mysql数据库配置 ***
DB_URI = 'mysql+pymysql://root:102487@localhost:3306/test'


# *** redis数据库配置 ***
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_PASSWD = '102487'



# *** 最新数据记录配置文件位置 ***  弃用
# LAST_ITEM_INFO_CONF_PATH = os.path.join(BASE_DIR, "spiders/confs/last_item_info.txt")


# *** 后端服务器位置 ***
BACKEND_HOST = '127.0.0.1:8000'


# 防止url过长导致scrapy忽略
URLLENGTH_LIMIT = 5000

# 下载文件存储位置
FILE_STORE= os.path.join(BASE_DIR, 'files/microsoft')







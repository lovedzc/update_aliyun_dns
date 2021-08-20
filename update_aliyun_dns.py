####################################
# 自动更新阿里云的域名记录
####################################

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import requests
import re
import time
import logging
from logging.handlers import TimedRotatingFileHandler

log_file_handler = TimedRotatingFileHandler(filename="DDNSUpdate.log", when="D", interval=1, backupCount=3)
log_file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.addHandler(log_file_handler)
log.info("------------------ 启动运行 ------------------")

# 初始化
client = AcsClient('<your-access-key-id>', '<your-access-key-secret>', '<your-region-id>')
request = CommonRequest()
request.set_domain('alidns.aliyuncs.com')
request.set_version('2015-01-09')
domain = "<your-domain>"
prefix = "<your-prefix>"

# 获取公网IP地址
html_text = requests.get("https://www.whatismyip.com/").text
ip_text = re.findall(r'(?<![\.\d])(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])', html_text)
ip = ip_text[0]
log.info("公网IP地址 = "+ ip)
log.info("域名 = "+ prefix + "." + domain)

# 获取二级域名的RecordId
request.set_action_name('DescribeDomainRecords')
request.add_query_param('DomainName', domain)
response = client.do_action_with_exception(request)
jsonObj = json.loads(response.decode("UTF-8"))
records = jsonObj["DomainRecords"]["Record"]
record = None
for rec in records:
    if rec["RR"] == prefix:
        record = rec
        break
if record == None:
    log.info("未找到二级域名记录")
    exit()
elif record['Value'] == ip:
    log.info("现有IP记录已为最新")
    exit()

# 更新IP记录
request.set_action_name('UpdateDomainRecord')
request.add_query_param('RecordId', record['RecordId'])
request.add_query_param('RR', prefix)
request.add_query_param('Type', 'A')
request.add_query_param('Value', ip)
response = client.do_action_with_exception(request)

log.info("DDNS更新完成\n")


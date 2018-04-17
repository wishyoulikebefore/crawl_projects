import json
import os
import xlwt
import time
import requests
from bs4 import BeautifulSoup
import random

"""
考虑到概念的更新
http://q.10jqka.com.cn/gn
以300800安防为例
http://q.10jqka.com.cn/gn/detail/order/desc/page/2/ajax/1/code/300800
"""

isExists = os.path.exists("D:/python_stock/股票概念")
if not isExists:
    print(u"创建名为股票概念的文件夹")
    os.makedirs("D:/python_stock/股票概念")
    os.chdir("D:/python_stock/股票概念")
else:
    os.chdir("D:/python_stock/股票概念")

output = open("concept.txt","a")

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

start_url = "http://q.10jqka.com.cn/gn"

raw_cookies = "v=AoBGvUUuzpZbAbKSWww8W-7GUg9TCWTTBu241_oRTBsudS49ohk0Y1b9iGVJ; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1523759613; historystock=300188; spversion=20130314"
cookies={}
for line in raw_cookies.split(';'):
    key, value = line.split('=', 1)
    cookies[key] = value

def getHtmlPage_GBK(url,saveFile=None):
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        "http":"119.27.189.65:80",
        'Host': 'q.10jqka.com.cn',
        "Connection": "keep - alive",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    html = requests.get(url,headers=headers,cookies=cookies)
    if saveFile:
        if os.path.exists(saveFile+".txt"):
            print("%s has been crawled" %(saveFile))
        else:
            with open(saveFile+".txt","wb") as f:
                print("%s is crawling" % (saveFile))
                f.write(html.content)
    html.encoding = 'gbk'
    soup = BeautifulSoup(html.text, 'lxml')
    return soup

def start_crawl(start_url):
    soup = getHtmlPage_GBK(start_url)
    content = soup.find("div",class_="cate_inner").find_all("a")
    for item in content:
        returnUrl = item["href"]
        conceptIndex = returnUrl.split("/")[-2]
        conceptName = item.get_text()
        soup2 = getHtmlPage_GBK(returnUrl)
        content2 = soup2.find("div",class_="m-pager")
        try:
            pageNum = content2.find_all("a")[-1]["page"]
        except:
            pageNum = 1
        output.write("%s\n" %(conceptName))
        getStock(conceptName,conceptIndex,int(pageNum))
        print("%s has been finished" % (conceptName))

def getStock(conceptName,conceptIndex,pageNum):
    for nu in range(pageNum):
        targetUrl = "http://q.10jqka.com.cn/gn/detail/order/desc/page/%s/ajax/1/code/%s" %(nu+1,conceptIndex)
        saveFile = "%s_%s.txt" %(conceptName,nu)
        soup3 = getHtmlPage_GBK(targetUrl,saveFile)
        content3 = soup3.find("tbody").find_all("tr")
        for item in content3:
            td_list = item.find_all("td")
            stockIndex = td_list[1].get_text()
            stockName = td_list[2].get_text()
            circulation_market_value = td_list[-3].get_text()
            output.write("%s\t%s\t%s\n" %(stockIndex,stockName,circulation_market_value))
        time.sleep(10*random.random())
        if nu %4 == 0:
            time.sleep(20*random.random())

start_crawl(start_url)

"""
尚未解决cookie登陆的问题
IP切换也不行（爬取5个界面后就不行了）
"""




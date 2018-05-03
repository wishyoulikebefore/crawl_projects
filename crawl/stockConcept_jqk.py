import os
import time
import requests
from bs4 import BeautifulSoup
import random
from selenium import webdriver

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

def getHtmlPage_GBK(url):
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        "http":"119.27.189.65:80",
        'Host': 'q.10jqka.com.cn',
        "Connection": "keep - alive",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    html = requests.get(url,headers=headers)
    html.encoding = 'gbk'
    soup = BeautifulSoup(html.text, 'lxml')
    return soup

def start_crawl(start_url):
    soup = getHtmlPage_GBK(start_url)
    content = soup.find("div",class_="cate_inner").find_all("a")
    for item in content:
        conceptUrl = item["href"]
        conceptIndex = conceptUrl.split("/")[-2]
        conceptName = item.get_text()
        output.write("%s\t%s\n" %(conceptName,conceptIndex))
        conceptFile = open(conceptName+".txt","a")
        print("%s crawl start" %(conceptName))
        my_webdriver(conceptUrl,conceptFile,conceptName)
        print("%s crawl end" % (conceptName))

def my_webdriver(conceptUrl,conceptFile,conceptName):
    browser = webdriver.Firefox()
    browser.get(conceptUrl)
    while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
        button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
        presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
        crawl_page(browser,conceptFile,conceptName)
        print("第%s页爬取结束" % (presentPage))
        button.click()
        time.sleep(5)
    crawl_page(browser,conceptFile,conceptName)
    browser.close()
    conceptFile.write("\n\n")
    print("%s is over" %(conceptUrl))

def crawl_page(browser,conceptFile,conceptName):
    locate = browser.find_elements_by_xpath('//div[@id="maincont"]//tbody/tr')
    presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
    record  =open("%s_%s.txt" %(conceptName,presentPage),"a")
    record.write(browser.page_source)
    record.close()
    for item in locate:
        stockName = item.find_elements_by_xpath("td")[2].text
        output.write("%s\n" %(stockName))
        conceptFile.write("%s\n" % (stockName))

start_crawl(start_url)



